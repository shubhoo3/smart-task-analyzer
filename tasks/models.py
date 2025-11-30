from django.db import models

# Create your models here.

class Task(models.Model):
    title = models.CharField(max_length=255)
    due_date = models.DateField(null=True, blank=True)
    estimated_hours = models.PositiveIntegerField(default=1)
    importance = models.PositiveIntegerField(default=5)
    dependencies = models.JSONField(default=list, blank=True)

    def __str__(self) -> str:
        return self.title
