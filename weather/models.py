from django.contrib.auth import get_user_model
from django.db import models


class Location(models.Model):
    name = models.CharField(max_length=190)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='locations')
    latitude = models.DecimalField(max_digits=7, decimal_places=4)
    longitude = models.DecimalField(max_digits=7, decimal_places=4)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Локация'
        verbose_name_plural = 'Локации'
        constraints = [
            models.UniqueConstraint(fields=['user', 'latitude', 'longitude'], name='unique_user_coordinates')
        ]
