from django.core.mail import send_mail


def send_vtf_mail(receiver, vtf_code):
    subject = "SCUPP团队"
    html_message = f"""
请使用以下代码进行验证:
    {vtf_code}
谢谢！
scupp团队。
                """
    from_mail = '1792236446@qq.com'
    receiver = [receiver]
    send_mail(subject=subject, message=html_message,
              from_email=from_mail, recipient_list=receiver)
