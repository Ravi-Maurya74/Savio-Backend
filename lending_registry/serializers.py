from rest_framework import serializers
from lending_registry.models import LendingRegistry
from user.serializers import UserSerialzer as UserSerializer
from user.models import User


class LendingRegistryCreateSerializer(serializers.ModelSerializer):
    """Serializer for the lending registry object"""

    borrower = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    lender = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = LendingRegistry
        fields = (
            "id",
            "lender",
            "borrower",
            "amount",
            "create_date",
        )
        extra_kwargs = {"id": {"read_only": True}}

    def validate(self, attrs):
        user = self.context["request"].user
        borrower = attrs["borrower"]
        lender = attrs["lender"]

        if user != borrower and user != lender:
            raise serializers.ValidationError(
                "You must be either the lender or the borrower to create a lending registry."
            )

        return super().validate(attrs)


class LendingRegistrySerializer(serializers.ModelSerializer):
    """Serializer for the lending registry object"""

    lender = UserSerializer(read_only=True)
    borrower = UserSerializer(read_only=True)
    initiated_by = UserSerializer(read_only=True)
    cleared_by = UserSerializer(read_only=True)

    class Meta:
        model = LendingRegistry
        fields = (
            "id",
            "lender",
            "borrower",
            "initiated_by",
            "cleared_by",  # add manually
            "amount",
            "create_date",
            "clear_date",
            "status",
        )

    extra_kwargs = {"id": {"read_only": True}}


# Lending Registry Serializer to accept initiate request. Should contain urls to accept and reject the request.


class AcceptLendingRegistrySerializer(serializers.ModelSerializer):
    """Serializer for the lending registry object"""

    lender = UserSerializer(read_only=True)
    borrower = UserSerializer(read_only=True)
    initiated_by = UserSerializer(read_only=True)
    cleared_by = UserSerializer(read_only=True)

    accept_url = serializers.HyperlinkedIdentityField(
        view_name="accept_initiate_request",
        lookup_field="id",
        lookup_url_kwarg="pk",
    )
    # reject_url = serializers.HyperlinkedIdentityField(
    #     view_name="reject_initiate_request"
    # )

    class Meta:
        model = LendingRegistry
        fields = (
            "id",
            "lender",
            "borrower",
            "initiated_by",
            "cleared_by",  # add manually
            "amount",
            "create_date",
            "clear_date",
            "status",
            "accept_url",
            # "reject_url",
        )

    extra_kwargs = {"id": {"read_only": True}}
