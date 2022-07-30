import gc
from django.http import JsonResponse

def generate_response(msg, status_code):
    response = JsonResponse(msg)
    response.status_code = status_code
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    return response


# def release(objects):
#     for obj in objects:
#         del obj
#     gc.collect()