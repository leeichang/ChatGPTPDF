from celery import shared_task
from .util import (
openai_chat,
get_store_embedding,
embed_docs)
from langchain.docstore.document import Document
from datetime import datetime
from django.db.models.fields import BigIntegerField
from application import settings

import debugpy
# # Replace 5678 with the port you want to use for debugging
# debugpy.listen(('0.0.0.0', 5678))

# # Pause execution until debugger is attached
# debugpy.wait_for_client()

@shared_task
def process_history_embedding(guid: str,messages: str):

    print("process_history_embedding",guid,messages)
    prompt = f"""請依據以下內容總結出對話的摘要\n
    對話內容：{messages}" 以繁體中文回答\n"""  
    result = openai_chat(prompt)
    print("result",guid,result)
    now = datetime.now()
    doc =  Document(
            page_content=result, metadata={"datetime":f"{now}" }
        )
    print("doc",doc)
    historyIndex = embed_docs([doc],guid,settings.HISTORY_ROOT)


@shared_task
def clear_cache():
    print("call clear_cache")
    from .CacheManager import CacheManager  # Import here
    CacheManager().clear_expired()
