from rest_framework import serializers
from category.models import Category


# Create your serializers here.

# Serializer for category model

class CategorySerializer(serializers.ModelSerializer):
    """Serializer for the category object"""

    class Meta:
        model = Category
        fields = ("id", "name")