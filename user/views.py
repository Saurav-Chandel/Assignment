from django.shortcuts import render,HttpResponse
import requests
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated,AllowAny
# Create your views here.

from .helpers import send_otp_to_phone,send_verification_email

class SignUpView(APIView):
    '''
    SignUp API
    '''
    permission_classes=[AllowAny,]
    authentication_classes = []
    def post(self,request):
        data=request.data
        print(data)
        username=request.data.get('email')
        data['username']=username

        if User.objects.filter(email=data['email']).exists():
            return Response({'msg':'User already exists.'})
        try:
            import random
            PhoneOTP = random.randint(11111,22222)
            phone_number=request.data.get('phone_number')
            message="your otp is "+str(PhoneOTP)
            if phone_number and message:
                send_otp_to_phone(request,phone_number,message)
            # verification = client.verify.services(credentials.verify_service_id).verifications.create(to='+'+str(MobileNumber), channel='sms',locale='en')
        except:
           data['Response']=0
           data['Message']='Invalid mobile number.'
           return Response(data)   
        data['phone_otp']=PhoneOTP   
        #Add User data
        serializer=SignUpSerializer(data=data)    
        serializer.is_valid(raise_exception=True)
        user=serializer.save()
        d=dict()
        d['User']=str(user.id)
        d['DeviceToken']=data.get("DeviceToken","")
        d['DeviceType']=data.get("DeviceType","")
        Devices.objects.filter(DeviceToken=d["DeviceToken"]).delete()

        #Add Device data
        deviceserializer=DeviceSerializer(data=d)
        deviceserializer.is_valid(raise_exception=True)
        deviceserializer.save()

        # create a token on the basis of email and password.
        url='http://localhost:8000/user/api/token/'
        email=request.data.get('email')
        payload={'email':email,'password':request.data['password']}
        response = requests.request("POST", url, data=payload)
        token=response.json()

        # my_dict2 = {k: v for k, v in data.items() if k != 'phone_otp'}  #exclude phone-otp from data.items()

        return Response({'data':data,'token':token,'msg':'signup successfully'})

from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q,F

class LogInView(APIView):
    '''
    login  API
    '''
    permission_classes=[AllowAny,]
    authentication_classes = []
    def post(self,request):
        data=request.data
        email=request.data['email']
        password=request.data['password']
      
        try:
            user=User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'data':'User not found'})

        device_exists=Devices.objects.filter(User=user.id)
        if device_exists:
            device_exists.update(DeviceToken=request.data.get('DeviceToken',''))   
        else:
            d=dict()
            d['User']=str(user.id)
            d['DeviceToken']=data.get("DeviceToken","")
            d['DeviceType']=data.get("DeviceType","")
            Devices.objects.filter(DeviceToken=d["DeviceToken"]).delete()
            
            #Add Device data
            deviceserializer=DeviceSerializer(data=d)
            deviceserializer.is_valid(raise_exception=True)
            deviceserializer.save()

        if user.check_password(password):
            token=RefreshToken.for_user(user)
            if len(Token.objects.filter( token_type="access_token", user_id=user.id))==0:
                Token.objects.create(
                    user_id=user.id,
                    token=str(token.access_token),
                    token_type="access_token"
                )
            else:
                Token.objects.filter(user_id=user.id,token_type="access_token").update(token=str(token.access_token))
            serializer=UserSerializer(user)
            profile=Profiles.objects.filter(User=user.id).values()[0]
            profile['email']=User.objects.filter(id=user.id).values('email')[0]['email']
            return Response({'user':profile,"access_token": str(token.access_token),
                    "refresh_token": str(token),'msg':'Login successfully'})
        else:
            return Response({"status": 400, "msg": "Incorrect credentials."})
        

from rest_framework_simplejwt import authentication            
class Resendotp(APIView):
    """"
    Resend Otp
    """
    # permission_classes=[IsAuthenticated,]
    # authentication_classes = [authentication.JWTAuthentication]

    def post(self,request):
        data=request.data
        phone=data.get('phone_number')
        
        if phone == '':
            return Response({'msg':'plz enter a phone number'})

        user=request.user
        print(user.id)

        user_obj=User.objects.filter(id=user.id,is_deleted=0,is_phone_verified=1)
        print(user_obj)

        if user_obj:
            return Response({
                'data':'the customer is already verified'
            })
        else:
            import random
            PhoneOTP = random.randint(1111,2222)
            phone_number=data.get('phone_number')
            message="your otp is "+str(PhoneOTP)
            try:
                send_otp_to_phone(request,phone_number,message)
            except:
                return Response({'msg':'invalid phone_number'})

            finally:
                   c=User.objects.filter(id=user.id,is_deleted=0,phone_number=phone)
                   if not c:
                       return Response({'msg':'enter a registered phone_number'})
                   if c:
                       c.update(phone_otp=PhoneOTP)
                       cc=User.objects.filter(id=user.id).values('id','phone_otp')[0]

                       return Response({
                           'msg':'otp is sent to your register mobile number',
                           'data':cc
                       })    

