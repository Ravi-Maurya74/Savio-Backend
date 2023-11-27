from django.shortcuts import render
from rest_framework import generics, authentication, permissions
from django.contrib.auth import get_user_model
from lending_registry.serializers import (
    ActiveLendingRegistrySerializer,
    ClearedLendingRegistrySerializer,
    LendingRegistryCreateSerializer,
    AcceptLendingRegistrySerializer,
    ClearRequestPendingLendingRegistrySerializer,
    InitiateClearRequestSerializer,
)
from lending_registry.models import LendingRegistry
from django.db.models import Q, Sum
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema


class StatusChoicesView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        return Response(dict(LendingRegistry.STATUS_CHOICES))


# CreateView for lending registry of the authenticated user
class CreateLendingRegistryView(generics.CreateAPIView):
    """
    Create a new LendingRegistry
    """

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    serializer_class = LendingRegistryCreateSerializer

    def perform_create(self, serializer):
        """Create a new lending registry"""
        serializer.save(initiated_by=self.request.user)


# ListView for lending registry of active records of the authenticated user
class ListActiveLendingRegistryView(generics.ListAPIView):
    """
    List all the active LendingRegistry of the authenticated user.
    """

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    serializer_class = ActiveLendingRegistrySerializer

    def get_queryset(self):
        user = self.request.user
        return LendingRegistry.objects.filter(
            Q(lender=user) | Q(borrower=user), status=LendingRegistry.ACTIVE
        )


# ListView for LendingRegistry of cleared records of the authenticated user.
class ListClearedLendingRegistryView(generics.ListAPIView):
    """
    List all the cleared LendingRegistry of the authenticated user.
    """

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    serializer_class = ClearedLendingRegistrySerializer

    def get_queryset(self):
        user = self.request.user
        return LendingRegistry.objects.filter(
            Q(lender=user) | Q(borrower=user), status=LendingRegistry.CLEARED
        )


class ListInitiateRequestPendingLendingRegistryView(generics.ListAPIView):
    """
    ListView for lending registry of records with initiate request pending.
    Also gives links to accept or reject initiate request.
    """

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    serializer_class = AcceptLendingRegistrySerializer

    def get_queryset(self):
        user = self.request.user
        return LendingRegistry.objects.filter(
            Q(lender=user) | Q(borrower=user),
            status=LendingRegistry.INITIATE_REQUEST_PENDING,
        ).exclude(initiated_by=user)


# ListView for lending registry of records with clear request pending
class ListClearRequestPendingLendingRegistryView(generics.ListAPIView):
    """
    ListView for lending registry of records with clear request pending.
    Also gives links to accept or reject clear request.
    """

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    serializer_class = ClearRequestPendingLendingRegistrySerializer

    def get_queryset(self):
        user = self.request.user
        return LendingRegistry.objects.filter(
            Q(lender=user) | Q(borrower=user),
            status=LendingRegistry.CLEAR_REQUEST_PENDING,
        ).exclude(cleared_by=user)


# View to accept pending initiate request


@extend_schema(
    request=None,
    responses={
        "200": AcceptLendingRegistrySerializer,
    },
)
@api_view(["GET"])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def accept_initiate_request_view(request, pk):
    """
    Redirected endpoint. Do not use manually.
    """
    try:
        lending_registry = LendingRegistry.objects.get(
            pk=pk, status=LendingRegistry.INITIATE_REQUEST_PENDING
        )
    except LendingRegistry.DoesNotExist:
        return Response(
            {
                "error": "Lending registry not found or not in INITIATE_REQUEST_PENDING status."
            },
            status=404,
        )

    if (
        lending_registry.lender != request.user
        and lending_registry.borrower != request.user
    ) or (lending_registry.initiated_by == request.user):
        return Response({"error": "Not allowed."}, status=403)

    serializer = ActiveLendingRegistrySerializer(
        lending_registry,
        data={"status": LendingRegistry.ACTIVE},
        partial=True,
        context={"request": request},
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=400)


# view to reject pending initiate request. Should be able to reject only if the user is the lender or borrower of the lending registry and not the initiator.
# On rejecting, the lending registry should be deleted.


@extend_schema(
    request=None, responses={"200": {"success": "Lending registry deleted."}}
)
@api_view(["GET"])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def reject_initiate_request_view(request, pk):
    """
    Redirected endpoint. Do not use manually.
    """
    try:
        lending_registry = LendingRegistry.objects.get(
            pk=pk, status=LendingRegistry.INITIATE_REQUEST_PENDING
        )
    except LendingRegistry.DoesNotExist:
        return Response(
            {
                "error": "Lending registry not found or not in INITIATE_REQUEST_PENDING status."
            },
            status=404,
        )

    if (
        lending_registry.lender != request.user
        and lending_registry.borrower != request.user
    ) or (lending_registry.initiated_by == request.user):
        return Response({"error": "Not allowed."}, status=403)

    lending_registry.delete()
    return Response({"success": "Lending registry deleted."}, status=200)


