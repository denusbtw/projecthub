from rest_framework import serializers

from projecthub.tasks.models import Board


class BaseBoardReadSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    order = serializers.IntegerField()


class BoardListSerializer(BaseBoardReadSerializer):
    pass


class BoardDetailSerializer(BaseBoardReadSerializer):
    pass


class BoardCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ("id", "name", "order")

    def validate(self, attrs):
        project = self.context["project"]
        if project.is_archived:
            raise serializers.ValidationError(
                "Can't create board for archived project."
            )
        return attrs


class BoardUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ("name", "order")
        extra_kwargs = {
            "name": {"required": False},
            "order": {"required": False},
        }
