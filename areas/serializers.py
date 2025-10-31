from rest_framework import serializers
from .models import Area, Postcode, TimeSlot


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


class AreaListSerializer(serializers.ModelSerializer):
    """Serializer for listing areas - only shows name"""
    
    class Meta:
        model = Area
        fields = ['id', 'name']


class AreaDetailSerializer(serializers.ModelSerializer):
    """Serializer for area detail - shows all associated postcodes"""
    postcodes = PostcodeListSerializer(many=True, read_only=True)
    
    class Meta:
        model = Area
        fields = ['id', 'name', 'postcodes', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


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
    
class TimeSlotSerializer(serializers.ModelSerializer):
    """Serializer for TimeSlot"""
    day_display = serializers.CharField(source='get_day_of_week_display', read_only=True)
    time_display = serializers.CharField(source='get_time_slot_display', read_only=True)
    
    class Meta:
        model = TimeSlot
        fields = ['id', 'area', 'day_of_week', 'day_display', 'time_slot', 'time_display', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        """Check if time slot already exists for this area and day"""
        area = data.get('area')
        day_of_week = data.get('day_of_week')
        time_slot = data.get('time_slot')
        
        # For update operations, exclude the current instance
        queryset = TimeSlot.objects.filter(
            area=area,
            day_of_week=day_of_week,
            time_slot=time_slot
        )
        
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                f'Time slot {time_slot} for {day_of_week} already exists for this area.'
            )
        
        return data


class TimeSlotListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing time slots"""
    day_display = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = TimeSlot
        fields = ['id', 'day_of_week', 'day_display', 'time_slot', 'is_active']


class TimeSlotBulkCreateSerializer(serializers.Serializer):
    """Serializer for bulk creating time slots for an area"""
    area = serializers.IntegerField()
    days = serializers.ListField(
        child=serializers.ChoiceField(choices=TimeSlot.DAYS_OF_WEEK),
        allow_empty=False
    )
    time_slots = serializers.ListField(
        child=serializers.ChoiceField(choices=TimeSlot.TIME_SLOTS),
        allow_empty=False
    )
    is_active = serializers.BooleanField(default=True)

    def validate_area(self, value):
        """Validate that area exists"""
        if not Area.objects.filter(id=value).exists():
            raise serializers.ValidationError("Area does not exist.")
        return value

    def create(self, validated_data):
        """Create multiple time slots"""
        area = Area.objects.get(id=validated_data['area'])
        days = validated_data['days']
        time_slots = validated_data['time_slots']
        is_active = validated_data.get('is_active', True)
        
        created_slots = []
        skipped_slots = []
        
        for day in days:
            for time_slot in time_slots:
                # Check if already exists
                if TimeSlot.objects.filter(
                    area=area,
                    day_of_week=day,
                    time_slot=time_slot
                ).exists():
                    skipped_slots.append(f"{day} - {time_slot}")
                else:
                    slot = TimeSlot.objects.create(
                        area=area,
                        day_of_week=day,
                        time_slot=time_slot,
                        is_active=is_active
                    )
                    created_slots.append(slot)
        
        return {
            'created': created_slots,
            'skipped': skipped_slots
        }