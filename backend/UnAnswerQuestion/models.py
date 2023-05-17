from django.db import models

# Create your models here.
from dvadmin.utils.models import CoreModel
from dvadmin.system.models import Users as User


import uuid

from typing import Dict, Any
import array

class unAnswerQuestion(CoreModel):
    userInfo = models.CharField(max_length=255, verbose_name="使用者資訊")
    email = models.CharField(max_length=100, verbose_name="使用者信箱")
    phone = models.CharField(max_length=25, verbose_name="使用者電話")
    question = models.CharField(max_length =4000,verbose_name="問題")
    answer= models.CharField(max_length =4000,verbose_name="回答")

    def __str__(self):
        return self.file_name

    class Meta:
        db_table = "unAnswerQuestions"
        verbose_name = '未回答問題清單'
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)
