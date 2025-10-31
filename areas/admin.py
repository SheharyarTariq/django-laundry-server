from django.contrib import admin
from .models import Area, Postcode, TimeSlot


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'postcode_count', 'timeslot_count', 'created_at', 'updated_at']
    search_fields = ['name']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    def postcode_count(self, obj):
        return obj.postcodes.count()
    postcode_count.short_description = 'Postcodes'
    
    def timeslot_count(self, obj):
        return obj.time_slots.count()
    timeslot_count.short_description = 'Time Slots'


@admin.register(Postcode)
class PostcodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'postcode', 'area', 'created_at', 'updated_at']
    list_filter = ['area', 'created_at']
    search_fields = ['postcode', 'area__name']
    ordering = ['postcode']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['area']


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['id', 'area', 'day_of_week', 'time_slot', 'is_active', 'created_at']
    list_filter = ['area', 'day_of_week', 'is_active', 'created_at']
    search_fields = ['area__name']
    ordering = ['area', 'day_of_week', 'time_slot']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['area']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('area', 'day_of_week', 'time_slot')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )