from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.permissions import IsAdminUser, IsSuperAdmin
from accounts.serializers import (
    AdminCreateSerializer,
    AdminListSerializer,
    AdminLoginSerializer,
    ChangePasswordSerializer,
    UserSerializer,
    VoterListSerializer,
    VoterLoginSerializer,
    VoterProfileSerializer,
    VoterRegistrationSerializer,
)
from accounts.services import (
    AdminManagementService,
    AuthenticationService,
    VoterManagementService,
    VoterRegistrationService,
)
from core.exceptions import (
    AccountDeactivatedException,
    AccountNotVerifiedException,
    EVotingException,
    InvalidCredentialsException,
    ResourceNotFoundException,
    SystemException,
)
from core.logging_config import get_logger
from core.response_formatter import error_response_from_exception, success_response

User = get_user_model()


class AdminLoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = AdminLoginSerializer

    def post(self, request):
        """Handle admin login with structured error handling and logging."""

        correlation_id = getattr(request, "correlation_id", None)
        logger = get_logger("evoting.accounts.views.admin_login")

        serializer = AdminLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = AuthenticationService()
        try:
            user = service.authenticate_admin(
                serializer.validated_data["username"],
                serializer.validated_data["password"],
            )
        except InvalidCredentialsException as exc:
            logger.warning("Invalid admin credentials")
            return Response(
                error_response_from_exception(exc, correlation_id=correlation_id),
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except AccountDeactivatedException as exc:
            logger.warning("Deactivated admin account login attempt")
            return Response(
                error_response_from_exception(exc, correlation_id=correlation_id),
                status=status.HTTP_403_FORBIDDEN,
            )
        except EVotingException as exc:
            # Fallback for any other domain exception
            logger.error("Admin login failed due to domain error: %s", exc)
            return Response(
                error_response_from_exception(exc, correlation_id=correlation_id),
                status=status.HTTP_400_BAD_REQUEST,
            )
        except SystemException as exc:
            logger.error("Admin login failed due to system error", exc_info=True)
            return Response(
                error_response_from_exception(exc, correlation_id=correlation_id),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        refresh = RefreshToken.for_user(user)
        payload = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "full_name": user.get_full_name(),
                "role": user.role,
            },
        }
        return Response(
            success_response(payload, correlation_id=correlation_id),
            status=status.HTTP_200_OK,
        )


class VoterLoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = VoterLoginSerializer

    def post(self, request):
        """Handle voter login and translate domain errors to HTTP responses."""

        correlation_id = getattr(request, "correlation_id", None)
        logger = get_logger("evoting.accounts.views.voter_login")

        serializer = VoterLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = AuthenticationService()
        try:
            user = service.authenticate_voter(
                serializer.validated_data["voter_card_number"],
                serializer.validated_data["password"],
            )
        except InvalidCredentialsException as exc:
            logger.warning("Invalid voter credentials")
            return Response(
                error_response_from_exception(exc, correlation_id=correlation_id),
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except AccountDeactivatedException as exc:
            logger.warning("Deactivated voter attempted login")
            return Response(
                error_response_from_exception(exc, correlation_id=correlation_id),
                status=status.HTTP_403_FORBIDDEN,
            )
        except AccountNotVerifiedException as exc:
            logger.warning("Unverified voter attempted login")
            return Response(
                error_response_from_exception(exc, correlation_id=correlation_id),
                status=status.HTTP_403_FORBIDDEN,
            )
        except EVotingException as exc:
            logger.error("Voter login failed due to domain error: %s", exc)
            return Response(
                error_response_from_exception(exc, correlation_id=correlation_id),
                status=status.HTTP_400_BAD_REQUEST,
            )
        except SystemException as exc:
            logger.error("Voter login failed due to system error", exc_info=True)
            return Response(
                error_response_from_exception(exc, correlation_id=correlation_id),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        refresh = RefreshToken.for_user(user)
        payload = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "full_name": user.get_full_name(),
                "voter_card_number": user.voter_profile.voter_card_number,
                "role": user.role,
            },
        }
        return Response(
            success_response(payload, correlation_id=correlation_id),
            status=status.HTTP_200_OK,
        )


