from django.contrib import admin
from django.urls import path
from .views import *
from rest_framework_simplejwt import views as jwt_views

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('signup/',SignUpView.as_view(),name="signup"),
    path('login/',LogInView.as_view(),name="login"),
    path('resend_otp/',Resendotp.as_view(),name="resend_otp"),
    path('phone_otp_verification/',PhoneOtpVerification.as_view(),name="resend_otp"),
    path('forgot_password/',ForgotPasswordAPI.as_view(),name="forgot_password"),
    path('reset_password/',ResetPasswordAPI,name="reset_password"),
    path('password_set_success/',PwdResetSuccess.as_view(),name="password_set_success"),
    path('change_password/',ChangePasswordAPI.as_view(),name="change_password"),
    path('update_profile/<int:pk>/',UpdateProfileAPI.as_view(),name="update_profile"),
    
    #tokens
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='phone_otp_verification'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),

    #SendRequests
    path('friend_requests/',SendRequests.as_view(),name="friend_requests"),
    path('friend_request_invitations/',Friend_Request_Inviitations.as_view(),name="friend_request_invitations"),
    path('send_request/',SentRequestsListAPI.as_view(),name="friend_request_invitations"),
    path('accept_friend_request/',Accept_Request.as_view(),name="send_request"),
    path('my_friends/',MyFriends.as_view(),name="my_friends"),
    path('cancel_request/',CancelRequest.as_view(),name="cancel_request"),
    path('unfriend/',Unfriend.as_view(),name="unfriend"),

    #post
    path('create_post/',CreatePostView.as_view(),name="create_post"),
    path('delete_post/',deletePostAPiView.as_view(),name="delete_post"),
]