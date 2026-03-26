from rest_framework import serializers

from audit.models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for exposing audit log entries via the API.

    No additional validation or logging is required here because
    this serializer is read-only and simply reflects stored audit
    information.
    """
    class Meta:
        model = AuditLog
        fields = ["id", "timestamp", "action", "user_identifier", "details"]
