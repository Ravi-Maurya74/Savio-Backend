from django.shortcuts import render
from rest_framework import generics, authentication, permissions
from django.contrib.auth import get_user_model
from transaction.serializers import TransactionListSerializer, TransactionDetailSerializer
from transaction.models import Transaction
from rest_framework.exceptions import PermissionDenied


# Create your views here.

# CreateView for transaction of the authenticated user


class ListCreateTransactionView(generics.ListCreateAPIView):
    """List and create transactions"""

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    serializer_class = TransactionListSerializer

    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(user=user)

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
