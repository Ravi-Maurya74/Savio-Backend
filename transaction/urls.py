from django.urls import path
from transaction import views

urlpatterns = [
    path("", views.ListCreateTransactionView.as_view(), name="list-create"),
    path(
        "<int:pk>/",
        views.RetrieveUpdateDestroyTransactionView.as_view(),
        name="transaction-detail",
    ),
    path(
        "<int:year>/<int:month>/",
        views.ListTransactionByMonthView.as_view(),
        name="transactions-by-month",
    ),
    path(
        "daily/<int:year>/<int:month>/",
        views.DailyExpenditureView.as_view(),
        name="daily-expenditure",
    ),
    path(
        "category/<int:year>/<int:month>/",
        views.SpendingByCategoryView.as_view(),
        name="category-list",
    ),
    path(
        "prediction/",
        views.MonthlySpendingPredictionView.as_view(),
        name="prediction",
    ),
]
