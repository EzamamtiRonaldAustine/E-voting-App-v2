from django.db import transaction

from audit.services import AuditService
from core.exceptions import BusinessRuleException, EVotingException, ResourceNotFoundException, SystemException
from core.logging_config import build_log_extra, get_logger
from elections.models import Candidate, Poll, PollPosition, Position, VotingStation


class CandidateService:
    def __init__(self):
        self._audit = AuditService()
        self._logger = get_logger("evoting.elections.candidates")

    def create(self, validated_data, created_by):
        """Create a new candidate with audit logging and error handling."""

        try:
            candidate = Candidate.objects.create(created_by=created_by, **validated_data)
            self._audit.log(
                "CREATE_CANDIDATE",
                created_by.username,
                f"Created candidate: {candidate.full_name} (ID: {candidate.id})",
            )
            self._logger.info(
                "Candidate created",
                extra=build_log_extra(
                    user_identifier=created_by.username,
                    context={"candidate_id": candidate.id},
                ),
            )
            return candidate
        except Exception as exc:  # pragma: no cover - defensive
            self._logger.error("Unexpected error creating candidate: %s", exc, exc_info=True)
            raise SystemException("Failed to create candidate") from exc

    def update(self, candidate, validated_data, updated_by):
        """Update an existing candidate with logging for traceability."""

        for field_name, field_value in validated_data.items():
            setattr(candidate, field_name, field_value)
        candidate.save()
        self._audit.log(
            "UPDATE_CANDIDATE",
            updated_by.username,
            f"Updated candidate: {candidate.full_name} (ID: {candidate.id})",
        )
        self._logger.info(
            "Candidate updated",
            extra=build_log_extra(
                user_identifier=updated_by.username,
                context={"candidate_id": candidate.id},
            ),
        )
        return candidate

    def deactivate(self, candidate_id, deleted_by):
        """Soft-delete a candidate with error handling and logging."""

        try:
            candidate = Candidate.objects.get(pk=candidate_id)
        except Candidate.DoesNotExist as exc:
            self._logger.warning(
                "Attempt to deactivate missing candidate",
                extra=build_log_extra(context={"candidate_id": candidate_id}),
            )
            raise ResourceNotFoundException("Candidate not found") from exc

        candidate.is_active = False
        candidate.save(update_fields=["is_active"])
        self._audit.log(
            "DELETE_CANDIDATE",
            deleted_by.username,
            f"Deactivated candidate: {candidate.full_name} (ID: {candidate.id})",
        )
        self._logger.info(
            "Candidate deactivated",
            extra=build_log_extra(
                user_identifier=deleted_by.username,
                context={"candidate_id": candidate.id},
            ),
        )
        return candidate

    def search(self, query_params):
        qs = Candidate.objects.all()
        if name := query_params.get("name"):
            qs = qs.filter(full_name__icontains=name)
        if party := query_params.get("party"):
            qs = qs.filter(party__icontains=party)
        if education := query_params.get("education"):
            qs = qs.filter(education=education)
        if min_age := query_params.get("min_age"):
            qs = [c for c in qs if c.age >= int(min_age)]
            return qs
        if max_age := query_params.get("max_age"):
            qs = [c for c in qs if c.age <= int(max_age)]
            return qs
        return qs


class VotingStationService:
    def __init__(self):
        self._audit = AuditService()
        self._logger = get_logger("evoting.elections.stations")

    def create(self, validated_data, created_by):
        """Create a voting station and record the operation."""

        try:
            station = VotingStation.objects.create(created_by=created_by, **validated_data)
            self._audit.log(
                "CREATE_STATION",
                created_by.username,
                f"Created station: {station.name} (ID: {station.id})",
            )
            self._logger.info(
                "Station created",
                extra=build_log_extra(
                    user_identifier=created_by.username,
                    context={"station_id": station.id},
                ),
            )
            return station
        except Exception as exc:  # pragma: no cover - defensive
            self._logger.error("Unexpected error creating station: %s", exc, exc_info=True)
            raise SystemException("Failed to create station") from exc

    def update(self, station, validated_data, updated_by):
        """Update a station with audit + structured logging."""

        for field_name, field_value in validated_data.items():
            setattr(station, field_name, field_value)
        station.save()
        self._audit.log(
            "UPDATE_STATION",
            updated_by.username,
            f"Updated station: {station.name} (ID: {station.id})",
        )
        self._logger.info(
            "Station updated",
            extra=build_log_extra(
                user_identifier=updated_by.username,
                context={"station_id": station.id},
            ),
        )
        return station

    def deactivate(self, station_id, deleted_by):
        """Deactivate a voting station with consistent error reporting."""

        try:
            station = VotingStation.objects.get(pk=station_id)
        except VotingStation.DoesNotExist as exc:
            self._logger.warning(
                "Attempt to deactivate missing station",
                extra=build_log_extra(context={"station_id": station_id}),
            )
            raise ResourceNotFoundException("Station not found") from exc

        station.is_active = False
        station.save(update_fields=["is_active"])
        self._audit.log(
            "DELETE_STATION",
            deleted_by.username,
            f"Deactivated station: {station.name} (ID: {station.id})",
        )
        self._logger.info(
            "Station deactivated",
            extra=build_log_extra(
                user_identifier=deleted_by.username,
                context={"station_id": station.id},
            ),
        )
        return station


