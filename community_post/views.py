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
    CommentListSerializer,
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


# View to bookmark a post or remove a bookmark of the authenticated user


class BookmarkView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def post(self, request, pk):
        post = generics.get_object_or_404(CommunityPost, pk=pk)
        bookmark, created = Bookmark.objects.get_or_create(user=request.user, post=post)
        # The get_or_create method returns a tuple where the first element is the Bookmark object and the second element is a boolean indicating whether the object was created (True) or retrieved (False).
        if not created:
            bookmark.delete()
        return Response({"success": True})


# View to upvote or downvote a post of the authenticated user


class PostVoteView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def post(self, request, pk):
        post = generics.get_object_or_404(CommunityPost, pk=pk)
        vote = int(request.data.get("vote"))
        if vote not in [PostVote.UPVOTE, PostVote.DOWNVOTE]:
            return Response({"success": False})
        post_vote, created = PostVote.objects.get_or_create(
            user=request.user, post=post, defaults={"vote": vote}
        )
        if not created:
            if post_vote.vote == vote:
                post_vote.delete()
            else:
                post_vote.vote = vote
                post_vote.save()
        else:
            post_vote.vote = vote
            post_vote.save()
        return Response({"success": True})
    

class CommentListView(generics.ListAPIView):
    serializer_class = CommentListSerializer

    def post(self, request, *args, **kwargs):
        post_id = request.data.get('post_id')
        comment_id = request.data.get('comment_id')
        if comment_id == 0:
            comments = Comment.objects.filter(post_id=post_id, depth=0)
        else:
            comments = Comment.objects.filter(parent_id=comment_id)
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)
