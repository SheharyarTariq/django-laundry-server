from django.db import models

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
    
class TimeSlot(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='time_slots')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['area', 'day_of_week', 'start_time']
        unique_together = ['area', 'day_of_week', 'start_time', 'end_time']
        verbose_name = 'Time Slot'
        verbose_name_plural = 'Time Slots'

    def __str__(self):
        return f"{self.area.name} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"

    def get_day_name(self):
        return self.get_day_of_week_display()


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