from django.http import JsonResponse
from rest_framework.decorators import api_view
import os
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes

def is_not_empty_string(s):
    return isinstance(s, str) and bool(s.strip())

@api_view(['POST'])
@permission_classes([AllowAny])
def session(request):
    try:
        AUTH_SECRET_KEY = os.environ.get('AUTH_SECRET_KEY')
        has_auth = is_not_empty_string(AUTH_SECRET_KEY)
        response_data = {
            'status': 'Success',
            'message': '',
            'data': {
                'auth': has_auth,
                'model': 'ChatGPTPDF', #current_model()
            }
        }
        return JsonResponse(response_data)
    except Exception as error:
        response_data = {
            'status': 'Fail',
            'message': str(error),
            'data': None
        }
        return JsonResponse(response_data)

def current_model():
    # Implement your current_model function here
    pass
