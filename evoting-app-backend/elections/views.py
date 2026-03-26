from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdminOrReadOnlyVoter, IsAdminUser
from core.exceptions import BusinessRuleException, EVotingException, ResourceNotFoundException
from core.logging_config import get_logger
from core.response_formatter import error_response_from_exception, success_response
from elections.models import Candidate, Poll, Position, VotingStation
from elections.serializers import (
    AssignCandidatesSerializer,
    CandidateCreateSerializer,
    CandidateSerializer,
    CandidateUpdateSerializer,
    PollCreateSerializer,
    PollSerializer,
    PollUpdateSerializer,
    PositionCreateSerializer,
    PositionSerializer,
    VotingStationCreateSerializer,
    VotingStationSerializer,
)
from elections.services import (
    CandidateService,
    PollService,
    PositionService,
    VotingStationService,
)


class CandidateListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnlyVoter]

    def get_queryset(self):
        service = CandidateService()
        return service.search(self.request.query_params)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CandidateCreateSerializer
        return CandidateSerializer

    def perform_create(self, serializer):
        service = CandidateService()
        service.create(serializer.validated_data, self.request.user)


class CandidateDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAdminOrReadOnlyVoter]
    queryset = Candidate.objects.all()

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return CandidateUpdateSerializer
        return CandidateSerializer

    def perform_update(self, serializer):
        service = CandidateService()
        service.update(self.get_object(), serializer.validated_data, self.request.user)


class CandidateDeactivateView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        service = CandidateService()
        correlation_id = getattr(request, "correlation_id", None)
        try:
            service.deactivate(pk, request.user)
        except ResourceNotFoundException as exc:
            return Response(
                error_response_from_exception(exc, correlation_id=correlation_id),
                status=status.HTTP_404_NOT_FOUND,
            )
        except BusinessRuleException as exc:
            return Response(
                error_response_from_exception(exc, correlation_id=correlation_id),
                status=status.HTTP_400_BAD_REQUEST,
            )
        payload = {"message": "Candidate deactivated."}
        return Response(success_response(payload, correlation_id=correlation_id))


class VotingStationListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnlyVoter]
    queryset = VotingStation.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return VotingStationCreateSerializer
        return VotingStationSerializer

    def perform_create(self, serializer):
        service = VotingStationService()
        service.create(serializer.validated_data, self.request.user)


class VotingStationDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAdminOrReadOnlyVoter]
    queryset = VotingStation.objects.all()
    serializer_class = VotingStationSerializer

    def perform_update(self, serializer):
        service = VotingStationService()
        service.update(self.get_object(), serializer.validated_data, self.request.user)


class VotingStationDeactivateView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        service = VotingStationService()
        correlation_id = getattr(request, "correlation_id", None)
        try:
            service.deactivate(pk, request.user)
        except ResourceNotFoundException as exc:
            return Response(
                error_response_from_exception(exc, correlation_id=correlation_id),
                status=status.HTTP_404_NOT_FOUND,
            )
        payload = {"message": "Station deactivated."}
        return Response(success_response(payload, correlation_id=correlation_id))


class PositionListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnlyVoter]
    queryset = Position.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PositionCreateSerializer
        return PositionSerializer

    def perform_create(self, serializer):
        service = PositionService()
        service.create(serializer.validated_data, self.request.user)


class PositionDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAdminOrReadOnlyVoter]
    queryset = Position.objects.all()

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return PositionCreateSerializer
        return PositionSerializer

    def perform_update(self, serializer):
        service = PositionService()
        service.update(self.get_object(), serializer.validated_data, self.request.user)


class PositionDeactivateView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        service = PositionService()
        correlation_id = getattr(request, "correlation_id", None)
        try:
            service.deactivate(pk, request.user)
        except ResourceNotFoundException as exc:
            return Response(
                error_response_from_exception(exc, correlation_id=correlation_id),
                status=status.HTTP_404_NOT_FOUND,
            )
        except BusinessRuleException as exc:
            return Response(
                error_response_from_exception(exc, correlation_id=correlation_id),
                status=status.HTTP_400_BAD_REQUEST,
            )
        payload = {"message": "Position deactivated."}
        return Response(success_response(payload, correlation_id=correlation_id))


class PollListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnlyVoter]
    queryset = Poll.objects.all()
    serializer_class = PollSerializer

    def create(self, request, *args, **kwargs):
        serializer = PollCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = PollService()
        correlation_id = getattr(request, "correlation_id", None)
        try:
            poll = service.create(serializer.validated_data, request.user)
        except EVotingException as exc:
            return Response(
                error_response_from_exception(exc, correlation_id=correlation_id),
                status=status.HTTP_400_BAD_REQUEST,
            )
        payload = PollSerializer(poll).data
        return Response(
            success_response(payload, correlation_id=correlation_id),
            status=status.HTTP_201_CREATED,
        )


class PollDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAdminOrReadOnlyVoter]
    queryset = Poll.objects.prefetch_related(
        "poll_positions__position",
        "poll_positions__candidates",
        "stations",
    ).all()
    serializer_class = PollSerializer


class PollUpdateView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        try:
            poll = Poll.objects.get(pk=pk)
        except Poll.DoesNotExist:
            return Response({"detail": "Poll not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PollUpdateSerializer(poll, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        service = PollService()
        correlation_id = getattr(request, "correlation_id", None)
        try:
            service.update(poll, serializer.validated_data, request.user)
        except BusinessRuleException as exc:
            return Response(
                error_response_from_exception(exc, correlation_id=correlation_id),
                status=status.HTTP_400_BAD_REQUEST,
            )
        payload = PollSerializer(poll).data
        return Response(success_response(payload, correlation_id=correlation_id))


class PollDeleteView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, pk):
        service = PollService()
        correlation_id = getattr(request, "correlation_id", None)
        try:
            service.delete(pk, request.user)
        except ResourceNotFoundException as exc:
            return Response(
                error_response_from_exception(exc, correlation_id=correlation_id),
                status=status.HTTP_404_NOT_FOUND,
            )
        except BusinessRuleException as exc:
            return Response(
                error_response_from_exception(exc, correlation_id=correlation_id),
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class PollToggleStatusView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        action = request.data.get("action")
        if action not in ("open", "close"):
            return Response(
                {"detail": "Action must be 'open' or 'close'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        service = PollService()
        correlation_id = getattr(request, "correlation_id", None)
        try:
            poll = service.toggle_status(pk, action, request.user)
        except ResourceNotFoundException as exc:
            return Response(
                error_response_from_exception(exc, correlation_id=correlation_id),
                status=status.HTTP_404_NOT_FOUND,
            )
        except BusinessRuleException as exc:
            return Response(
                error_response_from_exception(exc, correlation_id=correlation_id),
                status=status.HTTP_400_BAD_REQUEST,
            )
        payload = PollSerializer(poll).data
        return Response(success_response(payload, correlation_id=correlation_id))


class AssignCandidatesView(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = AssignCandidatesSerializer

    def post(self, request):
        serializer = AssignCandidatesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = PollService()
        correlation_id = getattr(request, "correlation_id", None)
        try:
            poll_position = service.assign_candidates(
                serializer.validated_data["poll_position_id"],
                serializer.validated_data["candidate_ids"],
                request.user,
            )
        except ResourceNotFoundException as exc:
            return Response(
                error_response_from_exception(exc, correlation_id=correlation_id),
                status=status.HTTP_404_NOT_FOUND,
            )
        except BusinessRuleException as exc:
            return Response(
                error_response_from_exception(exc, correlation_id=correlation_id),
                status=status.HTTP_400_BAD_REQUEST,
            )
        payload = {
            "message": f"Candidates assigned to {poll_position.position.title}.",
            "candidate_count": poll_position.candidates.count(),
        }
        return Response(success_response(payload, correlation_id=correlation_id))