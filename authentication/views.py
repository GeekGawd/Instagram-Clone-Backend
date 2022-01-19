from rest_framework import generics, serializers, status, mixins
from core.models import *
import time, random
from authentication.serializers import AuthTokenSerializer, ChangePasswordSerializer, CreateUsernameSerializer, UserSerializer
from django.core.mail import EmailMessage
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import Http404
from django.contrib.auth.hashers import check_password
from django.conf import settings
from django.core.exceptions import BadRequest, ObjectDoesNotExist
from authentication.tasks import send_login_mail, send_otp_email
        
class CreateUserView(generics.GenericAPIView, mixins.CreateModelMixin):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        email = request.data.get("email")
        try:
            profile = Profile.objects.get(username=username)
            return Response({"status": "Username already Taken."}, status=status.HTTP_409_CONFLICT)    
            # else:
            #     serializer = self.serializer_class(data=request.data)
            #     if serializer.is_valid(raise_exception=True):
            #         user = serializer.save()
            #     profile.user = user
            #     profile.save()
            #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ObjectDoesNotExist:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=True):
                    user = serializer.save()
            profile = Profile.objects.create(username=username, user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

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

class PasswordResetOTP(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        request_email = request.data.get("email", )

        try:
            user = User.objects.get(email__iexact = request_email)
        except:
            return Response({"status" : "No such account exists"},status = status.HTTP_400_BAD_REQUEST)

        if user.is_active:
            send_otp_email.delay(request_email,"[OTP] Password Change for Connect App")
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
                    send_login_mail.delay(request_email, "[OTP] New Login for Connect App")
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
            return Response(user.tokens(),status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED) 

class CreateUsername(APIView):

    def post(self, request, *args, **kwargs):
        username = request.data.get("username",)
        try:
            Profile.objects.get(username=username)
            return Response({"status": "Username already taken"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"username": f"{username}"}, status=status.HTTP_201_CREATED)
