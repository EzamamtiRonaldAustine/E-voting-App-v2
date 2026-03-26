from django.contrib.auth import get_user_model
from django.db import transaction

from accounts.models import VoterProfile
from audit.services import AuditService
from elections.models import VotingStation
from core.exceptions import (
    AccountDeactivatedException,
    AccountNotVerifiedException,
    EVotingException,
    InvalidCredentialsException,
    ResourceNotFoundException,
    SystemException,
)
from core.logging_config import build_log_extra, get_logger

User = get_user_model()


class AuthenticationService:
    def __init__(self):
        self._audit = AuditService()
        # Dedicated logger for authentication-related events
        self._logger = get_logger("evoting.accounts.authentication")

    def authenticate_admin(self, username, password):
        """Authenticate an admin user with structured logging and exceptions.

        The view layer is responsible for mapping these exceptions to
        HTTP responses; this method focuses on domain rules.
        """

        try:
            self._logger.info(
                "Admin login attempt",
                extra=build_log_extra(user_identifier=username),
            )
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist as exc:
                # Log and raise a domain-specific exception instead of returning strings.
                self._audit.log("LOGIN_FAILED", username, "Invalid admin credentials")
                self._logger.warning(
                    "Admin user not found", extra=build_log_extra(user_identifier=username)
                )
                raise InvalidCredentialsException() from exc

            if not user.check_password(password):
                self._audit.log("LOGIN_FAILED", username, "Wrong password")
                self._logger.warning(
                    "Invalid admin password", extra=build_log_extra(user_identifier=username)
                )
                raise InvalidCredentialsException()

            if not user.is_admin_user:
                self._audit.log("LOGIN_FAILED", username, "Not an admin account")
                self._logger.warning(
                    "Login with non-admin account",
                    extra=build_log_extra(user_identifier=username),
                )
                raise InvalidCredentialsException("This is not an admin account")

            if not user.is_active:
                self._audit.log("LOGIN_FAILED", username, "Account deactivated")
                self._logger.warning(
                    "Deactivated admin account login attempt",
                    extra=build_log_extra(user_identifier=username),
                )
                raise AccountDeactivatedException()

            self._audit.log("LOGIN", username, "Admin login successful")
            self._logger.info(
                "Admin login successful", extra=build_log_extra(user_identifier=username)
            )
            return user
        except EVotingException:
            # Let the caller map domain exceptions to appropriate responses.
            raise
        except Exception as exc:  # pragma: no cover - defensive
            self._logger.error(
                "Unexpected error during admin authentication: %s",
                exc,
                exc_info=True,
                extra=build_log_extra(user_identifier=username),
            )
            raise SystemException("Failed to authenticate admin user") from exc

    def authenticate_voter(self, voter_card_number, password):
        """Authenticate a voter with structured logging and exceptions."""

        try:
            self._logger.info(
                "Voter login attempt",
                extra=build_log_extra(user_identifier=voter_card_number),
            )
            try:
                profile = VoterProfile.objects.select_related("user").get(
                    voter_card_number=voter_card_number
                )
            except VoterProfile.DoesNotExist as exc:
                self._audit.log("LOGIN_FAILED", voter_card_number, "Invalid voter credentials")
                self._logger.warning(
                    "Voter profile not found",
                    extra=build_log_extra(user_identifier=voter_card_number),
                )
                raise InvalidCredentialsException(
                    "Invalid voter card number or password."
                ) from exc

            user = profile.user

            if not user.check_password(password):
                self._audit.log("LOGIN_FAILED", voter_card_number, "Invalid voter credentials")
                self._logger.warning(
                    "Invalid voter password",
                    extra=build_log_extra(user_identifier=voter_card_number),
                )
                raise InvalidCredentialsException(
                    "Invalid voter card number or password."
                )

            if not user.is_active:
                self._audit.log(
                    "LOGIN_FAILED", voter_card_number, "Voter account deactivated"
                )
                self._logger.warning(
                    "Deactivated voter account login attempt",
                    extra=build_log_extra(user_identifier=voter_card_number),
                )
                raise AccountDeactivatedException("This voter account has been deactivated.")

            if not user.is_verified:
                self._audit.log("LOGIN_FAILED", voter_card_number, "Voter not verified")
                self._logger.warning(
                    "Unverified voter login attempt",
                    extra=build_log_extra(user_identifier=voter_card_number),
                )
                raise AccountNotVerifiedException(
                    "Your registration has not been verified yet."
                )

            self._audit.log("LOGIN", voter_card_number, "Voter login successful")
            self._logger.info(
                "Voter login successful",
                extra=build_log_extra(user_identifier=voter_card_number),
            )
            return user
        except EVotingException:
            raise
        except Exception as exc:  # pragma: no cover - defensive
            self._logger.error(
                "Unexpected error during voter authentication: %s",
                exc,
                exc_info=True,
                extra=build_log_extra(user_identifier=voter_card_number),
            )
            raise SystemException("Failed to authenticate voter") from exc


