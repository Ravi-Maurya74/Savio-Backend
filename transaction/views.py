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
import numpy as np
from sklearn.linear_model import LinearRegression
import calendar


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


class SpendingByCategoryView(generics.ListAPIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, year, month, *args, **kwargs):
        user = request.user
        transactions = Transaction.objects.filter(
            user=user, date__year=year, date__month=month
        )
        spending_by_category = transactions.values("category__name").annotate(
            total_spending=Sum("amount")
        )
        return Response(spending_by_category)


class MonthlySpendingPredictionView(generics.GenericAPIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user
        current_month = date.today().month
        current_year = date.today().year
        transactions = Transaction.objects.filter(
            user=user, date__year=current_year, date__month=current_month
        )
        total_spending = transactions.aggregate(Sum("amount"))["amount__sum"]

        # Calculate the cumulative expenditure up to each day
        cumulative_expenditures_actual = []
        for day in range(1, date.today().day + 1):
            cumulative_expenditure = transactions.filter(date__day__lte=day).aggregate(
                Sum("amount")
            )["amount__sum"]
            # Replace None with 0
            if cumulative_expenditure is None:
                cumulative_expenditure = 0
            # Include the full date (day, month, and year)
            full_date = date(date.today().year, date.today().month, day)
            cumulative_expenditures_actual.append(
                {"date": full_date, "expenditure": cumulative_expenditure}
            )

        # Train the model with the cumulative expenditure up to each day
        days = np.array(range(1, date.today().day + 1))
        model = LinearRegression().fit(
            days.reshape((-1, 1)),
            [
                expenditure["expenditure"]
                for expenditure in cumulative_expenditures_actual
            ],
        )

        # Predict the cumulative expenditure for the rest of the month
        cumulative_expenditures_predicted = [
            {"date": date(current_year, current_month, day), "expenditure": expenditure}
            for day, expenditure in zip(
                range(
                    date.today().day + 1,
                    calendar.monthrange(current_year, current_month)[1] + 1,
                ),
                model.predict(
                    np.array(
                        range(
                            date.today().day + 1,
                            calendar.monthrange(current_year, current_month)[1] + 1,
                        )
                    ).reshape((-1, 1))
                ),
            )
        ]

        monthly_budget = (
            user.total_budget
        )  # Assuming the monthly budget is stored in a profile related to the user

        return Response(
            {
                # 'transactions': TransactionSerializer(transactions, many=True).data,
                "monthly_budget": monthly_budget,
                "predicted_total_expenditure": cumulative_expenditures_predicted[-1][
                    "expenditure"
                ]
                if cumulative_expenditures_predicted
                else None,
                "cumulative_expenditures": cumulative_expenditures_actual
                + cumulative_expenditures_predicted,
            }
        )
