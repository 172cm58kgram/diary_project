from django.test import TestCase
from .models import DiaryEntry
from django.contrib.auth.models import User

class DiaryEntryTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.entry = DiaryEntry.objects.create(
            author=self.user,
            title="Test Entry",
            content="This is a test diary entry."
        )

    def test_diary_entry_creation(self):
        """日記の作成テスト"""
        self.assertEqual(self.entry.title, "Test Entry")
        self.assertEqual(self.entry.content, "This is a test diary entry.")
        self.assertEqual(self.entry.author.username, "testuser")