class VoterRegistrationService:
    def __init__(self):
        self._audit = AuditService()
        self._logger = get_logger("evoting.accounts.registration")

    def register(self, validated_data):
        """Register a new voter and log key events for auditing."""

        try:
            voter_full_name = validated_data["full_name"]
            self._logger.info(
                "Voter registration attempt",
                extra=build_log_extra(
                    user_identifier=validated_data.get("email"),
                    context={"full_name": voter_full_name},
                ),
            )

            names = voter_full_name.split(" ", 1)
            try:
                station = VotingStation.objects.get(pk=validated_data["station_id"])
            except VotingStation.DoesNotExist as exc:
                self._logger.warning(
                    "Registration with invalid station id",
                    extra=build_log_extra(context={"station_id": validated_data["station_id"]}),
                )
                raise ResourceNotFoundException("Invalid or inactive voting station.") from exc

            user = User.objects.create_user(
                username=validated_data["email"],
                email=validated_data["email"],
                password=validated_data["password"],
                first_name=names[0],
                last_name=names[1] if len(names) > 1 else "",
                role=User.Role.VOTER,
                is_verified=False,
            )

            profile = VoterProfile.objects.create(
                user=user,
                national_id=validated_data["national_id"],
                date_of_birth=validated_data["date_of_birth"],
                gender=validated_data["gender"],
                address=validated_data["address"],
                phone=validated_data["phone"],
                station=station,
            )

            self._audit.log(
                "REGISTER",
                voter_full_name,
                f"New voter registered with card: {profile.voter_card_number}",
            )
            self._logger.info(
                "Voter registration successful",
                extra=build_log_extra(
                    user_identifier=validated_data.get("email"),
                    context={"voter_card_number": profile.voter_card_number},
                ),
            )
            return profile
        except EVotingException:
            raise
        except Exception as exc:  # pragma: no cover - defensive
            self._logger.error("Unexpected error during voter registration: %s", exc, exc_info=True)
            raise SystemException("Failed to register voter") from exc


