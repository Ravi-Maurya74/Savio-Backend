from rest_framework import serializers
from transaction.models import Transaction
from rest_framework.reverse import reverse


# Create your serializers here.

# Serializer for transaction model


class TransactionListSerializer(serializers.ModelSerializer):
    """Serializer for the transaction object"""

    detail = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ("id", "date", "amount", "title", "category", "detail")
        extra_kwargs = {"user": {"read_only": True}}

    def create(self, validated_data):
        """Create a new transaction"""
        return Transaction.objects.create(**validated_data)

    def get_detail(self, obj):
        request = self.context.get("request")
        return reverse("transaction-detail", kwargs={"pk": obj.pk}, request=request)


class TransactionDetailSerializer(serializers.ModelSerializer):
    """Serializer for the transaction object"""

    class Meta:
        model = Transaction
        fields = ("id", "date", "amount", "title", "category")
        extra_kwargs = {"user": {"read_only": True}}

    def create(self, validated_data):
        """Create a new transaction"""
        return Transaction.objects.create(**validated_data)