# view to accept pending clear request. Should be able to accept only if the user is the lender or borrower of the lending registry and not the same as cleared_by.
# On accepting, the lending registry status should be changed to CLEARED.


@extend_schema(
    request=None,
    responses={
        "200": AcceptLendingRegistrySerializer,
    },
)
@api_view(["GET"])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def accept_clear_request_view(request, pk):
    """
    Redirected endpoint. Do not use manually.
    """
    try:
        lending_registry = LendingRegistry.objects.get(
            pk=pk, status=LendingRegistry.CLEAR_REQUEST_PENDING
        )
    except LendingRegistry.DoesNotExist:
        return Response(
            {
                "error": "Lending registry not found or not in CLEAR_REQUEST_PENDING status."
            },
            status=404,
        )

    if (
        lending_registry.lender != request.user
        and lending_registry.borrower != request.user
    ) or (lending_registry.cleared_by == request.user):
        return Response({"error": "Not allowed."}, status=403)

    serializer = ActiveLendingRegistrySerializer(
        lending_registry,
        data={"status": LendingRegistry.CLEARED},
        partial=True,
        context={"request": request},
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=400)


# view to reject pending clear request. Should be able to reject only if the user is the lender or borrower of the lending registry and not the same as cleared_by.
# On rejecting, the lending registry status should be changed to ACTIVE.


@extend_schema(
    request=None,
    responses={
        "200": AcceptLendingRegistrySerializer,
    },
)
@api_view(["GET"])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def reject_clear_request_view(request, pk):
    """
    Redirected endpoint. Do not use manually.
    """
    try:
        lending_registry = LendingRegistry.objects.get(
            pk=pk, status=LendingRegistry.CLEAR_REQUEST_PENDING
        )
    except LendingRegistry.DoesNotExist:
        return Response(
            {
                "error": "Lending registry not found or not in CLEAR_REQUEST_PENDING status."
            },
            status=404,
        )

    if (
        lending_registry.lender != request.user
        and lending_registry.borrower != request.user
    ) or (lending_registry.cleared_by == request.user):
        return Response({"error": "Not allowed."}, status=403)

    serializer = ActiveLendingRegistrySerializer(
        lending_registry,
        data={"status": LendingRegistry.ACTIVE},
        partial=True,
        context={"request": request},
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=400)


# view to initiate a clear request. Should be able to initiate only if the user is the lender or borrower of the lending registry.
# On initiating, the lending registry status should be changed to CLEAR_REQUEST_PENDING.
# The cleared_by field should be set to whoever initiated the clear request.


@extend_schema(
    request=None,
    responses={
        "200": AcceptLendingRegistrySerializer,
    },
)
@api_view(["GET"])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def initiate_clear_request_view(request, pk):
    """
    Redirected endpoint. Do not use manually.
    """
    try:
        lending_registry = LendingRegistry.objects.get(
            pk=pk, status=LendingRegistry.ACTIVE
        )
    except LendingRegistry.DoesNotExist:
        return Response(
            {"error": "Lending registry not found or not in ACTIVE status."},
            status=404,
        )

    if (
        lending_registry.lender != request.user
        and lending_registry.borrower != request.user
    ):
        return Response({"error": "Not allowed."}, status=403)

    serializer = InitiateClearRequestSerializer(
        lending_registry,
        data={
            "status": LendingRegistry.CLEAR_REQUEST_PENDING,
            "cleared_by": request.user.id,
        },
        partial=True,
        context={"request": request},
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=400)


class UserBalanceView(generics.GenericAPIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        total_owed = (
            LendingRegistry.objects.filter(borrower=user)
            .exclude(
                Q(status=LendingRegistry.CLEARED)
                | Q(status=LendingRegistry.INITIATE_REQUEST_PENDING)
            )
            .aggregate(Sum("amount"))["amount__sum"]
            or 0
        )
        total_lent = (
            LendingRegistry.objects.filter(lender=user)
            .exclude(
                Q(status=LendingRegistry.CLEARED)
                | Q(status=LendingRegistry.INITIATE_REQUEST_PENDING)
            )
            .aggregate(Sum("amount"))["amount__sum"]
            or 0
        )
        net = total_lent - total_owed

        return Response(
            {
                "total_owed": total_owed,
                "total_lent": total_lent,
                "net": net,
            }
        )
