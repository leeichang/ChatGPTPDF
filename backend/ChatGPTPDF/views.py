import os
from django.shortcuts import render

from rest_framework import status,viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from .models import ChatGPTPDF
from .serializers import ChatGPTPDFSerializer,ChatGPTPDFCreateUpdateSerializer
from dvadmin.utils.viewset import CustomModelViewSet

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

    @action(detail=False, methods=['POST'])
    def perform_create(self, serializer):
        file = self.request.data['file']
        file_name = file.name
        file_size = file.size
        file_path = os.path.join(os.environ['FILE_UPLOAD_DIR'], file_name)

        with open(file_path, 'wb') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        ChatGPTPDF.objects.create(
            file_name=file_name,
            file_size=file_size,
            file_path=file_path,
        )

    @action(detail=False, methods=['GET'])
    def my_files(self, request):
        files = ChatGPTPDF.queryset.filter(creator=request.user)
        serializer = self.serializer_class(files, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'])
    def download(self, request, pk):
        file = ChatGPTPDF.objects.get(pk=pk)
        file_path = file.file.path
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/octet-stream")
            response['Content-Disposition'] = f'attachment; filename="{file.name}"'
            return response

    @action(detail=True, methods=['DELETE'])
    def delete(self, request, pk):
        file = ChatGPTPDF.objects.get(pk=pk)
        file_path = file.file_path
        file.delete()
        os.remove(file_path)
        return Response(status=status.HTTP_204_NO_CONTENT)

