from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from lab1.validators import validate_non_empty_or_spaces


class Team(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        validators=[validate_non_empty_or_spaces]
    )
    rating = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ]
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.rating})"

    def get_win_probability_against(self, other_team):
        total = self.rating + other_team.rating
        if total == 0:
            return 0.5
        return self.rating / total
