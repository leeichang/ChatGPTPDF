'''
  @author: hongzai
  @contact: 2505811377@qq.com
  @file: serializers.py
  @time: 2022/4/8 11:12
  @desc:
  '''
from .models import ChatGPTPDF
from dvadmin.utils.serializers import CustomModelSerializer
from .models import ChatGPTPDF
from rest_framework import serializers

class ChatGPTPDFSerializer(CustomModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    """
    序列化器
    """

    class Meta:
        model = ChatGPTPDF
        fields = "__all__"


class ChatGPTPDFCreateUpdateSerializer(CustomModelSerializer):
    """
    创建/更新时的列化器
    """

    class Meta:
        model = ChatGPTPDF
        fields = '__all__'
