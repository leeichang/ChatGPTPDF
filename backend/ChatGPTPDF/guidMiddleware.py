class GuidMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        guid = request.META.get('HTTP_X_GUID')
        if guid is not None:
            # 在這裡處理你的 GUID
            pass

        response = self.get_response(request)

        return response
