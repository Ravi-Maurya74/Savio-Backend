"""
Category model
"""

from django.db import models

# Create your models here.

from django.db import models


class Category(models.Model):
    FOOD_AND_DINING = "Food and Dining"
    GROCERIES = "Groceries"
    TRANSPORTATION = "Transportation"
    UTILITIES = "Utilities"
    RENT_MORTGAGE = "Rent/Mortgage"
    ENTERTAINMENT = "Entertainment"
    TRAVEL = "Travel"
    SHOPPING = "Shopping"
    HEALTH_AND_FITNESS = "Health and Fitness"
    PERSONAL_CARE = "Personal Care"
    EDUCATION = "Education"
    GIFTS_AND_DONATIONS = "Gifts and Donations"
    BUSINESS_EXPENSES = "Business Expenses"
    INSURANCE = "Insurance"
    TAXES = "Taxes"
    CATEGORY_CHOICES = [
        (FOOD_AND_DINING, "Food and Dining"),
        (GROCERIES, "Groceries"),
        (TRANSPORTATION, "Transportation"),
        (UTILITIES, "Utilities"),
        (RENT_MORTGAGE, "Rent/Mortgage"),
        (ENTERTAINMENT, "Entertainment"),
        (TRAVEL, "Travel"),
        (SHOPPING, "Shopping"),
        (HEALTH_AND_FITNESS, "Health and Fitness"),
        (PERSONAL_CARE, "Personal Care"),
        (EDUCATION, "Education"),
        (GIFTS_AND_DONATIONS, "Gifts and Donations"),
        (BUSINESS_EXPENSES, "Business Expenses"),
        (INSURANCE, "Insurance"),
        (TAXES, "Taxes"),
    ]
    name = models.CharField(max_length=20, choices=CATEGORY_CHOICES, unique=True)

    def __str__(self):
        return self.name
