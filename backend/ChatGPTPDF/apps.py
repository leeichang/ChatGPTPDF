from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler

from .tasks import clear_cache  

class ChatgptpdfConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ChatGPTPDF'

    def ready(self):
        # 创建一个调度器
        scheduler = BackgroundScheduler()

        # 添加一个任务到调度器，指定使用 interval 调度策略，每隔3秒执行一次 job_function
        scheduler.add_job(clear_cache, 'interval', seconds=300)

        # 开始运行调度器
        scheduler.start()