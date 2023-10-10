from django.urls import path
from transaction import views

urlpatterns = [
    path("", views.ListCreateTransactionView.as_view(), name="list-create"),
    path(
        "<int:pk>/",
        views.RetrieveUpdateDestroyTransactionView.as_view(),
        name="transaction-detail",
    ),
]
