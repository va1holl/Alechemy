from django.db import models

class Place(models.Model):
    KIND_CHOICES = [
        ("bar", "Бар"),
        ("shop", "Магазин"),
        ("other", "Другое"),
    ]
    name = models.CharField(max_length=120)
    kind = models.CharField(max_length=16, choices=KIND_CHOICES)
    lat = models.FloatField()
    lon = models.FloatField()
    city = models.CharField(max_length=64, blank=True)
    address = models.CharField(max_length=256, blank=True)
    url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.get_kind_display()})"

class Promotion(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="promotions")
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    valid_from = models.DateField()
    valid_to = models.DateField()
    source_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} @ {self.place}"