from rest_framework import generics, permissions, authentication
from rest_framework.response import Response
from django.db.models import Count, Q
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
        post_id = request.data.get("post_id")
        comment_id = request.data.get("comment_id")
        if comment_id == 0:
            comments = Comment.objects.filter(post_id=post_id, depth=0)
        else:
            comments = Comment.objects.filter(parent_id=comment_id)

        comments = comments.annotate(
            priority=(
                Count("votes", filter=Q(votes__vote=CommentVote.UPVOTE))
                - Count("votes", filter=Q(votes__vote=CommentVote.DOWNVOTE))
            )
        ).order_by("-priority")

        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)


# View to upvote or downvote a comment of the authenticated user


class CommentVoteView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def post(self, request, pk):
        comment = generics.get_object_or_404(Comment, pk=pk)
        vote = int(request.data.get("vote"))
        if vote not in [CommentVote.UPVOTE, CommentVote.DOWNVOTE]:
            return Response({"success": False})
        comment_vote, created = CommentVote.objects.get_or_create(
            user=request.user, comment=comment, defaults={"vote": vote}
        )
        if not created:
            if comment_vote.vote == vote:
                comment_vote.delete()
            else:
                comment_vote.vote = vote
                comment_vote.save()
        else:
            comment_vote.vote = vote
            comment_vote.save()
        return Response({"success": True})


# View to create new comment or reply to a comment of the authenticated user


class CommentCreateView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def post(self, request, *args, **kwargs):
        post_id = request.data.get("post_id")
        comment_id = request.data.get("comment_id")
        content = request.data.get("content")
        if comment_id == 0:
            comment = Comment.objects.create(
                post_id=post_id, author=request.user, content=content
            )
        else:
            parent = Comment.objects.get(id=comment_id)
            comment = Comment.objects.create(
                post_id=post_id, author=request.user, content=content, parent=parent
            )
        # serializer = CommentListSerializer(comment)
        return Response({"success": True})


# ListApiView to return all the post made by the authenticated user


class UserPostListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    serializer_class = CommunityPostListSerializer
    # queryset = CommunityPost.objects.all()

    def get_queryset(self):
        return CommunityPost.objects.filter(author=self.request.user)


# ListApiView to return all the posts bookmarked by the authenticated user.


class UserBookmarkListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    serializer_class = CommunityPostListSerializer
    # queryset = CommunityPost.objects.all()

    def get_queryset(self):
        user = self.request.user
        bookmarks = Bookmark.objects.filter(user=user)
        return CommunityPost.objects.filter(bookmarks__in=bookmarks)
