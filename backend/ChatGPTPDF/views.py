import os
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status,viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from .models import ChatGPTPDF
from .serializers import ChatGPTPDFSerializer,ChatGPTPDFCreateUpdateSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from rest_framework.authentication import BaseAuthentication
from drf_yasg.utils import swagger_auto_schema
import openai
# from .callback import QuestionGenCallbackHandler, StreamingLLMCallbackHandler

import uuid
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
    #處理cors問題
    ###
    @api_view(['OPTIONS'])
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
    @action(detail=False, methods=['POST'])
    def set_qa_documents(self, request):
        try:
            fid = request.data['document_ids']
            if fid != "undefined" and int(fid) > 0:
                ChatGPTPDF.set_qa_documents(fid)
                std_data={
                    "status":"Success"
                }
                return Response(std_data)
            else:
                std_data={
                    "status":"Fail"
                }
                return Response(std_data)
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)  
    
    @action(detail=False, methods=['POST'])
    def perform_create(self, serializer):
        try:    
            file = self.request.FILES['file']
            file_uuid = uuid.uuid4()
            file_name, file_extension = os.path.splitext(file.name)
            file_name = file_name + '_' +str(file_uuid)+file_extension
            file_size = file.size
            file_path = os.path.join(os.environ['FILE_UPLOAD_DIR'], file_name)
            

            with open(file_path, 'wb') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            new_obj = ChatGPTPDF.objects.create(
                file_name=file_name,
                file_size=file_size,
                file_path=file_path,
                file_uuid =file_uuid,
                creator_id= 1,
            )
            new_obj_id = new_obj.id

            ChatGPTPDF.handleFileIndex(file_path,file_uuid)
            obj = ChatGPTPDF.objects.get(file_uuid=file_uuid)
            obj.indexed = True
            obj.save()

            result = ChatGPTPDF.getDefaultSummaryAndQuestion(file_uuid)
            std_data={
                "status":"Success",
                "id":new_obj_id,
                "data":result,
            }
            return Response(std_data,status=status.HTTP_201_CREATED)
        
        except openai.error.APIConnectionError as e:
            print(f"API連接錯誤: {e}")
        except Exception as e:
            # 處理所有其他未捕獲的異常的代碼
            print(f"An unexpected error occurred: {e}")
            
    @action(detail=False, methods=['GET'])
    def my_files(self, request):
        files = self.queryset.filter(creator=request.query_params['user'] ,indexed = True )
        serializer = self.serializer_class(files, many=True)
        std_data={
            "status":"Success",
            "data":serializer.data,
        }
        return Response(std_data,status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    @swagger_auto_schema(operation_id='downloadFile')  # 將 'my_view' 替換為您的 view 函數名稱
    def downloadFile(self, request):
        try:
            fId = request.query_params['id']
            if fId!="undefined" and int(fId) > 0:
                file = ChatGPTPDF.objects.get(id=request.query_params['id'])
                file_path = file.file_path
                with open(file_path, 'rb') as fh:
                    response = HttpResponse(fh.read(), content_type="application/octet-stream")
                    response['Content-Disposition'] = f'attachment; filename="{file.file_name}"'
                
                return response
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        except KeyError:
            # 'id' 不存在於 query_params 的錯誤處理
            pass   

    @action(detail=True, methods=['DELETE'])
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
    @action(detail=False, methods=['POST'])

    def chat_process(self,request):
        prompt = request.data.get('prompt')
        options = request.data.get('options', {})
        system_message = request.data.get('systemMessage')
        selectedKeys = request.data.get('selectedKeys')

        def process(chat):
            nonlocal first_chunk
            if first_chunk:
                response = chat
            else:
                response = '\n' + chat
            response = json.dumps(response)
            response.streaming_content = (response,)
            response['Content-Type'] = 'application/octet-stream'
            return response

        first_chunk = True
        try:
            response_data = ChatGPTPDF.chatReplyProcess({
                'message': prompt,
                'process': process,
                'selectedKeys': selectedKeys,
                'question_handler': self.question_handler,
                'stream_handler': self.stream_handler,
            })
        except Exception as e:
            return Response({'message': str(e)}, status=500)

        std_data={
            "status":"Success",
            "text":response_data,
        }
        return Response(std_data,status=status.HTTP_200_OK)
