from django.db import models

from io import BytesIO
from PIL import Image
import os

from supabase import create_client, Client
from django.core.files.base import ContentFile
from django.conf import settings
from django.db.models import Count, Case, When, IntegerField


url: str = settings.SUPABASE_URL
key: str = settings.SUPABASE_KEY
supabase: Client = create_client(url, key)
bucket_name: str = "community_post_images"

# Create your models here.


class CommunityPost(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey("user.User", on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.title

    def upvotes(self) -> int:
        return self.votes.filter(vote=PostVote.UPVOTE).count()

    def downvotes(self):
        return self.votes.filter(vote=PostVote.DOWNVOTE).count()

    def score(self):
        upvotes = self.votes.filter(vote=PostVote.UPVOTE).count()
        downvotes = self.votes.filter(vote=PostVote.DOWNVOTE).count()
        return upvotes - downvotes

    def save(self, *args, **kwargs):
        old_image = None
        if self.pk:
            old_image = CommunityPost.objects.get(pk=self.pk).image
            if old_image and old_image != self.image:
                file_name = os.path.basename(old_image.name)
                response = supabase.storage.from_(bucket_name).remove(file_name)

        if self.image and (not self.pk or self.image != old_image):
            # Open the uploaded image with Pillow
            img = Image.open(self.image)

            # Convert the image mode to RGB
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Compress the image to limit its size to 1MB
            output = BytesIO()
            img.save(output, format="JPEG", quality=60)
            # output.seek(0)

            # Upload the compressed image to Supabase storage
            file_name = f"{self.image.name.split('.')[0]}.jpg"
            file_content = ContentFile(output.read())
            file_options = {
                # "cacheControl": 3600,
                "contentType": "image/jpeg",
            }
            response = supabase.storage.from_(bucket_name).upload(
                file=output.getvalue(), file_options=file_options, path=file_name
            )
            self.image = f"{bucket_name}/{file_name}"

        super().save(*args, **kwargs)


class Bookmark(models.Model):
    user = models.ForeignKey(
        "user.User", on_delete=models.CASCADE, related_name="bookmarks"
    )
    post = models.ForeignKey(
        "community_post.CommunityPost",
        on_delete=models.CASCADE,
        related_name="bookmarks",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")

    def __str__(self):
        return f"{self.user} - {self.post}"


class PostVote(models.Model):
    UPVOTE = 1
    DOWNVOTE = -1
    VOTE_CHOICES = (
        (UPVOTE, "Upvote"),
        (DOWNVOTE, "Downvote"),
    )

    user = models.ForeignKey(
        "user.User", on_delete=models.CASCADE, related_name="votes"
    )
    post = models.ForeignKey(
        "community_post.CommunityPost", on_delete=models.CASCADE, related_name="votes"
    )
    vote = models.SmallIntegerField(choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")

    def __str__(self):
        return f"{self.user} {self.get_vote_display()}d {self.post}"


class Comment(models.Model):
    content = models.TextField()
    author = models.ForeignKey(
        "user.User", on_delete=models.CASCADE, related_name="comments"
    )
    post = models.ForeignKey(
        "community_post.CommunityPost",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="replies",
        null=True,
        blank=True,
    )
    depth = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.author} commented {self.content[:50]} on {self.post}"

    def upvotes(self):
        return self.votes.filter(vote=CommentVote.UPVOTE).count()

    def downvotes(self):
        return self.votes.filter(vote=CommentVote.DOWNVOTE).count()

    def score(self):
        upvotes = self.votes.filter(vote=CommentVote.UPVOTE).count()
        downvotes = self.votes.filter(vote=CommentVote.DOWNVOTE).count()
        return upvotes - downvotes

    def save(self, *args, **kwargs):
        if self.parent is not None:
            self.depth = self.parent.depth + 1
        super().save(*args, **kwargs)


class CommentVote(models.Model):
    UPVOTE = 1
    DOWNVOTE = -1
    VOTE_CHOICES = (
        (UPVOTE, "Upvote"),
        (DOWNVOTE, "Downvote"),
    )

    user = models.ForeignKey(
        "user.User", on_delete=models.CASCADE, related_name="comment_votes"
    )
    comment = models.ForeignKey(
        "community_post.Comment", on_delete=models.CASCADE, related_name="votes"
    )
    vote = models.SmallIntegerField(choices=VOTE_CHOICES)

    class Meta:
        unique_together = ("user", "comment")

    def __str__(self):
        return f"{self.user} - {self.comment} - {self.get_vote_display()}"
