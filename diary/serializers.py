from rest_framework import serializers
from .models import DiaryEntry, Tag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class DiaryEntrySerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = DiaryEntry
        fields = '__all__'
        