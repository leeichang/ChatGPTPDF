import os
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status,viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from .models import unAnswerQuestion
from .serializers import unAnswerQuestionSerializer,unAnswerQuestionCreateUpdateSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from rest_framework.authentication import BaseAuthentication
from drf_yasg.utils import swagger_auto_schema
# from .callback import QuestionGenCallbackHandler, StreamingLLMCallbackHandler

import uuid
class unAnswerQuestionViewSet(CustomModelViewSet):
    """
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = unAnswerQuestion.objects.all()
    serializer_class = unAnswerQuestionSerializer
    create_serializer_class = unAnswerQuestionCreateUpdateSerializer
    update_serializer_class = unAnswerQuestionCreateUpdateSerializer

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
    
