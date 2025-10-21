from django.db import models
from django.utils import timezone

class AnalyzedString(models.Model):
    sha256_hash = models.CharField(max_length=64, unique=True)
    original_string = models.TextField()
    length = models.IntegerField(null=False, blank=False)
    is_palindrome = models.BooleanField()
    unique_characters = models.IntegerField()
    word_count = models.IntegerField()
    character_frequency_map = models.JSONField()
    created_at = models.DateTimeField(
        default=timezone.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    )
