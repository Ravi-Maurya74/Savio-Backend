# Generated by Django 4.2.5 on 2023-10-07 18:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="LendingRegistry",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("date", models.DateTimeField()),
                ("initiate_request", models.BooleanField(default=False)),
                ("clear_request", models.BooleanField(default=False)),
                ("clear_status", models.BooleanField(default=False)),
                (
                    "borrower",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="borrow",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "cleared_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cleared",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "initiated_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="initiated",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "lender",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lend",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