class PhoneOtpVerification(APIView):
    """
     Phone Otp_verification
    """
   
    def post(self,request):
        data=request.data
        otp=data.get('otp')
        user=request.user

        if User.objects.filter(id=user.id,is_deleted=0,is_phone_verified=1).exists():  #when we use filter queryset--> .exists() is used .but not with get queryset.
            return Response({'msg':'user is already verified'})
    
        try:
            user_obj=User.objects.get(id=user.id,is_deleted=0,is_phone_verified=0)
        
            if str(user.phone_otp) == otp:  
                user_obj.is_phone_verified = True
                user_obj.save() 
                return Response ({
                            "data": None,
                            "code": status.HTTP_200_OK,
                            "message": "Otp verification successfully",
                             },status = status.HTTP_200_OK)

            else:
                return Response({
                        "data": None,
                        "code": status.HTTP_400_BAD_REQUEST,
                        "message": "You Entered Wrong OTP",
                    })                
        except User.DoesNotExist:
            return Response({
                    "data": None,
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "User Does Not Exist",
                })

import random, string
class ForgotPasswordAPI(APIView):
    '''
    Forgot password API
    '''

    def post(self,request):
        data=request.data
        email=data['email']
        u=User.objects.filter(email_iexact=email)

        if len(u)==0:
            return Response({"status":400,"msg":"Email does not exist.Please signup first."})

        else:
            x1 = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(5))
            x2 = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(4))    
            message = "Click on the below link to reset your password:\nhttp://localhost:8000/BeachPlus/ResetPwdTemplate/?code="+x1+str(u.values()[0]['id'])+x2
            send_verification_email(request,email,message)
            return Response({"msg":'A Forgot Password link has been sent to your registered mail.',"status":200})

from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse,HttpResponseRedirect
@api_view(['GET','POST'])
@csrf_exempt
def ResetPasswordAPI(request):
    code=request.GET['code']
    User_id=code[5:][:3]
    u=User.objects.get(id=User_id)
    dictValues={}
    dictValues['User_id']=User
    if u is not None:
        if request.method == 'POST':
            pwd=str(request.data['password'])
            ppwd=str(request.data['ppassword'])
        
            if pwd == ppwd and pwd != '' and ppwd != '':
                u.set_password(pwd)
                u.save()
                return HttpResponseRedirect('/BeachPlus/PwdResetSuccess/')
            else:
                dictValues['error']='Passwords do not match.'
                return render(request,'resetpassword.html',dictValues)
            
    return render(request,'resetpassword.html',dictValues)


class PwdResetSuccess(APIView):
    def get(self, request, *args, **kwargs):
        html = "<html><body>Your password has been reset.</body></html>" 
        return HttpResponse(html)

        
class ChangePasswordAPI(APIView):
    '''
    change password
    '''
    def post(self,request):
        data=request.data
        print(data)
        user=data['user_id']
        print(user)
        user1=request.data.get('user_id')
        u=User.objects.get(id__iexact=request.data.get('user_id'))
        print(u)

        old=request.data.get('old_password')
        new=request.data.get('new_password')

        if u.check_password(old):
            u.set_password(new)
            u.save()
            return HttpResponse('your password is changed')
        return HttpResponse("password did not match")

from .response import *
from rest_framework_simplejwt import authentication
class UpdateProfileAPI(APIView):
    permission_classes=[IsAuthenticated,]
    # authentication_classes = [authentication.JWTAuthentication]  //by default in settings
    def get_object(self, pk):
        try:
            return Profiles.objects.get(pk=pk)
        except Profiles.DoesNotExist:
            raise ResponseNotFound()

    def put(self,request,pk):
        data=request.data
        profile=self.get_object(pk)
        # print(profile)
        serializer=ProfileSerializer(profile,data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'data':serializer.data,'msg':'profile updated successfully'})



#Sends a friend request.(input:->id of Sender,Receiver)
class SendRequests(APIView):
    permission_classes=[IsAuthenticated,]
    # authentication_classes = [authentication.JWTAuthentication] 
    def post(self,request):
        serializer=FriendRequestsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"data":serializer.data,"msg":"friend requests send successfully"})


#jisko mene request bheji (means receiver) uski id input leke senders ka data nikal lenge.(kis kis ne meko request bheji hai)
class Friend_Request_Inviitations(APIView):
    # permission_classes=[IsAuthenticated,]
    # authentication_classes = [authentication.JWTAuthentication] 
    def post(self,request):
        data=request.data
        fr=FriendRequests.objects.select_related().filter(Receiver=request.data['Receiver']).values("id","Sender",ProfileImage=F("Sender__profile_image"),FirstName=F("Sender__User__first_name"),LastName=F("Sender__User__last_name"),Email=F("Sender__User__email"), City=F("Sender__City"),State=F("Sender__State"),Country=F("Sender__Country"),latitude=F("Sender__latitude"),longitude=F("Sender__longitude"),ZipCode=F("Sender__ZipCode"))
        return Response({"data":fr,"msg":"List of all invitaions"})

