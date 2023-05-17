'''
  @author: hongzai
  @contact: 2505811377@qq.com
  @file: serializers.py
  @time: 2022/4/8 11:12
  @desc:
  '''
from .models import unAnswerQuestion
from dvadmin.utils.serializers import CustomModelSerializer
from rest_framework import serializers

class unAnswerQuestionSerializer(CustomModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    """
    序列化器
    """

    class Meta:
        model = unAnswerQuestion
        fields = "__all__"


class unAnswerQuestionCreateUpdateSerializer(CustomModelSerializer):
    """
    创建/更新时的列化器
    """

    class Meta:
        model = unAnswerQuestion
        fields = '__all__'
