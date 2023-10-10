"""
User Database Model
"""

from dotenv import load_dotenv

load_dotenv()

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

from decimal import Decimal

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from io import BytesIO
from PIL import Image
import os

from supabase import create_client, Client
from django.core.files.base import ContentFile

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)
bucket_name: str = "profile_pic"


# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not email:
            raise ValueError("User must have an email address")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)  # encrypts the password
        user.save(using=self._db)  # standard procedure for saving objects in django
        return user

    def create_superuser(self, email, password):
        """Creates and saves a new superuser"""
        user = self.create_user(email, password)
        user.is_superuser = True  # is_superuser is created by PermissionsMixin
        user.is_staff = True  # is_staff is created by PermissionsMixin
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    total_budget = models.DecimalField(
        max_digits=20, decimal_places=2, default=Decimal(0.00)
    )
    profile_pic = models.ImageField(
        null=True,
        blank=True,
    )

    objects = UserManager()

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"

    def save(self, *args, **kwargs):
        if self.pk:
            # Get the previous profile picture
            old_user = User.objects.get(pk=self.pk)
            old_profile_pic = old_user.profile_pic

            # Delete the previous profile picture if it exists
            if old_profile_pic and self.profile_pic != old_profile_pic:
                # Delete the old profile picture from Supabase storage
                file_name = os.path.basename(old_profile_pic.name)
                response = supabase.storage.from_(bucket_name).remove(file_name)

        if self.profile_pic:
            # Open the uploaded image with Pillow
            img = Image.open(self.profile_pic)

            # Convert the image mode to RGB
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Compress the image to limit its size to 1MB
            output = BytesIO()
            img.save(output, format="JPEG", quality=60)
            # output.seek(0)

            # Upload the compressed image to Supabase storage
            file_name = f"{self.profile_pic.name.split('.')[0]}.jpg"
            file_content = ContentFile(output.read())
            file_options = {
                # "cacheControl": 3600,
                "contentType": "image/jpeg",
            }
            response = supabase.storage.from_(bucket_name).upload(
                file=output.getvalue(), file_options=file_options, path=file_name
            )
            self.profile_pic = f"{bucket_name}/{file_name}"

        super().save(*args, **kwargs)
