'''
  @author: leeichang
  @contact: ichang.lee@cymmetrik.com
  @file: urls.py
  @time: 2023/3/30 12:23
  @desc:
  '''
from rest_framework.routers import SimpleRouter

from .views import ChatGPTPDFViewSet

router = SimpleRouter()
router.register("File", ChatGPTPDFViewSet)

urlpatterns = [
]
urlpatterns += router.urls