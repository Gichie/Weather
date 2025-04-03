from django.contrib.auth import get_user_model
from django.db import models


class Location(models.Model):
    name = models.CharField(max_length=190)
    country = models.CharField(max_length=80, blank=True, null=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='locations')
    latitude = models.DecimalField(max_digits=8, decimal_places=5)
    longitude = models.DecimalField(max_digits=8, decimal_places=5)

    def __str__(self):
        return f'{self.name}({self.country})'

    class Meta:
        verbose_name = 'Локация'
        verbose_name_plural = 'Локации'
        constraints = [
            models.UniqueConstraint(fields=['user', 'latitude', 'longitude'], name='unique_user_coordinates')
        ]
        ordering = ['id']
