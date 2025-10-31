from django.db import models
from django.core.exceptions import ValidationError

class Area(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Area'
        verbose_name_plural = 'Areas'

    def __str__(self):
        return self.name


class Postcode(models.Model):
    postcode = models.CharField(max_length=20, unique=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='postcodes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['postcode']
        verbose_name = 'Postcode'
        verbose_name_plural = 'Postcodes'

    def __str__(self):
        return f"{self.postcode} - {self.area.name}"
    
class TimeSlot(models.Model):
    DAYS_OF_WEEK = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    TIME_SLOTS = [
        ('08:00-10:00', '08:00 - 10:00'),
        ('10:00-12:00', '10:00 - 12:00'),
        ('12:00-14:00', '12:00 - 14:00'),
        ('14:00-16:00', '14:00 - 16:00'),
        ('16:00-18:00', '16:00 - 18:00'),
        ('18:00-20:00', '18:00 - 20:00'),
    ]
    
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='time_slots')
    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    time_slot = models.CharField(max_length=15, choices=TIME_SLOTS)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['area', 'day_of_week', 'time_slot']
        verbose_name = 'Time Slot'
        verbose_name_plural = 'Time Slots'
        unique_together = ['area', 'day_of_week', 'time_slot']

    def __str__(self):
        return f"{self.area.name} - {self.get_day_of_week_display()} ({self.time_slot})"

    def clean(self):
        """Validate that the combination is unique"""
        if TimeSlot.objects.filter(
            area=self.area,
            day_of_week=self.day_of_week,
            time_slot=self.time_slot
        ).exclude(pk=self.pk).exists():
            raise ValidationError(
                f'Time slot {self.time_slot} for {self.get_day_of_week_display()} already exists for this area.'
            )
