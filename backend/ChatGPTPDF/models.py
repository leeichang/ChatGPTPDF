from django.db import models

# Create your models here.
from dvadmin.utils.models import CoreModel
from dvadmin.system.models import Users as User


def user_directory_path(instance, filename):
    # 檔案上傳後的儲存路徑，使用 uuid 作為檔案名稱
    return 'user_{0}/{1}'.format(instance.creator.id, str(instance.file_uuid))

class ChatGPTPDF(CoreModel):
    file_name = models.CharField(max_length=255, verbose_name="檔案名稱")
    file_size = models.FloatField(verbose_name="檔案大小")
    file_uuid = models.UUIDField(verbose_name="檔案UUID")
    file_path = models.CharField(max_length=500, verbose_name="檔案路徑")
    indexed = models.BooleanField(verbose_name="是否已經索引", default=False)

    def __str__(self):
        return self.file_name

    class Meta:
        db_table = "files"
        verbose_name = '檔案表'
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)