#mene kis kis ko request bheji hai
class SentRequestsListAPI(APIView):
    # permission_classes=(IsAuthenticated,)
    def post(self,request,*args,**kwargs):
        requests=FriendRequests.objects.filter(Sender=request.POST['User'],Status='Sent').values('id',User_id=F('Receiver_id'),ProfileImage=F("Receiver__profile_image"),FirstName=F('Receiver__User__first_name'),LastName=F("Receiver__User__last_name"),Email=F("Receiver__User__email"), City=F("Receiver__City"),State=F("Receiver__State"),Country=F("Receiver__Country"),latitude=F("Receiver__latitude"),longitude=F("Receiver__longitude"),ZipCode=F("Receiver__ZipCode"))
        return Response({
            'data':requests,
            'msg':'Send RequestsList',
            'status':200
        })

#accepts the friend requests.
class Accept_Request(APIView):
    # permission_classes=(IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        data = FriendRequests.objects.filter(id=request.POST["Request_id"]).update(
            Status="Accept"
        )
        return Response({"msg": "Accept Friend", "status": 200})



#list of firiends who accepts my requests.
class MyFriends(APIView):
    # permission_classes=(IsAuthenticated,)
    def post(self,request,*args,**kwargs):
        f=dict()
        F1=FriendRequests.objects.select_related().filter(Receiver=request.POST['User'],Status='Accept').values("id","DateAdded",User_id=F('Sender_id'),ProfileImage=F("Sender__profile_image"),FirstName=F("Sender__User__first_name"),LastName=F("Sender__User__last_name"),Email=F("Sender__User__email"), City=F("Sender__City"),State=F("Sender__State"),Country=F("Sender__Country"),latitude=F("Sender__latitude"),longitude=F("Sender__longitude"),ZipCode=F("Sender__ZipCode"))
        F2=FriendRequests.objects.select_related().filter(Sender=request.POST['User'],Status='Accept').values('id','DateAdded',User_id=F('Receiver_id'),ProfileImage=F("Receiver__profile_image"),FirstName=F('Receiver__User__first_name'),LastName=F("Receiver__User__last_name"),Email=F("Receiver__User__email"), City=F("Receiver__City"),State=F("Receiver__State"),Country=F("Receiver__Country"),latitude=F("Receiver__latitude"),longitude=F("Receiver__longitude"),ZipCode=F("Receiver__ZipCode"))
        f=list(F1)+list(F2)
        return Response({'data':f,'msg':'Friends list.','status':200})

#mene jis jis ko requests bheji hai ...unko mai cancel bhi kr skta hu unke accept krne se pehle.
class CancelRequest(APIView):
    # permission_classes=(IsAuthenticated,)
    def post(self,request,*args,**kwargs):
        FriendRequests.objects.filter(id=request.POST['Request_id']).delete()
        return Response({'msg':'Request Cancelled.','status':200})

# we both are already a friends ,and i want to unfriend him or her.
class Unfriend(APIView):
    # permission_classes=(IsAuthenticated,)
    def post(self,request,*args,**kwargs):
        FriendRequests.objects.filter(id=request.POST['Request_id'],Status='Accept').delete()
        return Response({'msg':'Unfriend.','status':200})

#post
from django.core.files.storage import FileSystemStorage
from datetime import datetime
class CreatePostView(APIView):
    # permission_classes=[IsAuthenticated,]
    # authentication_classes = [authentication.JWTAuthentication] 
    def post(self,request):
        data=request.data
        if len(post.objects.filter(user=request.POST['user']))>0:
            post.objects.filter(user=request.POST['user']).delete()
        serializer=PostSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if len(request.FILES.getlist('vedio'))>0:
            files=request.FILES.getlist('vedio')  
            print(files) 
            file=[]
            for i in range(len(files)):
                fs = FileSystemStorage()
                filename = fs.save(files[i], files[i])
                uploaded_file_url = fs.url(filename)
                file.append(uploaded_file_url)
            post.objects.filter(user=request.POST['user']).update(video=file)    
        p=post.objects.filter(user=request.POST['user']).values()[0]
        return Response({"data":p,'msg':'post created successfully'})


import os
from main import settings
class deletePostAPiView(APIView):
    # permission_classes=[IsAuthenticated,]
    # authentication_classes = [authentication.JWTAuthentication] 
    def post(self,request):
        data=request.data
        user=request.data['user']
        ImageName=str(request.data['postdata'])
        user=post.objects.filter(user=request.data['user'])
        rep=str(user.values()[0]['video']).replace(ImageName,'')
        replace=list(filter(None,str(rep).replace('[','').replace(']','').replace('\'','').replace(" ","").split(',')))
        user.update(video=replace)
        try:
            ImageName=ImageName.replace('%20',' ').replace('%3A',':').replace('/media/','/')
            print(ImageName)
            # print(os.path.join(settings.BASE_DIR,'static_media'+str(str(ImageName))))
            # print(os.path.join(settings.BASE_DIR,'static_media\BusinessImages'+str(str(ImageName))))
            os.remove(os.path.join(settings.BASE_DIR,'static_media'+str(str(ImageName))))         ###delete the image from static_media
        except:
            a=1
        p=post.objects.filter(user=request.POST['user']).values()[0]
        return Response({"data":p,'msg':'delete the postdata successfully'})
















        
  
        



