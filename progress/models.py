from django.db import models

from levels.models import Level


class GameSession(models.Model):
    session_key = models.CharField(max_length=100, unique=True)
    current_level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, blank=True)
    total_score = models.IntegerField(default=0)
    is_finished = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.session_key
