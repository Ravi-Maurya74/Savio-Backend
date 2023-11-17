from rest_framework import generics, authentication, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from transaction.serializers import (
    TransactionListSerializer,
    TransactionDetailSerializer,
    TransactionCreateSerializer,
)
from transaction.models import Transaction
from rest_framework.exceptions import PermissionDenied
from django.db.models import Sum
from django.db.models.functions import TruncDate
from calendar import monthrange
from datetime import date, timedelta


# Create your views here.

# CreateView for transaction of the authenticated user


class ListCreateTransactionView(generics.ListCreateAPIView):
    """List and create transactions"""

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    # serializer_class = TransactionListSerializer

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TransactionCreateSerializer
        else:
            return TransactionListSerializer

    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        create_serializer = TransactionCreateSerializer(data=request.data)
        create_serializer.is_valid(raise_exception=True)
        self.perform_create(create_serializer)
        headers = self.get_success_headers(create_serializer.data)

        # Serialize the created transaction with the TransactionListSerializer
        list_serializer = TransactionListSerializer(create_serializer.instance)

        return Response(
            list_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        """Create a new transaction"""
        serializer.save(user=self.request.user)


# RetrieveUpdateDestroyView for transaction of the authenticated user


class RetrieveUpdateDestroyTransactionView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a transaction"""

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    serializer_class = TransactionDetailSerializer

    def get_queryset(self):
        user = self.request.user
        transaction = Transaction.objects.filter(pk=self.kwargs["pk"])
        if transaction[0].user == user:
            return transaction
        else:
            raise PermissionDenied()


# View to get the list of transactions of the authenticated user made in a particular month


class ListTransactionByMonthView(generics.ListAPIView):
    """List transactions by month"""

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    serializer_class = TransactionListSerializer

    def get_queryset(self):
        user = self.request.user
        month = self.kwargs["month"]
        year = self.kwargs["year"]
        return Transaction.objects.filter(user=user, date__month=month, date__year=year)


# View to get the total expenditure of each day in a particular month of the authenticated user.
# The returned list  should have items that contain two fields: date and total_amount.
# Returned list should not be transactions but the total expenditure of each day in a particular month of the authenticated user.
# This should be calculated by adding the amount of all the transactions of that day for all days of the month.


class DailyExpenditureView(generics.GenericAPIView):
    """Get the total expenditure of each day in a particular month"""

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, year, month, *args, **kwargs):
        user = self.request.user
        queryset = Transaction.objects.filter(
            user=user, date__year=year, date__month=month
        )
        daily_totals = (
            queryset
            # .annotate(transaction_date=TruncDate('date'))  # Rename 'date' to 'transaction_date'
            .values("date")  # Use the new name here
            .annotate(total_amount=Sum("amount"))
            .order_by("date")  # And here
        )
        # return Response(list(daily_totals))
        # if we return the list of daily_totals, like above, we would get the list but it will not have all days of that month. It will only have days on which there was atleast one transaction.
        # So, we need to create a list of all days of that month and then add the total_amount to the corresponding day in the list of all days.

        daily_totals_dict = {
            daily_total["date"]: daily_total["total_amount"]
            for daily_total in daily_totals
        }

        _, last_day = monthrange(year, month)
        all_days = [date(year, month, day) for day in range(1, last_day + 1)]

        result = [
            {"date": day, "total_amount": daily_totals_dict.get(day, 0)}
            for day in all_days
        ]

        return Response(result)
