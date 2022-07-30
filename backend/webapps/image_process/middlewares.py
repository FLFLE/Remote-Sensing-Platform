from django.utils.deprecation import MiddlewareMixin

class DownloadImage(MiddlewareMixin):
    def process_response(self, request, response):
        response['Access-Control-Allow-Origin'] = "*"
        if request.method == 'OPTIONS':
            # 所有的头信息都允许
            response['Access-Control-Allow-Headers'] = '*'
        return response