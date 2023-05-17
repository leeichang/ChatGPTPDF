'''
  @author: leeichang
  @contact: ichang.lee@cymmetrik.com
  @file: urls.py
  @time: 2023/5/3 17:13
  @desc:
  '''
from rest_framework.routers import SimpleRouter

from .views import unAnswerQuestionViewSet

router = SimpleRouter()
router.register("unAnswerQuestion", unAnswerQuestionViewSet)

urlpatterns = [
]
urlpatterns += router.urls