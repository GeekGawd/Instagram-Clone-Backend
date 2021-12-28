from rest_framework import generics, serializers, status, authentication, permissions
from core.models import *
import time, random
from authentication.serializers import AuthTokenSerializer, ChangePasswordSerializer, UserSerializer
from django.core.mail import EmailMessage
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import Http404
from django.contrib.auth.hashers import check_password
from django.conf import settings
        
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer

class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        request_email = request.data.get('email',)
        try:
            user1 = User.objects.get(email__iexact = request_email)
        except: 
            return Response({'status':'User not registered'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = AuthTokenSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

def login_send_otp_email(email,subject="[OTP] New Login for Connect App"):
    
        OTP.objects.filter(otp_email__iexact = email).delete()

        otp = random.randint(100000,999999)

        msg = EmailMessage(subject, f'<div style="font-family: Helvetica,Arial,sans-serif;min-width:1000px;overflow:auto;line-height:2"><div style="margin:50px auto;width:70%;padding:20px 0"><div style="border-bottom:1px solid #eee"><a href="" style="font-size:2em;color: #FFD243;text-decoration:none;font-weight:600">Connect</a></div><p style="font-size:1.2em">Greetings,</p><p style="font-size:1.2em"> Thank you for creating an account on Connect. You can count on us for quality, service, and selection. Now, we would not like to hold you up, so use the following OTP to complete your Sign Up procedures and order away.<br><b style="text-align: center;display: block;">Note: OTP is only valid for 5 minutes.</b></p><h2 style="font-size: 1.9em;background: #FFD243;margin: 0 auto;width: max-content;padding: 0 15px;color: #fff;border-radius: 4px;">{otp}</h2><p style="font-size:1.2em;">Regards,<br/>Team Connect</p><hr style="border:none;border-top:1px solid #eee" /><div style="float:right;padding:8px 0;color:#aaa;font-size:1.2em;line-height:1;font-weight:500"><p>Connect</p><p>Boys Hostel, Near Girl Hostel AKGEC</p><p>Ghaziabad</p></div></div></div>', 'swaad.info.contact@gmail.com', (email,))
        msg.content_subtype = "html"
        msg.send()

        time_created = int(time.time())
        OTP.objects.create(otp=otp, otp_email = email, time_created = time_created)
        
        return Response({"OTP has been successfully sent to your email."})

def send_otp_email(email,subject):
    
    OTP.objects.filter(otp_email__iexact = email).delete()

    otp = random.randint(100000,999999)

    msg = EmailMessage(subject, f'<div style="font-family: Helvetica,Arial,sans-serif;min-width:1000px;overflow:auto;line-height:2"><div style="margin:50px auto;width:70%;padding:20px 0"><div style="border-bottom:1px solid #eee"><a href="" style="font-size:2em;color: #FFD243;text-decoration:none;font-weight:600">Connect</a></div><p style="font-size:1.2em">Greetings,</p><p style="font-size:1.2em"> Looks like you forgot your password. No worries we are here to help you recover your account. Use the following OTP to recover your account and start ordering the delicacies again in no time. <br><b style="text-align: center;display: block;">Note: OTP is only valid for 5 minutes.</b></p><h2 style="font-size: 1.9em;background: #FFD243;margin: 0 auto;width: max-content;padding: 0 15px;color: #fff;border-radius: 4px;">{otp}</h2><p style="font-size:1.2em;">Regards,<br/>Team Connect</p><hr style="border:none;border-top:1px solid #eee" /><div style="float:right;padding:8px 0;color:#aaa;font-size:1.2em;line-height:1;font-weight:500"><p>Connect</p><p>Boys Hostel, Near Girl Hostel AKGEC</p><p>Ghaziabad</p></div></div></div>' , 'swaad.info.contact@gmail.com', (email,))
    msg.content_subtype = "html"
    msg.send()

    time_created = int(time.time())

    OTP.objects.create(otp=otp, otp_email = email, time_created = time_created)

class PasswordResetOTP(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        request_email = request.data.get("email", )

        try:
            user = User.objects.get(email__iexact = request_email)
        except: 
            return Response({"status" : "No such account exists"},status = status.HTTP_400_BAD_REQUEST)

        if user.is_active:
            send_otp_email(email = request_email,subject="[OTP] Password Change for Connect App") 
            return Response({"status" : "OTP has been sent to your email."}, status = status.HTTP_200_OK)
        return Response({"status": "Please verify your account."}, status=status.HTTP_406_NOT_ACCEPTABLE)


class PasswordResetOTPConfirm(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        request_otp   = request.data.get("otp",)
        request_email = request.data.get("email",)

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
            
            return Response({"status": "OTP has been verified."}, status=status.HTTP_200_OK)

        return Response({"status": "Please Provide an email address"},status = status.HTTP_400_BAD_REQUEST)


class SignUpOTP(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        request_email = request.data.get("email",)
        try:
            user = User.objects.get(email__iexact = request_email)
            return Response({"status": "User is already registered."}, status=status.HTTP_403_FORBIDDEN)
        except:
            if request_email:
                try:
                    login_send_otp_email(email=request_email)
                    return Response({'status':'OTP sent successfully.'},status = status.HTTP_200_OK)
                except:
                    return Response({'status':"Couldn't send otp."}, status = status.HTTP_405_METHOD_NOT_ALLOWED)
            else:
                return Response({"status":"Please enter an email id"},status = status.HTTP_400_BAD_REQUEST)
                
class SignUpOTPVerification(APIView):
    permission_classes = [AllowAny]
    def post(self, request):

        request_otp   = request.data.get("otp",)
        request_email = request.data.get("email")
        if request_email:
            try:
                otp_instance = OTP.objects.get(otp_email__iexact = request_email)
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
            return Response({"status": "Email Verified."}, status=status.HTTP_200_OK)
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