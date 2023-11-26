from rest_framework import serializers
from lending_registry.models import LendingRegistry
from user.serializers import UserSerializer as UserSerializer
from user.models import User


class LendingRegistryCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating lending registry
    """

    borrower = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    lender = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = LendingRegistry
        fields = (
            "id",
            "lender",
            "borrower",
            "amount",
            "description",
            # "create_date",
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


class ActiveLendingRegistrySerializer(serializers.ModelSerializer):
    """
    Serializer for viewing active Lending Registry.
    Also contains link to initiate a clear request.
    """

    lender = UserSerializer(read_only=True)
    borrower = UserSerializer(read_only=True)
    initiated_by = UserSerializer(read_only=True)
    cleared_by = UserSerializer(read_only=True)

    # add hyperlink to initiate clearing request

    initiate_clearing_request_url = serializers.HyperlinkedIdentityField(
        view_name="initiate_clear_request",
        lookup_field="id",
        lookup_url_kwarg="pk",
    )

    class Meta:
        model = LendingRegistry
        fields = "__all__"

    extra_kwargs = {"id": {"read_only": True}}


class ClearedLendingRegistrySerializer(serializers.ModelSerializer):
    """
    Serializer for viewing cleared LendingRegistry.
    All fields are read only. The data can not be chaged now.
    """

    lender = UserSerializer(read_only=True)
    borrower = UserSerializer(read_only=True)
    initiated_by = UserSerializer(read_only=True)
    cleared_by = UserSerializer(read_only=True)

    class Meta:
        model = LendingRegistry
        fields = "__all__"
        # read_only_fields = "__all__"

    extra_kwargs = {"id": {"read_only": True}}

    def get_fields(self):
        fields = super().get_fields()
        for field_name, field in fields.items():
            field.read_only = True
        return fields


# Lending Registry Serializer to accept initiate request. Should contain urls to accept and reject the request.


class AcceptLendingRegistrySerializer(serializers.ModelSerializer):
    """
    Serializer for LendingRegistry of record with initiate request not yet accepted.
    Contains link to accept this record or reject it.
    """

    lender = UserSerializer(read_only=True)
    borrower = UserSerializer(read_only=True)
    initiated_by = UserSerializer(read_only=True)
    cleared_by = UserSerializer(read_only=True)

    accept_url = serializers.HyperlinkedIdentityField(
        view_name="accept_initiate_request",
        lookup_field="id",
        lookup_url_kwarg="pk",
    )
    reject_url = serializers.HyperlinkedIdentityField(
        view_name="reject_initiate_request",
        lookup_field="id",
        lookup_url_kwarg="pk",
    )

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
            "description",
            "accept_url",
            "reject_url",
        )

    extra_kwargs = {"id": {"read_only": True}}


class ClearRequestPendingLendingRegistrySerializer(serializers.ModelSerializer):
    """
    Serializer for viewing active Lending Registry records whose clear request is pending.
    Also contains link accept or reject the clear request.
    """

    lender = UserSerializer(read_only=True)
    borrower = UserSerializer(read_only=True)
    initiated_by = UserSerializer(read_only=True)
    cleared_by = UserSerializer(read_only=True)

    accept_clear_request_url = serializers.HyperlinkedIdentityField(
        view_name="accept_clear_request",
        lookup_field="id",
        lookup_url_kwarg="pk",
    )
    reject_clear_request_url = serializers.HyperlinkedIdentityField(
        view_name="reject_clear_request",
        lookup_field="id",
        lookup_url_kwarg="pk",
    )

    class Meta:
        model = LendingRegistry
        fields = "__all__"

    extra_kwargs = {"id": {"read_only": True}}
