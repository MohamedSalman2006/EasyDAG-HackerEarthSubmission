from rest_framework import serializers
from .models import Post, User

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['wallet_address']

class PostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    score = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'post_type', 'created_at', 'author', 'score']