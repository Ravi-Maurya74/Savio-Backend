from django.urls import path
from community_post import views

urlpatterns = [
    path("", views.ListCreateCommunityPostView.as_view(), name="list-create"),
    path("user_posts/", views.UserPostListView.as_view(), name="user-posts"),
    path(
        "user_bookmarks/", views.UserBookmarkListView.as_view(), name="user-bookmarks"
    ),
    path(
        "<int:pk>/",
        views.RetrieveUpdateDestroyCommunityPostView.as_view(),
        name="community-post-detail",
    ),
    path("<int:pk>/bookmark/", views.BookmarkView.as_view(), name="bookmark"),
    path("<int:pk>/vote/", views.PostVoteView.as_view(), name="vote"),
    path("comments/", views.CommentListView.as_view(), name="list-comment"),
    # path("comments/<int:pk>/", views.CommentDetailView.as_view(), name="detail-comment"),
    path(
        "comments/<int:pk>/vote/", views.CommentVoteView.as_view(), name="vote-comment"
    ),
    path("comments/create/", views.CommentCreateView.as_view(), name="create-comment"),
]
