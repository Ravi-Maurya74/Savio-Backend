from django.shortcuts import render
from rest_framework import generics
from category.serializers import CategorySerializer
from category.models import Category

# Create your views here.

# List all categories using ListAPIView


class ListCategoryView(generics.ListAPIView):
    """List all categories"""

    serializer_class = CategorySerializer
    queryset = Category.objects.all()
