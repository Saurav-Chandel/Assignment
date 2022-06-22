# import requests
# import random
# import twilio
# from django.conf import settings

# def send_otp_to_phone(phone_number):
#     try:
#         print("otp")
#         otp=random.randint(1000,9999)
        
#         url=f'https://2factor.in/API/V1/{settings.API_KEY}/SMS/{phone_number}/{otp}'
#         response=requests.get(url)
#         return otp

#     except Exception as e:
#         return None


import requests
from django.core.mail import send_mail
from main import settings
from rest_framework.response import Response




def send_verification_email(request,user_email,email_body):
    """
    Send Reset Password Mail
    """

    if user_email and email_body:
        Message = email_body
        from_email = settings.EMAIL_HOST_USER
        to_email = user_email
        try:
            send_mail(
                "verify your account<Don't Reply>",
                Message,
                from_email,
                [to_email],
                fail_silently=False,
            )
        except Exception as e:
            return e
    return None


from twilio.rest import Client
import random
otp=random.randint(1000,9999)

def send_otp_to_phone(request,phone_number,message1):
    account_sid = "AC77b0b5ff6daa1b596c30632c72e17c6a"
    auth_token  = "136ced11505153e99d316c9c140bc061"
    client = Client(account_sid, auth_token)

    if phone_number and message1:
        to=phone_number
        print(to)
        body1=message1
        print(body1)

        try:
           message = client.messages.create(
           body=body1,
           from_="+19106066129",
           to = to, 
           )


           if message:
              print("yes")
           else:
               print("no")   
       
           print(message.sid)
        
        except Exception as e:
            return None          
    return None     
    


# from twilio.rest import Client
# import random
# otp=random.randint(1000,9999)
# # Your Account SID from twilio.com/console
# account_sid = "AC77b0b5ff6daa1b596c30632c72e17c6a"
# # Your Auth Token from twilio.com/console
# auth_token  = "9e92134f37630e144c6d1449f2aad78a"

# client = Client(account_sid, auth_token)

# message = client.messages.create(
#     to="+919805488217", 
#     from_="+19106066129",
#     body="your otp is "+str(otp))

# print(message.sid)




