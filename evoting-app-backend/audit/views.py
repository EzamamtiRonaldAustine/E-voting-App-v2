from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdminUser
from audit.serializers import AuditLogSerializer
from audit.services import AuditService
from core.response_formatter import success_response


class AuditLogListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = AuditLogSerializer

    def get_queryset(self):
        qs = AuditService.get_recent(limit=None)

        if action := self.request.query_params.get("action"):
            qs = qs.filter(action=action)
        if user := self.request.query_params.get("user"):
            qs = qs.filter(user_identifier__icontains=user)

        return qs


class AuditActionTypesView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        types = list(AuditService.get_action_types())
        return Response(
            success_response(types, correlation_id=getattr(request, "correlation_id", None))
        )
