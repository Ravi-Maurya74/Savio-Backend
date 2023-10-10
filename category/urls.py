from django.urls import path
from category import views

urlpatterns = [
    path("", views.ListCategoryView.as_view(), name="list"),
]