class AdminManagementService:
    def __init__(self):
        self._audit = AuditService()
        self._logger = get_logger("evoting.accounts.admin_management")

    @transaction.atomic
    def create_admin(self, validated_data, created_by):
        """Create a new admin user with audit and error handling."""

        try:
            names = validated_data["full_name"].split(" ", 1)
            user = User.objects.create_user(
                username=validated_data["username"],
                email=validated_data["email"],
                password=validated_data["password"],
                first_name=names[0],
                last_name=names[1] if len(names) > 1 else "",
                role=validated_data["role"],
                is_verified=True,
                is_staff=True,
            )
            self._audit.log(
                "CREATE_ADMIN",
                created_by.username,
                f"Created admin: {user.username} (Role: {user.role})",
            )
            self._logger.info(
                "Admin created",
                extra=build_log_extra(
                    user_identifier=created_by.username,
                    context={"admin_username": user.username, "role": user.role},
                ),
            )
            return user
        except Exception as exc:  # pragma: no cover - defensive
            self._logger.error("Unexpected error creating admin: %s", exc, exc_info=True)
            raise SystemException("Failed to create admin user") from exc

    def deactivate(self, admin_id, deactivated_by):
        """Deactivate an admin account with logging for traceability."""

        try:
            admin_user = User.objects.get(pk=admin_id)
        except User.DoesNotExist as exc:
            self._logger.warning(
                "Attempt to deactivate missing admin",
                extra=build_log_extra(context={"admin_id": admin_id}),
            )
            raise ResourceNotFoundException("Admin user not found") from exc

        admin_user.is_active = False
        admin_user.save(update_fields=["is_active"])
        self._audit.log(
            "DEACTIVATE_ADMIN",
            deactivated_by.username,
            f"Deactivated admin: {admin_user.username}",
        )
        self._logger.info(
            "Admin deactivated",
            extra=build_log_extra(
                user_identifier=deactivated_by.username,
                context={"admin_username": admin_user.username},
            ),
        )
        return admin_user


class VoterManagementService:
    def __init__(self):
        self._audit = AuditService()
        self._logger = get_logger("evoting.accounts.voter_management")

    def verify(self, voter_id, verified_by):
        """Verify a single voter with audit and error handling."""

        try:
            user = User.objects.get(pk=voter_id)
        except User.DoesNotExist as exc:
            self._logger.warning(
                "Attempt to verify missing voter",
                extra=build_log_extra(context={"voter_id": voter_id}),
            )
            raise ResourceNotFoundException("Voter not found") from exc

        user.is_verified = True
        user.save(update_fields=["is_verified"])
        self._audit.log(
            "VERIFY_VOTER",
            verified_by.username,
            f"Verified voter: {user.get_full_name()}",
        )
        self._logger.info(
            "Voter verified",
            extra=build_log_extra(
                user_identifier=verified_by.username,
                context={"voter_id": user.id},
            ),
        )
        return user

    def verify_all_pending(self, verified_by):
        """Verify all unverified voters in a bulk operation."""

        unverified_queryset = User.objects.filter(is_verified=False)
        count_verified = unverified_queryset.update(is_verified=True)
        self._audit.log(
            "VERIFY_ALL_VOTERS",
            verified_by.username,
            f"Verified {count_verified} voters",
        )
        self._logger.info(
            "Bulk voter verification completed",
            extra=build_log_extra(
                user_identifier=verified_by.username,
                context={"verified_count": count_verified},
            ),
        )
        return count_verified

    def deactivate(self, voter_id, deactivated_by):
        """Deactivate a voter account with proper logging."""

        try:
            user = User.objects.get(pk=voter_id, role=User.Role.VOTER)
        except User.DoesNotExist as exc:
            self._logger.warning(
                "Attempt to deactivate missing voter",
                extra=build_log_extra(context={"voter_id": voter_id}),
            )
            raise ResourceNotFoundException("Voter not found") from exc

        user.is_active = False
        user.save(update_fields=["is_active"])
        self._audit.log(
            "DEACTIVATE_VOTER",
            deactivated_by.username,
            f"Deactivated voter: {user.get_full_name()}",
        )
        self._logger.info(
            "Voter deactivated",
            extra=build_log_extra(
                user_identifier=deactivated_by.username,
                context={"voter_id": user.id},
            ),
        )
        return user

    def search(self, query_params):
        qs = User.objects.filter(role=User.Role.VOTER).select_related("voter_profile")

        if name := query_params.get("name"):
            qs = qs.filter(first_name__icontains=name) | qs.filter(last_name__icontains=name)
        if card := query_params.get("card"):
            qs = qs.filter(voter_profile__voter_card_number=card)
        if nid := query_params.get("national_id"):
            qs = qs.filter(voter_profile__national_id=nid)
        if station_id := query_params.get("station_id"):
            qs = qs.filter(voter_profile__station_id=station_id)

        return qs