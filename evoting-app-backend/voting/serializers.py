from rest_framework import serializers

from core.logging_config import build_log_extra, get_logger


class CastVoteItemSerializer(serializers.Serializer):
    poll_position_id = serializers.IntegerField()
    candidate_id = serializers.IntegerField(required=False, allow_null=True, default=None)
    abstain = serializers.BooleanField(default=False)


class CastVoteSerializer(serializers.Serializer):
    poll_id = serializers.IntegerField()
    votes = CastVoteItemSerializer(many=True)

    def validate_votes(self, value):
        logger = get_logger("evoting.voting.serializers.cast")
        for item in value:
            if item.get("abstain") and item.get("candidate_id"):
                logger.warning(
                    "Invalid vote payload: abstain with candidate selected",
                    extra=build_log_extra(context={"poll_position_id": item.get("poll_position_id")}),
                )
                raise serializers.ValidationError(
                    "Cannot both abstain and select a candidate."
                )
        return value


class VoteHistorySerializer(serializers.Serializer):
    poll_id = serializers.IntegerField()
    poll_title = serializers.CharField()
    poll_status = serializers.CharField()
    election_type = serializers.CharField()
    positions = serializers.ListField()


class PositionResultSerializer(serializers.Serializer):
    position_id = serializers.IntegerField()
    position_title = serializers.CharField()
    max_winners = serializers.IntegerField()
    results = serializers.ListField()
    abstain_count = serializers.IntegerField()
    total_votes = serializers.IntegerField()


class PollResultSerializer(serializers.Serializer):
    poll_id = serializers.IntegerField()
    poll_title = serializers.CharField()
    status = serializers.CharField()
    election_type = serializers.CharField()
    total_votes_cast = serializers.IntegerField()
    total_eligible = serializers.IntegerField()
    turnout_percentage = serializers.FloatField()
    positions = PositionResultSerializer(many=True)


class StationResultSerializer(serializers.Serializer):
    station_id = serializers.IntegerField()
    station_name = serializers.CharField()
    station_location = serializers.CharField()
    registered_voters = serializers.IntegerField()
    voters_voted = serializers.IntegerField()
    turnout_percentage = serializers.FloatField()
    positions = serializers.ListField()