class PositionService:
    def __init__(self):
        self._audit = AuditService()
        self._logger = get_logger("evoting.elections.positions")

    def create(self, validated_data, created_by):
        """Create a position with audit logging."""

        try:
            position = Position.objects.create(created_by=created_by, **validated_data)
            self._audit.log(
                "CREATE_POSITION",
                created_by.username,
                f"Created position: {position.title} (ID: {position.id})",
            )
            self._logger.info(
                "Position created",
                extra=build_log_extra(
                    user_identifier=created_by.username,
                    context={"position_id": position.id},
                ),
            )
            return position
        except Exception as exc:  # pragma: no cover - defensive
            self._logger.error("Unexpected error creating position: %s", exc, exc_info=True)
            raise SystemException("Failed to create position") from exc

    def update(self, position, validated_data, updated_by):
        """Update an existing position with traceable logging."""

        for field_name, field_value in validated_data.items():
            setattr(position, field_name, field_value)
        position.save()
        self._audit.log(
            "UPDATE_POSITION",
            updated_by.username,
            f"Updated position: {position.title} (ID: {position.id})",
        )
        self._logger.info(
            "Position updated",
            extra=build_log_extra(
                user_identifier=updated_by.username,
                context={"position_id": position.id},
            ),
        )
        return position

    def deactivate(self, position_id, deleted_by):
        """Deactivate a position with consistent error reporting."""

        try:
            position = Position.objects.get(pk=position_id)
        except Position.DoesNotExist as exc:
            self._logger.warning(
                "Attempt to deactivate missing position",
                extra=build_log_extra(context={"position_id": position_id}),
            )
            raise ResourceNotFoundException("Position not found") from exc

        position.is_active = False
        position.save(update_fields=["is_active"])
        self._audit.log(
            "DELETE_POSITION",
            deleted_by.username,
            f"Deactivated position: {position.title} (ID: {position.id})",
        )
        self._logger.info(
            "Position deactivated",
            extra=build_log_extra(
                user_identifier=deleted_by.username,
                context={"position_id": position.id},
            ),
        )
        return position


