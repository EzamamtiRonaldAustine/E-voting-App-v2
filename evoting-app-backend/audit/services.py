from audit.models import AuditLog
from core.logging_config import build_log_extra, get_logger


class AuditService:
    """Thin service wrapper around the AuditLog model.

    Although this service mostly delegates directly to the ORM, a
    dedicated logger is provided so that failures in audit logging
    can be diagnosed without impacting primary business flows.
    """

    _logger = get_logger("evoting.audit.service")

    @staticmethod
    def log(action, user_identifier, details=""):
        try:
            return AuditLog.objects.create(
                action=action,
                user_identifier=user_identifier,
                details=details,
            )
        except Exception as exc:  # pragma: no cover - defensive
            AuditService._logger.error(
                "Failed to write audit log: %s",
                exc,
                exc_info=True,
                extra=build_log_extra(
                    user_identifier=user_identifier,
                    context={"action": action},
                ),
            )
            # Do not re-raise here to avoid breaking the main flow.
            return None

    @staticmethod
    def get_recent(limit=20):
        return AuditLog.objects.all()[:limit]

    @staticmethod
    def filter_by_action(action_type):
        return AuditLog.objects.filter(action=action_type)

    @staticmethod
    def filter_by_user(user_identifier):
        return AuditLog.objects.filter(user_identifier__icontains=user_identifier)

    @staticmethod
    def get_action_types():
        return (
            AuditLog.objects.values_list("action", flat=True)
            .distinct()
            .order_by("action")
        )
