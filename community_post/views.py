from rest_framework import generics, permissions, authentication
from rest_framework.response import Response
from community_post.models import (
    CommunityPost,
    Bookmark,
    PostVote,
    Comment,
    CommentVote,
)
from community_post.serializers import (
    CommunityPostCreateSerializer,
    CommunityPostListSerializer,
    CommunityPostDetailSerializer,
)


# Create your views here.


class ListCreateCommunityPostView(generics.ListCreateAPIView):
    """
    Create a new community post
    """

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    queryset = CommunityPost.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CommunityPostCreateSerializer
        return CommunityPostListSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class RetrieveUpdateDestroyCommunityPostView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, Update or Delete a community post
    """

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    queryset = CommunityPost.objects.all()
    serializer_class = CommunityPostDetailSerializer
