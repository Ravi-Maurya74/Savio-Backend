"""
Transaction models
"""

from django.db import models

# Create your models here.


class Transaction(models.Model):
    """Transaction model"""

    date = models.DateField()
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    title = models.CharField(max_length=255)
    category = models.ForeignKey("category.Category", on_delete=models.CASCADE)
    user = models.ForeignKey("user.User", on_delete=models.CASCADE)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return self.title
