from django.db import models
import os
# Create your models here.
from dvadmin.utils.models import CoreModel
from dvadmin.system.models import Users as User

from .util import (
    parse_content,
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
    get_answer_summary,
    openai_chat
)
import uuid
from .CacheManager import CacheManager

from typing import Dict, Any
from langchain.memory import ConversationBufferWindowMemory
from langchain.llms import OpenAI
from .query_data import get_chain
import array
from application import settings

def user_directory_path(instance, filename):
    # 檔案上傳後的儲存路徑，使用 uuid 作為檔案名稱
    return 'user_{0}/{1}'.format(instance.creator.id, str(instance.file_uuid))

class ChatGPTPDF(CoreModel):
    file_name = models.CharField(max_length=255, verbose_name="檔案名稱")
    file_size = models.FloatField(verbose_name="檔案大小")
    file_uuid = models.UUIDField(verbose_name="檔案UUID", db_index=True)
    file_path = models.CharField(max_length=500, verbose_name="檔案路徑")
    Abstract = models.TextField(verbose_name="摘要內容",null=True)
    indexed = models.BooleanField(verbose_name="是否已經建立索引",default=False)


    def __str__(self):
        return self.file_name

    def handleFileIndex(filePath:str, uuid: str):
        cache = CacheManager()
        # 1. parse file content into Document objects
        text = parse_content(filePath)
        # 3. embed docs
        pdf_id = uuid
        
        index = embed_docs(text,pdf_id)

        # 4. put index into cache
        cache.set(pdf_id, index)

    def set_qa_documents(document_ids,user_guid=""):
        cache = CacheManager()
        # 判斷 my_array 是否是 array 型別  
        if isinstance(document_ids, array.array):
            for doc in document_ids:
                obj = ChatGPTPDF.objects.get(id=doc)
                uuid = obj.file_uuid
                if not cache.check_cache(uuid):
                    # 1. get store embedding
                    store_embedding = get_store_embedding(uuid)
                    # 2. put store embedding into cache
                    cache.set(uuid, store_embedding)   
        else:
            if(document_ids>0):
                obj = ChatGPTPDF.objects.get(id=document_ids)
                uuid = obj.file_uuid
                if not cache.check_cache(uuid):
                    # 1. get store embedding
                    store_embedding = get_store_embedding(uuid)
                    # 2. put store embedding into cache
                    cache.set(uuid, store_embedding)           

    def get_chat_history(uuid)->ConversationBufferWindowMemory:
        cache = CacheManager()
        key = "HISTORY_KEY_" + str(uuid)
        if cache.check_cache(key):
            history = cache.get(key)
        else:
            llm = OpenAI(temperature=0, max_tokens_limit=10, openai_api_key=os.getenv("OPENAI_API_KEY"))
            history = ConversationBufferWindowMemory(k=5,memory_key="chat_history", input_key="human_input")

        return history

    @staticmethod
    def contains_keywords(text, keywords):
        return any(keyword in text for keyword in keywords) 

    def chatReplyProcess(options: Dict[str, Any]) -> None:
        message = options['message']
        process = options.get('process')
        selectedKeys = options.get('selectedKeys')
        question_handler = options.get('question_handler')
        stream_handler= options.get('stream_handler')
        guid = options.get('guid')
        id = 0;
        if isinstance(selectedKeys, array.array):
            id = selectedKeys[0]
        else:
            id = selectedKeys

        cache = CacheManager()
        # 1. get store embedding
        obj = ChatGPTPDF.objects.get(id=id)
        uuid = obj.file_uuid
        filename,file_ext = os.path.splitext(obj.file_name)
        history = ChatGPTPDF.get_chat_history(guid)
        if cache.check_cache(uuid):
            store_embedding = cache.get(uuid)
        else:
            store_embedding = get_store_embedding(uuid)
            cache.set(uuid, store_embedding)
        history_key = guid #"HISTORY_EMBEDDING_" + guid    
        if cache.check_cache(history_key):
            history_embedding = cache.get(history_key)
        else:
            history_embedding = get_store_embedding(history_key,settings.HISTORY_ROOT)
            cache.set(history_key, history_embedding)
        if history_embedding is not None:        
            store_embedding.merge_from(history_embedding)
        # 2. search docs
        search_result = search_docs(store_embedding,message)
        metadata = search_result[0].metadata
        if "filename" in metadata:
            filename = metadata["filename"]
        elif "source" in metadata:
            filename = metadata["source"]

        if filename.endswith('.xlsx') or filename.endswith('.xls') or filename.endswith('.csv'):
            for doc in search_result:
                doc.page_content = doc.page_content.replace("\'", "")

        # 3. get answer
        answer = get_answer_qa(search_result , message,file_ext,history)
        result =answer["output_text"]
        NoAnswer=["很抱歉","不知道","无法回答","無法回答","對不起","沒有提到在提供文件中","無法給出明確答案","未提及相關內容","並未提及","未提供相關解決方案","並未在提供的文件","沒有明確回答","沒有提到","在文件中找不到"]
        if result.startswith("我不知道") and len(result)<30:
            result = f"""感謝您的提問！我們非常重視您的問題：{message}，但目前我們還無法立即回答。為了讓您能得到最精確的答案，我們需要進一步調查和確認。請您填寫下方的資料，留下聯絡訊息，我們會盡快回覆您。如果您還有任何其他問題，歡迎隨時聯繫我們。謝謝您的耐心等待，期待為您提供更好的服務！
                     您的稱謂 您的電子郵件 
            範例格式： 李先生 sales.info@cymmetrik.com
            """
            inversion = False
        else:
            result = answer["output_text"]
            inversion = False
            
        #history.save_context({"human_input": f"{message}"}, {"outputs": f"{result}"})
        key = "HISTORY_KEY_" + guid
        cache.set(key, history)

        return result,inversion
    
    def getDefaultSummaryAndQuestion(uuid,file_extension,guid):
        cache = CacheManager()
        history = ConversationBufferWindowMemory(k=5,memory_key="chat_history", input_key="human_input")
        if cache.check_cache(uuid):
            store_embedding = cache.get(uuid)
        else:
            store_embedding = get_store_embedding(uuid)
            cache.set(uuid, store_embedding)
        message = "請給我本篇文章的摘要大概在200個字以內，並回覆繁體中文"
        # 2. search docs
        search_result = search_docs(store_embedding,message)        
        # 3. get answer
        answer = get_answer_qa(search_result , message,file_extension,history)
        result =answer["output_text"]
        message = "請給我本篇文章的5個重點，以條列式的方式呈現!並回覆繁體中文"
        search_result = search_docs(store_embedding,message)        
        # 3. get answer
        answer = get_answer_qa(search_result , message,file_extension,history)
        result1 =answer["output_text"]
        result = result + "\n\n五個內容相關重點：\n" + result1
        message = f"請依據下面摘要內容:{result} 建議三個跟內容有關的問題，請以條列式的方式呈現!並回覆繁體中文"
        result2 = openai_chat(message)
        result = result + "\n\n三個內容相關建議問題\n" + result2
        llm = OpenAI(temperature=0, max_tokens_limit=10, openai_api_key=os.getenv("OPENAI_API_KEY"))
        history.save_context({"human_input": ""},{"outputs":"{result}"})
        key = "HISTORY_KEY_" + guid
        cache.set(key, history)
        return result
    
    @staticmethod
    def get_share(uuid:str)->'ChatGPTPDF':
        obj = ChatGPTPDF.objects.filter(file_uuid=uuid).order_by('id').first()
        return obj


    class Meta:
        db_table = "files"
        verbose_name = '檔案表'
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)