class VoterRegistrationView(APIView):
    permission_classes = [AllowAny]
    serializer_class = VoterRegistrationSerializer

    def post(self, request):
        correlation_id = getattr(request, "correlation_id", None)
        logger = get_logger("evoting.accounts.views.registration")

        serializer = VoterRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = VoterRegistrationService()
        try:
            profile = service.register(serializer.validated_data)
        except EVotingException as exc:
            logger.warning("Voter registration failed due to domain error: %s", exc)
            return Response(
                error_response_from_exception(exc, correlation_id=correlation_id),
                status=status.HTTP_400_BAD_REQUEST,
            )
        except SystemException as exc:
            logger.error("Voter registration failed due to system error", exc_info=True)
            return Response(
                error_response_from_exception(exc, correlation_id=correlation_id),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        payload = {
            "message": "Registration successful. Pending admin verification.",
            "voter_card_number": profile.voter_card_number,
        }
        return Response(
            success_response(payload, correlation_id=correlation_id),
            status=status.HTTP_201_CREATED,
        )


class VoterProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = VoterProfileSerializer(request.user.voter_profile)
        return Response(serializer.data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not request.user.check_password(serializer.validated_data["current_password"]):
            # Keep response minimal but structured
            exc = EVotingException(
                message="Incorrect current password.", code="INVALID_PASSWORD"
            )
            return Response(
                error_response_from_exception(
                    exc, correlation_id=getattr(request, "correlation_id", None)
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()
        payload = {"message": "Password changed successfully."}
        return Response(
            success_response(payload, correlation_id=getattr(request, "correlation_id", None))
        )


class VoterListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = VoterListSerializer

    def get_queryset(self):
        service = VoterManagementService()
        return service.search(self.request.query_params)


class VoterVerifyView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        service = VoterManagementService()
        correlation_id = getattr(request, "correlation_id", None)
        try:
            service.verify(pk, request.user)
        except ResourceNotFoundException as exc:
            return Response(
                error_response_from_exception(exc, correlation_id=correlation_id),
                status=status.HTTP_404_NOT_FOUND,
            )
        payload = {"message": "Voter verified successfully."}
        return Response(success_response(payload, correlation_id=correlation_id))


class VoterVerifyAllView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        service = VoterManagementService()
        count = service.verify_all_pending(request.user)
        payload = {"message": f"{count} voters verified."}
        return Response(
            success_response(payload, correlation_id=getattr(request, "correlation_id", None))
        )


class VoterDeactivateView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        service = VoterManagementService()
        correlation_id = getattr(request, "correlation_id", None)
        try:
            service.deactivate(pk, request.user)
        except ResourceNotFoundException as exc:
            return Response(
                error_response_from_exception(exc, correlation_id=correlation_id),
                status=status.HTTP_404_NOT_FOUND,
            )
        payload = {"message": "Voter deactivated."}
        return Response(success_response(payload, correlation_id=correlation_id))


class AdminListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = AdminListSerializer

    def get_queryset(self):
        return User.objects.filter(role__in=User.ADMIN_ROLES).order_by("-date_joined")


class AdminCreateView(APIView):
    permission_classes = [IsSuperAdmin]
    serializer_class = AdminCreateSerializer

    def post(self, request):
        serializer = AdminCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = AdminManagementService()
        correlation_id = getattr(request, "correlation_id", None)
        admin_user = service.create_admin(serializer.validated_data, request.user)

        payload = {
            "message": f"Admin '{admin_user.username}' created with role: {admin_user.role}",
            "id": admin_user.id,
        }
        return Response(
            success_response(payload, correlation_id=correlation_id),
            status=status.HTTP_201_CREATED,
        )


class AdminDeactivateView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request, pk):
        if pk == request.user.pk:
            return Response(
                {
                    "success": False,
                    "error": {
                        "code": "SELF_DEACTIVATION_NOT_ALLOWED",
                        "message": "Cannot deactivate your own account.",
                        "details": {},
                        "correlation_id": getattr(request, "correlation_id", None),
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        service = AdminManagementService()
        correlation_id = getattr(request, "correlation_id", None)
        try:
            service.deactivate(pk, request.user)
        except ResourceNotFoundException as exc:
            return Response(
                error_response_from_exception(exc, correlation_id=correlation_id),
                status=status.HTTP_404_NOT_FOUND,
            )
        payload = {"message": "Admin deactivated."}
        return Response(success_response(payload, correlation_id=correlation_id))