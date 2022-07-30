from webapps.user.models import User
from rest_framework.views import APIView
from rest_framework import status
from webapps.utils import generate_response
from webapps.history.models import History


class HistoryView(APIView):
    def post(self, request):
        return self.query_history_list(request)

    def query_history_list(self, request):
        current_user = request.data["email_address"]
        history_list = []
        try:
            history = History.objects.filter(email_address=current_user)
            for record in history:
                upload_record = {}
                upload_record["email_address"] = record.email_address
                upload_record["upload_images"] = str(record.upload_images).split("?")
                upload_record["result_images"] = str(record.result_images).split("?")
                upload_record["upload_time"] = record.upload_time
                upload_record["type"] = record.type
                history_list.append(upload_record)
     
            return generate_response({"history_list": history_list}, status.HTTP_200_OK)

        except Exception as e:
            return generate_response({"history_list": None}, status.HTTP_404_NOT_FOUND)


class UsageView(APIView):
    def post(self, request):
        return self.query_use_times(request)

    def query_use_times(self, request):
        current_user = request.data["email_address"]
        try:
            user = User.objects.get(email_address=current_user)
            cd_use_time = user.cd_use_time
            td_use_time = user.td_use_time
            tc_use_time = user.tc_use_time
            te_use_time = user.te_use_time
            remain_times = user.times
            return generate_response(
                {
                    "change_detection": cd_use_time,
                    "target_detection": td_use_time,
                    "terrain_classification": tc_use_time,
                    "target_extraction": te_use_time,
                    "remain_times": remain_times,
                },
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            return generate_response(
                {"usage": None}, status_code=status.HTTP_404_NOT_FOUND
            )


class RemainTimeView(APIView):
    def post(self, request):
        return self.query_remaining_times(request)

    def query_remaining_times(self, request):
        email_address = request.data["email_address"]
        try:
            user = User.objects.get(email_address=email_address)
            remaining_times = user.times
            return generate_response({"times": remaining_times}, status.HTTP_200_OK)
        except Exception as e:
            return generate_response({"msg": "query fault"}, status.HTTP_404_NOT_FOUND)
