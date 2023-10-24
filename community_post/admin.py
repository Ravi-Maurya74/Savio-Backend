from django.contrib import admin
from .models import CommunityPost, Bookmark, PostVote, Comment, CommentVote


class CommunityPostAdmin(admin.ModelAdmin):
    readonly_fields = (
        "created_at",
        "updated_at",
        "upvotes",
        "downvotes",
        "score",
    )


class BookmarkAdmin(admin.ModelAdmin):
    readonly_fields = ["created_at"]


class VoteAdmin(admin.ModelAdmin):
    readonly_fields = ["created_at"]


class CommentAdmin(admin.ModelAdmin):
    readonly_fields = [
        "created_at",
        "updated_at",
        "depth",
        "upvotes",
        "downvotes",
        "score",
    ]


admin.site.register(CommunityPost, CommunityPostAdmin)
admin.site.register(Bookmark, BookmarkAdmin)
admin.site.register(PostVote, VoteAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(CommentVote)
