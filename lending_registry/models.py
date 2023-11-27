from django.db import models

# Create your models here.


class LendingRegistry(models.Model):
    INITIATE_REQUEST_PENDING = "Initiate Request Pending"
    ACTIVE = "Active"
    CLEAR_REQUEST_PENDING = "Clear Request Pending"
    CLEARED = "Cleared"

    STATUS_CHOICES = [
        (INITIATE_REQUEST_PENDING, "Initiate Request Pending"),
        (ACTIVE, "Active"),
        (CLEAR_REQUEST_PENDING, "Clear Request Pending"),
        (CLEARED, "Cleared"),
    ]

    lender = models.ForeignKey(
        "user.User", on_delete=models.CASCADE, related_name="lend"
    )
    borrower = models.ForeignKey(
        "user.User", on_delete=models.CASCADE, related_name="borrow"
    )
    initiated_by = models.ForeignKey(
        "user.User", on_delete=models.CASCADE, related_name="initiated"
    )
    cleared_by = models.ForeignKey(
        "user.User",
        on_delete=models.CASCADE,
        related_name="cleared",
        null=True,
        blank=True,
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    create_date = models.DateField(auto_now_add=True)
    clear_date = models.DateField(null=True, blank=True, auto_now=True)
    status = models.CharField(
        max_length=30, choices=STATUS_CHOICES, default=INITIATE_REQUEST_PENDING
    )
    description = models.CharField(max_length=250, null=True, blank=True)
