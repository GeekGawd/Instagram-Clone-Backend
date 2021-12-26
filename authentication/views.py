from re import S
from rest_framework import generics, serializers, status, authentication, permissions
from django.shortcuts import redirect, resolve_url, reverse
from core.models import *
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from authentication.serializers import LoginSerializer, UserSerializer, AuthTokenSerializer, ChangePasswordSerializer
from django.core.mail import send_mail, EmailMessage
import random, time, datetime
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import Http404
from django.utils import timezone
from django.contrib.auth import authenticate
import jwt
from django.contrib.auth.hashers import check_password, make_password
from django.conf import settings

class CreateUserView(APIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    
    def post(self, request):
        name = request.data.get('name',)
        request.data['name'] = name.strip().title()
        serializer = self.serializer_class(data=request.data)
        request_email = request.data.get('email',)
        try:
             user = User.objects.get(email__iexact = request_email)
        except:
            if serializer.is_valid():
                serializer.save()
                login_send_otp_email(request_email, signup_otp = True)
                return Response({'status' : 'User registered successfully and an OTP has been sent to your email.'}, status=status.HTTP_201_CREATED)
            return Response({'status' : 'Registration was not successful. Please enter the details carefully.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response({'status' : 'Entered email is already registered.'}, status=status.HTTP_403_FORBIDDEN)
        

class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        request_email = request.data.get('email',)
        try:
            user1 = User.objects.get(email__iexact = request_email)
        except: 
            return Response({'status':'User not registered'}, status=status.HTTP_401_UNAUTHORIZED)

        if user1.is_active is True:
            serializer = AuthTokenSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({
                'status':'User not validated, please goto login/otp'
            },status=status.HTTP_403_FORBIDDEN)

def login_send_otp_email(email,subject="[OTP] New Login for Swaad App", signup_otp = False):
    
        OTP.objects.filter(otp_email__iexact = email).delete()

        otp = random.randint(1000,9999)

        msg = EmailMessage(subject, f'<div style="font-family: Helvetica,Arial,sans-serif;min-width:1000px;overflow:auto;line-height:2"><div style="margin:50px auto;width:70%;padding:20px 0"><div style="border-bottom:1px solid #eee"><a href="" style="font-size:2em;color: #FFD243;text-decoration:none;font-weight:600">Swaad</a></div><p style="font-size:1.2em">Greetings,</p><p style="font-size:1.2em"> Thank you for creating an account on Swaad. You can count on us for quality, service, and selection. Now, we would not like to hold you up, so use the following OTP to complete your Sign Up procedures and order away.<br><b style="text-align: center;display: block;">Note: OTP is only valid for 5 minutes.</b></p><h2 style="font-size: 1.9em;background: #FFD243;margin: 0 auto;width: max-content;padding: 0 15px;color: #fff;border-radius: 4px;">{otp}</h2><p style="font-size:1.2em;">Regards,<br/>Team Swaad</p><hr style="border:none;border-top:1px solid #eee" /><div style="float:right;padding:8px 0;color:#aaa;font-size:1.2em;line-height:1;font-weight:500"><p>Swaad</p><p>Boys Hostel, Near Girl Hostel AKGEC</p><p>Ghaziabad</p></div></div></div>', 'swaad.info.contact@gmail.com', (email,))
        msg.content_subtype = "html"
        msg.send()

        time_created = int(time.time())
        OTP.objects.create(otp=otp, otp_email = email, time_created = time_created)

        if signup_otp:
            return
        else:
            return Response({"OTP has been successfully sent to your email."})

def send_otp_email(email,subject):
    
    OTP.objects.filter(otp_email__iexact = email).delete()

    otp = random.randint(1000,9999)

    msg = EmailMessage(subject, f'<div style="font-family: Helvetica,Arial,sans-serif;min-width:1000px;overflow:auto;line-height:2"><div style="margin:50px auto;width:70%;padding:20px 0"><div style="border-bottom:1px solid #eee"><a href="" style="font-size:2em;color: #FFD243;text-decoration:none;font-weight:600">Swaad</a></div><p style="font-size:1.2em">Greetings,</p><p style="font-size:1.2em"> Looks like you forgot your password. No worries we are here to help you recover your account. Use the following OTP to recover your account and start ordering the delicacies again in no time. <br><b style="text-align: center;display: block;">Note: OTP is only valid for 5 minutes.</b></p><h2 style="font-size: 1.9em;background: #FFD243;margin: 0 auto;width: max-content;padding: 0 15px;color: #fff;border-radius: 4px;">{otp}</h2><p style="font-size:1.2em;">Regards,<br/>Team Swaad</p><hr style="border:none;border-top:1px solid #eee" /><div style="float:right;padding:8px 0;color:#aaa;font-size:1.2em;line-height:1;font-weight:500"><p>Swaad</p><p>Boys Hostel, Near Girl Hostel AKGEC</p><p>Ghaziabad</p></div></div></div>' , 'swaad.info.contact@gmail.com', (email,))
    msg.content_subtype = "html"
    msg.send()

    time_created = int(time.time())

    OTP.objects.create(otp=otp, otp_email = email, time_created = time_created)

class PasswordReset(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        request_email = request.data.get("email", )

        try:
            user = User.objects.get(email__iexact = request_email)
        except: 
            return Response({"status" : "No such account exists"},status = status.HTTP_400_BAD_REQUEST)

        if user.is_active:
            send_otp_email(email = request_email,subject="[OTP] Password Change for Swaad App") 
            return Response({"status" : "OTP has been sent to your email."}, status = status.HTTP_200_OK)
        return Response({"status": "Please verify your account."}, status=status.HTTP_406_NOT_ACCEPTABLE)


class PasswordResetOTPConfirm(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        data = request.data
        request_otp   = data.get("otp",)
        request_email = data.get("email",)

        if request_email:
            try:
                otp_instance = OTP.objects.get(otp_email__iexact = request_email)
                user = User.objects.get(email__iexact = request_email)
            except:
                raise Http404

            request_time = otp_instance.time_created
            email = otp_instance.otp_email
            current_time = int(time.time())

            if current_time - request_time > 300:
                return Response({"status" : "Sorry, entered OTP has expired.", "entered otp": request_otp},status = status.HTTP_408_REQUEST_TIMEOUT)

            if str(otp_instance.otp) != str(request_otp):
                 return Response({"status" : "Sorry, entered OTP doesn't match the sent OTP."},status = status.HTTP_409_CONFLICT)
            
            if (request_email != email):
                return Response({"status" : "Sorry, entered OTP doesn't belong to your email id."},status = status.HTTP_401_UNAUTHORIZED)
            
            serializer = AuthTokenSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"status": "Please Provide an email address"},status = status.HTTP_400_BAD_REQUEST)


class SignUpOTP(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        request_email = request.data.get("email",)
        try:
            user = User.objects.get(email__iexact = request_email)
        except:
            return Response({"status": "User is not registered."}, status=status.HTTP_400_BAD_REQUEST)
        if user.is_active is False:
            if request_email:
                try:
                    login_send_otp_email(email=request_email)
                    return Response({'status':'OTP sent successfully.'},status = status.HTTP_200_OK)
                except:
                    return Response({'status':'Given email is not registered.'}, status = status.HTTP_405_METHOD_NOT_ALLOWED)
            else:
                return Response({"status":"Please enter an email id"},status = status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status":"User verified already"},status = status.HTTP_403_FORBIDDEN)
                
class SignUpOTPVerification(APIView):
    permission_classes = [AllowAny]
    def post(self, request):

        request_otp   = request.data.get("otp",)
        request_email = request.data.get("email")
        if request_email:
            try:
                otp_instance = OTP.objects.get(otp_email__iexact = request_email)
                user = User.objects.get(email__iexact = request_email)
            except:
                raise Http404
            
            otp = otp_instance.otp
            email = otp_instance.otp_email

            request_time = OTP.objects.get(otp_email__iexact = request_email).time_created
            current_time = int(time.time())

            if current_time - request_time > 300:
                return Response({"status" : "Sorry, entered OTP has expired."}, status = status.HTTP_403_FORBIDDEN)
            
            if str(request_otp) == str(otp) and request_email == email:
                OTP.objects.filter(otp_email__iexact = request_email).delete()
                user.is_active = True
                user.save()

                return Response(user.tokens(), status=status.HTTP_200_OK)
            else:
                return Response({
                    'status':'OTP incorrect.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
class ChangePassword(APIView):
    permission_classes = (AllowAny, )


    def patch(self, request, *args, **kwargs):
        request_email = request.data.get('email',)
        try:   
            user = User.objects.get(email__iexact = request_email)
        except:
            return Response({"status": "Given User email is not registered." }, 
                                status=status.HTTP_403_FORBIDDEN)
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            if check_password(request.data.get("new_password",), user.password):
                return Response({"status": "New password cannot be the same as old password." }, 
                                status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.data.get("new_password"))
            user.save()
            
            return Response({'status': "New Password Set"},status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)