from rest_framework import serializers
from .models import Area, Postcode, TimeSlot
from datetime import time

class PostcodeSerializer(serializers.ModelSerializer):
    """Serializer for Postcode with area details"""
    area_name = serializers.CharField(source='area.name', read_only=True)
    
    class Meta:
        model = Postcode
        fields = ['id', 'postcode', 'area', 'area_name', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate_postcode(self, value):
        """Validate and format postcode"""
        if not value:
            raise serializers.ValidationError("Postcode is required.")
        
        # Remove extra spaces and convert to uppercase
        value = value.strip().upper()
        
        # Check if postcode already exists (for create operation)
        if not self.instance:  # Only check during creation
            if Postcode.objects.filter(postcode=value).exists():
                raise serializers.ValidationError(f"Postcode '{value}' already exists.")
        else:  # During update, exclude the current instance
            if Postcode.objects.filter(postcode=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError(f"Postcode '{value}' already exists.")
        
        return value

class PostcodeListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing postcodes"""
    
    class Meta:
        model = Postcode
        fields = ['id', 'postcode']

class TimeSlotSerializer(serializers.ModelSerializer):
    """Serializer for TimeSlot"""
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = TimeSlot
        fields = ['id', 'day_of_week', 'day_name', 'start_time', 'end_time', 'is_active']

class TimeSlotToggleSerializer(serializers.Serializer):
    """Serializer for toggling time slot active status"""
    is_active = serializers.BooleanField(required=True)

class AreaListSerializer(serializers.ModelSerializer):
    """Serializer for listing areas - only shows name"""
    
    class Meta:
        model = Area
        fields = ['id', 'name']

class AreaDetailSerializer(serializers.ModelSerializer):
    """Serializer for area detail - shows all associated postcodes and time slots"""
    postcodes = PostcodeListSerializer(many=True, read_only=True)
    postcode_count = serializers.SerializerMethodField()
    time_slots = TimeSlotSerializer(many=True, read_only=True)
    
    class Meta:
        model = Area
        fields = ['id', 'name', 'postcode_count', 'postcodes', 'time_slots', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_postcode_count(self, obj):
        """Return the count of postcodes in this area"""
        return obj.postcodes.count()
    
class AreaSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating areas"""
    
    class Meta:
        model = Area
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_name(self, value):
        """Validate area name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Area name is required.")
        
        value = value.strip()
        
        # Check if area name already exists (for create operation)
        if not self.instance:  # Only check during creation
            if Area.objects.filter(name__iexact=value).exists():
                raise serializers.ValidationError(f"Area '{value}' already exists.")
        else:  # During update, exclude the current instance
            if Area.objects.filter(name__iexact=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError(f"Area '{value}' already exists.")
        
        return value
    
    def create(self, validated_data):
        """Create area and automatically create time slots"""
        area = Area.objects.create(**validated_data)
        
        # Define time slots
        time_slots_config = [
            (time(8, 0), time(10, 0)),
            (time(10, 0), time(12, 0)),
            (time(12, 0), time(14, 0)),
            (time(14, 0), time(18, 0)),
        ]
        
        # Create time slots for each day of the week
        time_slots = []
        for day in range(7):  # Monday (0) to Sunday (6)
            for start_time, end_time in time_slots_config:
                time_slots.append(
                    TimeSlot(
                        area=area,
                        day_of_week=day,
                        start_time=start_time,
                        end_time=end_time,
                        is_active=False
                    )
                )
        
        # Bulk create all time slots
        TimeSlot.objects.bulk_create(time_slots)
        
        return area