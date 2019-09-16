from rest_framework import serializers

from . import models


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Review
        fields = ('id', 'book', 'review')


class BookSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = models.Book
        fields = ('id', 'title', 'category', 'author', 'cover', 'reviews')
