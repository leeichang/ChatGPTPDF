import os
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from .models import ChatGPTPDF
from .serializers import ChatGPTPDFSerializer, ChatGPTPDFCreateUpdateSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from rest_framework.authentication import BaseAuthentication
from drf_yasg.utils import swagger_auto_schema
import openai

# from .callback import QuestionGenCallbackHandler, StreamingLLMCallbackHandler
from docx2pdf import convert
import subprocess
from fpdf import FPDF
from PyODConverter import DocumentConverter
import uuid
import platform
import sys

sys.path.append(os.environ["LIBREOFFICE_PROGRAM_PATH"])
sys.path.append(os.environ["SOFFICE_PATH"])
import logging
from .tasks import process_history_embedding
from application import settings
from .CacheManager import CacheManager

logger = logging.getLogger("chatgptpdf")


class ChatGPTPDFViewSet(CustomModelViewSet):
    """
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """

    queryset = ChatGPTPDF.objects.all()
    serializer_class = ChatGPTPDFSerializer
    create_serializer_class = ChatGPTPDFCreateUpdateSerializer
    update_serializer_class = ChatGPTPDFCreateUpdateSerializer

    authentication_classes = []
    permission_classes = []

    ###
    # 處理cors問題
    ###
    @api_view(["OPTIONS"])
    def preflight(self, request):
        return Response(status=status.HTTP_200_OK)

    # def get_authenticators(self):
    #     """
    #     Get the list of authenticators used for this viewset.

    #     Returns:
    #         List[BaseAuthentication]: List of authenticators
    #     """
    #     print("self:",self)
    #     if self.action == 'perform_create':
    #         # Return an empty list of authenticators for perform_create method
    #         return []
    #     else:
    #         # Return the default list of authenticators for other methods
    #         return super().get_authenticators()
    @action(detail=False, methods=["POST"])
    def set_qa_documents(self, request):
        try:
            guid = request.META.get("HTTP_X_GUID")
            fid = request.data["document_ids"]
            if fid != "undefined" and int(fid) > 0:
                ChatGPTPDF.set_qa_documents(fid, guid)
                std_data = {"status": "Success"}
                return Response(std_data)
            else:
                std_data = {"status": "Fail"}
                return Response(std_data)
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["POST"])
    def embedding_history(self, request):
        try:
            guid = request.data.get("guid")

            if guid != "undefined" and guid != None and guid != "":
                history = ChatGPTPDF.get_chat_history(guid)
                process_history_embedding(guid, history.buffer)
                std_data = {"status": "Success"}
                return Response(std_data)
            else:
                std_data = {"status": "Fail"}
                return Response(std_data)
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def get_os_type(self):
        os_type = platform.system().lower()

        if os_type == "darwin":
            return "mac"
        elif os_type == "linux":
            return "linux"
        else:
            return os_type

    def convert_doc2docx(self, input_file, output_directory):
        soffice_path = os.environ["SOFFICE_PATH"]
        cmd = [
            soffice_path,
            "--headless",
            "--convert-to",
            "docx",
            "--outdir",
            output_directory,
            input_file,
        ]
        subprocess.run(cmd, check=True)

    ###
    # 處理txt to pdf file
    ################################
    def txtToPdf(self, oldfilePath, newfilePath):
        font_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "fonts", "msyh.ttf"
        )

        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.add_page()
        # Set the font to use, size, and style
        pdf.add_font("msyh", "", font_path, uni=True)  # 使用支持中文的字體，例如微软雅黑
        pdf.set_font("msyh", size=12)
        # Read the text file and split it into lines
        with open(oldfilePath, "r", encoding="utf-8") as file:
            lines = file.readlines()
        for line in lines:
            line = line.replace("\n", "")
            pdf.multi_cell(0, 10, txt=line, align="L")

        pdf.output(newfilePath)

    def doc2pdf_linux(self, doc, output_directory):
        """
        convert a doc/docx document to pdf format (linux only, requires libreoffice)
        :param doc: path to document
        """
        soffice_path = os.environ["SOFFICE_PATH"]
        cmd = [soffice_path, "--convert-to", "pdf", "--outdir", output_directory, doc]
        p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        p.wait(timeout=10)
        stdout, stderr = p.communicate()
        if stderr:
            raise subprocess.SubprocessError(stderr)

    @action(detail=False, methods=["GET"])
    def get_share(self, request):
        try:
            fid = request.query_params["uuid"]
            if fid != "undefined" and fid != "":
                obj = ChatGPTPDF.get_share(fid)
                filename, file_extension = os.path.splitext(obj.file_name)
                filename = filename[: filename.rfind("_")] + file_extension
                if file_extension.lower() == ".pdf":
                    NoPdf = False
                else:
                    NoPdf = True
                std_data = {
                    "status": "Success",
                    "id": obj.id,
                    "name": filename,
                    "data": obj.Abstract,
                    "NoPdf": NoPdf,
                }
                return Response(std_data)
            else:
                std_data = {"status": "Fail"}
                return Response(std_data)
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["POST"])
    def perform_create(self, serializer):
        try:
            guid = self.request.META.get("HTTP_X_GUID")
            logger.debug("perform_create")
            files = self.request.FILES.getlist("file")
            file_uuid = uuid.uuid4()
            logger.debug(f"file_uuid:{file_uuid}")
            new_obj_id = 0
            for file in files:
                base_name, file_extension = os.path.splitext(file.name)
                file_name = base_name + "_" + str(file_uuid) + file_extension
                file_size = file.size
                file_path = os.path.join(os.environ["FILE_UPLOAD_DIR"], file_name)
                logger.debug(f"file_path:{file_path}")

                with open(file_path, "wb") as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                # if file_extension.lower() == ".doc":
                #     self.convert_doc2docx(file_path, os.environ['FILE_UPLOAD_DIR'])
                #     file_path = file_path + 'x'
                logger.debug(f"file_upload finish")

                if (
                    file_extension.lower() == ".docx"
                    or file_extension.lower() == ".doc"
                ):
                    if self.get_os_type() == "mac":
                        self.doc2pdf_linux(
                            file_path, os.environ["FILE_UPLOAD_DIR"]
                        )  # convert(file_path)
                    elif self.get_os_type() == "linux":
                        self.doc2pdf_linux(file_path, os.environ["FILE_UPLOAD_DIR"])

                    file_name = base_name + "_" + str(file_uuid) + ".pdf"
                    file_path = os.path.join(os.environ["FILE_UPLOAD_DIR"], file_name)
                    logger.debug(f"doc_to_pdf:{file_path}")
                elif file_extension.lower() == ".txt":
                    oldfilePath = file_path
                    file_name = base_name + "_" + str(file_uuid) + ".pdf"
                    file_path = os.path.join(os.environ["FILE_UPLOAD_DIR"], file_name)
                    self.txtToPdf(oldfilePath, file_path)
                    logger.debug(f"txt_to_pdf:{file_path}")

                new_obj = ChatGPTPDF.objects.create(
                    file_name=file_name,
                    file_size=file_size,
                    file_path=file_path,
                    file_uuid=file_uuid,
                    creator_id=1,
                )
                logger.debug(f"save_finish:{new_obj.id}")
                file_name, file_extension = os.path.splitext(file_path)
                if file_extension.lower() == ".pdf" and new_obj_id == 0:
                    new_obj_id = new_obj.id
                logger.debug(f"start index:{file_path}")
                ChatGPTPDF.handleFileIndex(file_path, file_uuid)
                logger.debug(f"end index:{file_path}")
            objs = ChatGPTPDF.objects.filter(file_uuid=file_uuid)
            for obj in objs:
                obj.indexed = True
                obj.save()

            logger.debug(f"start summary:{file_uuid}")
            result = ChatGPTPDF.getDefaultSummaryAndQuestion(
                file_uuid, file_extension.lower(), guid
            )
            logger.debug(f"end summary:{file_uuid}")
            if new_obj_id == 0:
                new_obj_id = new_obj.id
            obj = ChatGPTPDF.objects.get(id=new_obj_id)
            obj.Abstract = result
            obj.save()
            if new_obj_id == 0:
                NoPdf = True
            else:
                NoPdf = False
            std_data = {
                "status": "Success",
                "id": new_obj_id,
                "data": result,
                "NoPDF": NoPdf,
            }
            return Response(std_data, status=status.HTTP_201_CREATED)

        except openai.error.APIConnectionError as e:
            print(f"API連接錯誤: {e}")
        except Exception as e:
            # 處理所有其他未捕獲的異常的代碼
            print(f"An unexpected error occurred: {e}")

    @action(detail=False, methods=["GET"])
    def my_files(self, request):
        files = self.queryset.filter(creator=request.query_params["user"], indexed=True)
        serializer = self.serializer_class(files, many=True)
        std_data = {
            "status": "Success",
            "data": serializer.data,
        }
        return Response(std_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def last_chat_summary(self, request):
        guid = request.query_params["guid"]
        fId = request.query_params["id"]
        path = settings.HISTORY_ROOT
        index_path = f"{path}/{guid}" 
        history = ChatGPTPDF.get_chat_history(guid)
        if os.path.exists(index_path) and len(history.buffer)==0: 
            prompt = "最近一次的對話內容總結是什麼？以繁體中文回答"
            try:
                response_data, inversion = ChatGPTPDF.chatReplyProcess(
                    {
                        "message": prompt,
                        "selectedKeys": fId,
                        "guid": guid,
                    }
                )
            except Exception as e:
                return Response({"message": str(e)}, status=500)

            std_data = {
                "status": "Success",
                "data": f"之前{response_data}\n有沒有需要進一步協助的地方？",
                "inversion": inversion,
            }
        else:
            std_data = {
                "status": "Success",
                "data":"",
            }    
        return Response(std_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    @swagger_auto_schema(operation_id="downloadFile")  # 將 'my_view' 替換為您的 view 函數名稱
    def downloadFile(self, request):
        try:
            guid = request.query_params["guid"]
            fId = request.query_params["id"]
            if fId != "undefined" and int(fId) > 0:
                file = ChatGPTPDF.objects.get(id=request.query_params["id"])
                file_path = file.file_path
                file_name, file_extension = os.path.splitext(file_path)
                if (
                    file_extension.lower() == ".xlsx"
                    or file_extension.lower() == ".xls"
                    or file_extension.lower() == ".csv"
                ):
                    file_path = file_name + ".pdf"

                with open(file_path, "rb") as fh:
                    response = HttpResponse(
                        fh.read(), content_type="application/octet-stream"
                    )
                    response[
                        "Content-Disposition"
                    ] = f'attachment; filename="{file.file_name}"'

                return response
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        except KeyError:
            # 'id' 不存在於 query_params 的錯誤處理
            pass
        except Exception as e:
            # 處理所有其他未捕獲的異常的代碼
            print(f"downloadFile unexpected error occurred: {e}")

    @action(detail=True, methods=["DELETE"])
    def delete(self, request, pk):
        file = ChatGPTPDF.objects.get(pk=pk)
        file_path = file.file_path
        file.delete()
        os.remove(file_path)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def question_handler(response):
        # Define your own question handler callback here
        # This example just returns the response as is
        return response

    def stream_handler(response):
        # Define your own stream handler callback here
        # This example just returns the response as is
        return response

    @action(detail=False, methods=["POST"])
    def chat_process(self, request):
        guid = request.data.get("user_guid")
        prompt = request.data.get("prompt")
        options = request.data.get("options", {})
        system_message = request.data.get("systemMessage")
        selectedKeys = request.data.get("selectedKeys")

        def process(chat):
            nonlocal first_chunk
            if first_chunk:
                response = chat
            else:
                response = "\n" + chat
            response = json.dumps(response)
            response.streaming_content = (response,)
            response["Content-Type"] = "application/octet-stream"
            return response

        first_chunk = True
        try:
            response_data, inversion = ChatGPTPDF.chatReplyProcess(
                {
                    "message": prompt,
                    "process": process,
                    "selectedKeys": selectedKeys,
                    "question_handler": self.question_handler,
                    "stream_handler": self.stream_handler,
                    "guid": guid,
                }
            )
        except Exception as e:
            return Response({"message": str(e)}, status=500)

        std_data = {
            "status": "Success",
            "text": response_data,
            "inversion": inversion,
        }
        return Response(std_data, status=status.HTTP_200_OK)
