from webapps.utils import generate_response
from webapps.user.serializers import UserSerializer
from webapps.user.models import User, VertificationCode
from webapps.user import mail
from rest_framework import status
from rest_framework.views import APIView
from random import randint


class UserView(APIView):
    def post(self, request):
        action = request.data["action"]
        if action == "login":
            return self.login(request)
        elif action == "register":
            return self.register(request)
        else:
            return generate_response(
                {"msg": "action error"}, status.HTTP_400_BAD_REQUEST
            )

    # def delete(self, request):
    #     return self.log_out(request)

    # def log_out(self, request):
    #     email_address = request.data["email_address"]
    #     try:
    #         user = User.objects.get(email_address=email_address)
    #         user.is_login = 0
    #         user.save()
    #         return generate_response({"msg": "logged out"}, status.HTTP_204_NO_CONTENT)
    #     except Exception as e:
    #         return generate_response(
    #             {"msg": "something is error"}, status.HTTP_400_BAD_REQUEST
    #         )

    def login(self, request):
        msg = {"msg": "", "user": ""}
        email_address = request.data["email_address"]
        password = request.data["password"]

        # 校验用户是否存在
        try:
            user = User.objects.get(email_address=email_address)
        except Exception as e:
            msg["msg"] = "输入的邮箱未注册！"
            return generate_response(msg, status.HTTP_401_UNAUTHORIZED)

        # 用户存在的情况下校验密码是否正确以及是否已登录，正确则返回200.错误返回401
        if not user.verify_password(password):
            msg["msg"] = "密码输入有误！"
            return generate_response(msg, status.HTTP_401_UNAUTHORIZED)
        # elif user.has_login():
        #     msg["msg"] = "you have already logged in"
        #     return generate_response(msg, status.HTTP_400_BAD_REQUEST)
        # # 登录后修改标志位
        # user.is_login = 1
        # user.save()

        # 将用户的个人信息序列化，并返回前端
        serializer = UserSerializer(user)
        current_user = serializer.data
        msg["msg"] = "登录成功！"
        msg["user"] = current_user
        return generate_response(msg, status.HTTP_200_OK)

    # 发送完验证码后，第二次提交带有验证码的整个表单
    def register(self, request):
        username = request.data["username"]
        email_address = request.data["email_address"]
        password = request.data["password"]
        vtf_code = request.data["vtf_code"]

        # 校验验证码的正确性，失败则返回 406
        try:
            vtf = VertificationCode.objects.get(
                email_address=email_address, vertificationCode=vtf_code
            )
        except Exception as e:
            return generate_response(
                {"msg": "验证码输入有误！"}, status.HTTP_406_NOT_ACCEPTABLE
            )

        # 向数据库插入用户信息，成功返回 200，失败返回 406
        try:
            User.objects.create(
                username=username, email_address=email_address, password=password
            )
        except Exception as e:
            return generate_response(
                {"msg": "注册失败！"}, status.HTTP_406_NOT_ACCEPTABLE
            )
        return generate_response({"msg": "注册成功！"}, status.HTTP_200_OK)


class SendVertificationCode(APIView):
    def post(self, request):
        return self.sendCode(request)

    def sendCode(self, request):
        code = randint(100000, 999999)
        email_address = request.data["email_address"]
        # 试图通过用户提交的邮箱检验是否已经注册过
        # 已经注册过则提示用户，未注册过才向用户发送验证码
        try:
            user = User.objects.get(email_address=email_address)
        except Exception as e:
            # 判断用户是否是第一次发送，如果是第一次，则在数据库中插入记录
            # 若不是第一次发送，则更新数据库中的原有记录
            try:
                vtf = VertificationCode.objects.get(email_address=email_address)
            except Exception as e:
                VertificationCode.objects.create(
                    email_address=email_address, vertificationCode=code
                )
                mail.send_vtf_mail(email_address, code)
                return generate_response(
                    {"msg": "验证码发送成功！"}, status.HTTP_200_OK
                )

            # 如果不是第一次发送，则更新表中之前保存的验证码
            vtf.vertificationCode = code
            vtf.save()
            mail.send_vtf_mail(email_address, code)
            return generate_response({"msg": "验证码发送成功！"}, status.HTTP_200_OK)

        # 用户已经注册过则不予发送
        return generate_response(
            {"msg": "此邮箱已注册过！"}, status.HTTP_403_FORBIDDEN
        )


class PasswordView(APIView):
    def post(self, request):
        action = request.data["action"]
        if action == "send_vtf":
            return self.send_vtf(request)
        elif action == "reset":
            return self.reset_password(request)
        else:
            return generate_response(
                {"msg": "action error"}, status.HTTP_400_BAD_REQUEST
            )

    def send_vtf(self, request):
        email_address = request.data["email_address"]
        try:
            # 校验用户输入的邮箱是否是已注册
            user = User.objects.get(email_address=email_address)
            # 如果用户已经注册,那么vtf表应该有邮箱记录,更新验证码记录
            vtf = VertificationCode.objects.get(email_address=email_address)
            code = randint(100000, 999999)
            vtf.vertificationCode = code
            vtf.save()
            mail.send_vtf_mail(email_address, code)
            return generate_response({"msg": "验证码发送成功！"}, status.HTTP_200_OK)
        except Exception as e:
            # 用户输入了未注册的邮箱
            return generate_response(
                {"msg": "此邮箱未注册！"},
                status.HTTP_401_UNAUTHORIZED,
            )

    # 点击修改密码时，提交整个页面表单
    def reset_password(self, request):
        email_address = request.data["email_address"]
        vtf_code = request.data["vtf_code"]
        # 校验验证码的正确性
        if self.check_vtf(email_address, vtf_code):
            new_pwd = request.data["new_pwd"]
            user = User.objects.get(email_address=email_address)

            # 新密码与旧密码相同时，不予重置
            if user.password == new_pwd:
                return generate_response(
                    {"msg": "新密码与旧密码相同，请重新输入！"},
                    status.HTTP_406_NOT_ACCEPTABLE,
                )
            user.password = new_pwd
            user.save()
            return generate_response(
                {"msg": "密码重置成功！"}, status.HTTP_200_OK
            )

        return generate_response(
            {"msg": "验证码输入有误！"}, status.HTTP_401_UNAUTHORIZED
        )

    # 校验验证码的正确性
    def check_vtf(self, email_address, vtf_code):
        try:
            vtf = VertificationCode.objects.get(
                email_address=email_address, vertificationCode=vtf_code
            )
            return True

        except Exception as e:
            return False
