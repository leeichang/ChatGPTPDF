from django.db import models

# Create your models here.
from dvadmin.utils.models import CoreModel
from dvadmin.system.models import Users as User

from .util import (
    parse_pdf,
    text_to_docs,
    embed_docs,
    get_store_embedding,
    search_docs,
    get_answer,
    get_sources,
    pinecone_embed_docs,
    get_pinecone_embedding,
    get_answer_qa,
    get_sources_qa,
    get_answer_pinecone,
)
import uuid
from .CacheManager import CacheManager

def user_directory_path(instance, filename):
    # 檔案上傳後的儲存路徑，使用 uuid 作為檔案名稱
    return 'user_{0}/{1}'.format(instance.creator.id, str(instance.file_uuid))

class ChatGPTPDF(CoreModel):
    file_name = models.CharField(max_length=255, verbose_name="檔案名稱")
    file_size = models.FloatField(verbose_name="檔案大小")
    file_uuid = models.UUIDField(verbose_name="檔案UUID", db_index=True)
    file_path = models.CharField(max_length=500, verbose_name="檔案路徑")
    indexed = models.BooleanField(verbose_name="是否已經索引", default=False)

    def __str__(self):
        return self.file_name

    def handleFileIndex(filePath:str, uuid: str):
        cache = CacheManager()
        # 1. parse pdf
        content = parse_pdf(filePath)
        # 2. text to docs
        text = text_to_docs(content)
        # 3. embed docs
        pdf_id = uuid
        index = embed_docs(text,pdf_id)

        # 4. put index into cache
        cache.set(pdf_id, index)

    def set_qa_documents(document_ids):
        cache = CacheManager()
        for doc in document_ids:
            obj = ChatGPTPDF.objects.get(id=doc)
            uuid = obj.file_uuid
            if not cache.check_cache(uuid):
                # 1. get store embedding
                store_embedding = get_store_embedding(uuid)
                # 2. put store embedding into cache
                cache.set(uuid, store_embedding)

    class Meta:
        db_table = "files"
        verbose_name = '檔案表'
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)