class PollService:
    def __init__(self):
        self._audit = AuditService()
        self._logger = get_logger("evoting.elections.polls")

    @transaction.atomic
    def create(self, validated_data, created_by):
        """Create a poll along with its positions and stations."""

        try:
            poll = Poll.objects.create(
                title=validated_data["title"],
                description=validated_data.get("description", ""),
                election_type=validated_data["election_type"],
                start_date=validated_data["start_date"],
                end_date=validated_data["end_date"],
                status=Poll.Status.DRAFT,
                created_by=created_by,
            )
            poll.stations.set(
                VotingStation.objects.filter(pk__in=validated_data["station_ids"])
            )
            for position_id in validated_data["position_ids"]:
                PollPosition.objects.create(
                    poll=poll,
                    position_id=position_id,
                )
            self._audit.log(
                "CREATE_POLL",
                created_by.username,
                f"Created poll: {poll.title} (ID: {poll.id})",
            )
            self._logger.info(
                "Poll created",
                extra=build_log_extra(
                    user_identifier=created_by.username,
                    context={"poll_id": poll.id},
                ),
            )
            return poll
        except Exception as exc:  # pragma: no cover - defensive
            self._logger.error("Unexpected error creating poll: %s", exc, exc_info=True)
            raise SystemException("Failed to create poll") from exc

    def update(self, poll, validated_data, updated_by):
        """Update poll details when it is not open."""

        if poll.status == Poll.Status.OPEN:
            raise BusinessRuleException("Cannot update an open poll. Close it first.")
        for field_name, field_value in validated_data.items():
            setattr(poll, field_name, field_value)
        poll.save()
        self._audit.log(
            "UPDATE_POLL",
            updated_by.username,
            f"Updated poll: {poll.title} (ID: {poll.id})",
        )
        self._logger.info(
            "Poll updated",
            extra=build_log_extra(
                user_identifier=updated_by.username,
                context={"poll_id": poll.id},
            ),
        )
        return poll

    @transaction.atomic
    def delete(self, poll_id, deleted_by):
        """Delete a poll that is not open for voting."""

        try:
            poll = Poll.objects.get(pk=poll_id)
        except Poll.DoesNotExist as exc:
            self._logger.warning(
                "Attempt to delete missing poll",
                extra=build_log_extra(context={"poll_id": poll_id}),
            )
            raise ResourceNotFoundException("Poll not found") from exc

        if poll.status == Poll.Status.OPEN:
            raise BusinessRuleException("Cannot delete an open poll. Close it first.")

        poll_title = poll.title
        poll.delete()
        self._audit.log(
            "DELETE_POLL",
            deleted_by.username,
            f"Deleted poll: {poll_title}",
        )
        self._logger.info(
            "Poll deleted",
            extra=build_log_extra(
                user_identifier=deleted_by.username,
                context={"poll_title": poll_title},
            ),
        )

    def toggle_status(self, poll_id, action, toggled_by):
        """Open or close a poll with business rule validation."""

        try:
            poll = Poll.objects.prefetch_related("poll_positions__candidates").get(pk=poll_id)
        except Poll.DoesNotExist as exc:
            self._logger.warning(
                "Attempt to toggle missing poll",
                extra=build_log_extra(context={"poll_id": poll_id}),
            )
            raise ResourceNotFoundException("Poll not found") from exc

        if action == "open":
            if poll.status not in (Poll.Status.DRAFT, Poll.Status.CLOSED):
                raise BusinessRuleException(
                    f"Cannot open a poll with status: {poll.status}"
                )
            if poll.status == Poll.Status.DRAFT:
                has_candidates_assigned = any(
                    poll_position.candidates.exists()
                    for poll_position in poll.poll_positions.all()
                )
                if not has_candidates_assigned:
                    raise BusinessRuleException("Cannot open - no candidates assigned.")
            poll.status = Poll.Status.OPEN
            log_action = "OPEN_POLL" if poll.status == Poll.Status.DRAFT else "REOPEN_POLL"
        elif action == "close":
            if poll.status != Poll.Status.OPEN:
                raise BusinessRuleException("Only open polls can be closed.")
            poll.status = Poll.Status.CLOSED
            log_action = "CLOSE_POLL"
        else:
            raise BusinessRuleException(f"Invalid action: {action}")

        poll.save(update_fields=["status"])
        self._audit.log(
            log_action,
            toggled_by.username,
            f"{log_action.replace('_', ' ').title()}: {poll.title}",
        )
        self._logger.info(
            "Poll status toggled",
            extra=build_log_extra(
                user_identifier=toggled_by.username,
                context={"poll_id": poll.id, "new_status": poll.status},
            ),
        )
        return poll

    def assign_candidates(self, poll_position_id, candidate_ids, assigned_by):
        """Assign candidates to a poll position with rule checks."""

        try:
            poll_position = PollPosition.objects.select_related("poll", "position").get(
                pk=poll_position_id
            )
        except PollPosition.DoesNotExist as exc:
            self._logger.warning(
                "Assign candidates to missing poll position",
                extra=build_log_extra(context={"poll_position_id": poll_position_id}),
            )
            raise ResourceNotFoundException("Poll position not found") from exc

        if poll_position.poll.status == Poll.Status.OPEN:
            raise BusinessRuleException("Cannot modify candidates of an open poll.")

        eligible_candidates = Candidate.objects.filter(
            pk__in=candidate_ids,
            is_active=True,
            is_approved=True,
        )
        poll_position.candidates.set(eligible_candidates)

        self._audit.log(
            "ASSIGN_CANDIDATES",
            assigned_by.username,
            f"Assigned {eligible_candidates.count()} candidates to {poll_position.position.title} "
            f"in poll: {poll_position.poll.title}",
        )
        self._logger.info(
            "Candidates assigned to poll position",
            extra=build_log_extra(
                user_identifier=assigned_by.username,
                context={
                    "poll_position_id": poll_position.id,
                    "candidate_count": eligible_candidates.count(),
                },
            ),
        )
        return poll_position