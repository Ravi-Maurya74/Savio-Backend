from django.urls import path
from community_post import views

urlpatterns = [
    path("", views.ListCreateCommunityPostView.as_view(), name="list-create"),
    path(
        "<int:pk>/",
        views.RetrieveUpdateDestroyCommunityPostView.as_view(),
        name="community-post-detail",
    ),
]
