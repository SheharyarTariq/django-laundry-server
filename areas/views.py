from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Area, Postcode, TimeSlot
from .serializers import ( AreaSerializer, AreaListSerializer, AreaDetailSerializer, PostcodeSerializer, TimeSlotSerializer, TimeSlotToggleSerializer )

# ============= AREA VIEWS =============

class AreaListCreateView(APIView):
    """List all areas or create a new area"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        tags=["Areas"],
        responses={200: AreaListSerializer(many=True)}
    )
    def get(self, request):
        """Get all areas - returns only id and name"""
        areas = Area.objects.all()
        serializer = AreaListSerializer(areas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        tags=["Areas"],
        request_body=AreaSerializer,
        responses={201: AreaSerializer()}
    )
    def post(self, request):
        """Create a new area with default time slots (inactive)"""
        serializer = AreaSerializer(data=request.data)
        if serializer.is_valid():
            try:
                area = serializer.save()
                slots_count = area.time_slots.count()
                return Response({
                    'message': f'Area created successfully with {slots_count} time slots (all inactive).',
                    'area': serializer.data,
                    'time_slots_created': slots_count
                }, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({
                    'error': 'An area with this name already exists.'
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AreaDetailView(APIView):
    """Retrieve, update or delete an area"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        tags=["Areas"],
        responses={200: AreaDetailSerializer()}
    )
    def get(self, request, pk):
        """Get area details with all associated postcodes and time slots"""
        area = get_object_or_404(Area, pk=pk)
        serializer = AreaDetailSerializer(area)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        tags=["Areas"],
        request_body=AreaSerializer,
        responses={200: AreaSerializer()}
    )
    def put(self, request, pk):
        """Update an area"""
        area = get_object_or_404(Area, pk=pk)
        serializer = AreaSerializer(area, data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    'message': 'Area updated successfully.',
                    'area': serializer.data
                }, status=status.HTTP_200_OK)
            except IntegrityError:
                return Response({
                    'error': 'An area with this name already exists.'
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        tags=["Areas"],
        request_body=AreaSerializer,
        responses={200: AreaSerializer()}
    )
    def patch(self, request, pk):
        """Partially update an area"""
        area = get_object_or_404(Area, pk=pk)
        serializer = AreaSerializer(area, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    'message': 'Area updated successfully.',
                    'area': serializer.data
                }, status=status.HTTP_200_OK)
            except IntegrityError:
                return Response({
                    'error': 'An area with this name already exists.'
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        tags=["Areas"],
        responses={204: 'Area deleted successfully'}
    )
    def delete(self, request, pk):
        """Delete an area"""
        area = get_object_or_404(Area, pk=pk)
        
        # Check if area has associated postcodes
        if area.postcodes.exists():
            return Response({
                'error': f'Cannot delete area. It has {area.postcodes.count()} associated postcode(s). Please delete or reassign them first.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        area.delete()
        return Response({
            'message': 'Area deleted successfully.'
        }, status=status.HTTP_204_NO_CONTENT)

# ============= POSTCODE VIEWS =============

class PostcodeListCreateView(APIView):
    """List all postcodes or create a new postcode"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        tags=["Postcodes"],
        manual_parameters=[
            openapi.Parameter(
                'area',
                openapi.IN_QUERY,
                description="Filter postcodes by area ID",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={200: PostcodeSerializer(many=True)}
    )
    def get(self, request):
        """Get all postcodes with optional area filter"""
        area_id = request.query_params.get('area')
        
        if area_id:
            postcodes = Postcode.objects.filter(area_id=area_id)
        else:
            postcodes = Postcode.objects.all()
        
        serializer = PostcodeSerializer(postcodes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        tags=["Postcodes"],
        request_body=PostcodeSerializer,
        responses={201: PostcodeSerializer()}
    )
    def post(self, request):
        """Create a new postcode"""
        serializer = PostcodeSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    'message': 'Postcode created successfully.',
                    'postcode': serializer.data
                }, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({
                    'error': 'A postcode with this value already exists.'
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostcodeDetailView(APIView):
    """Retrieve, update or delete a postcode"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        tags=["Postcodes"],
        responses={200: PostcodeSerializer()}
    )
    def get(self, request, pk):
        """Get postcode details"""
        postcode = get_object_or_404(Postcode, pk=pk)
        serializer = PostcodeSerializer(postcode)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        tags=["Postcodes"],
        request_body=PostcodeSerializer,
        responses={200: PostcodeSerializer()}
    )
    def put(self, request, pk):
        """Update a postcode"""
        postcode = get_object_or_404(Postcode, pk=pk)
        serializer = PostcodeSerializer(postcode, data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    'message': 'Postcode updated successfully.',
                    'postcode': serializer.data
                }, status=status.HTTP_200_OK)
            except IntegrityError:
                return Response({
                    'error': 'A postcode with this value already exists.'
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        tags=["Postcodes"],
        request_body=PostcodeSerializer,
        responses={200: PostcodeSerializer()}
    )
    def patch(self, request, pk):
        """Partially update a postcode"""
        postcode = get_object_or_404(Postcode, pk=pk)
        serializer = PostcodeSerializer(postcode, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    'message': 'Postcode updated successfully.',
                    'postcode': serializer.data
                }, status=status.HTTP_200_OK)
            except IntegrityError:
                return Response({
                    'error': 'A postcode with this value already exists.'
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        tags=["Postcodes"],
        responses={204: 'Postcode deleted successfully'}
    )
    def delete(self, request, pk):
        """Delete a postcode"""
        postcode = get_object_or_404(Postcode, pk=pk)
        postcode.delete()
        return Response({
            'message': 'Postcode deleted successfully.'
        }, status=status.HTTP_204_NO_CONTENT)

class AreaTimeSlotListView(APIView):
    """List all time slots for a specific area"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        tags=["Time Slots"],
        manual_parameters=[
            openapi.Parameter(
                'day',
                openapi.IN_QUERY,
                description="Filter by day of week (0=Monday, 6=Sunday)",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'is_active',
                openapi.IN_QUERY,
                description="Filter by active status (true/false)",
                type=openapi.TYPE_BOOLEAN
            )
        ],
        responses={200: TimeSlotSerializer(many=True)}
    )
    def get(self, request, area_pk):
        """Get all time slots for an area with optional filters"""
        area = get_object_or_404(Area, pk=area_pk)
        time_slots = area.time_slots.all()
        
        # Filter by day if provided
        day = request.query_params.get('day')
        if day is not None:
            try:
                day = int(day)
                if 0 <= day <= 6:
                    time_slots = time_slots.filter(day_of_week=day)
            except ValueError:
                pass
        
        # Filter by active status if provided
        is_active = request.query_params.get('is_active')
        if is_active is not None:
            is_active_bool = is_active.lower() in ['true', '1', 'yes']
            time_slots = time_slots.filter(is_active=is_active_bool)
        
        serializer = TimeSlotSerializer(time_slots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TimeSlotToggleView(APIView):
    """Toggle active status of a specific time slot"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        tags=["Time Slots"],
        request_body=TimeSlotToggleSerializer,
        responses={
            200: openapi.Response(
                description="Time slot status updated",
                schema=TimeSlotSerializer()
            )
        }
    )
    def patch(self, request, area_pk, slot_pk):
        """Toggle or set the active status of a time slot"""
        area = get_object_or_404(Area, pk=area_pk)
        time_slot = get_object_or_404(TimeSlot, pk=slot_pk, area=area)
        
        serializer = TimeSlotToggleSerializer(data=request.data)
        if serializer.is_valid():
            time_slot.is_active = serializer.validated_data['is_active']
            time_slot.save()
            
            response_serializer = TimeSlotSerializer(time_slot)
            return Response({
                'message': f'Time slot {"activated" if time_slot.is_active else "deactivated"} successfully.',
                'time_slot': response_serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DayTimeSlotsBulkToggleView(APIView):
    """Activate or deactivate all time slots for a specific day"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        tags=["Time Slots"],
        request_body=TimeSlotToggleSerializer,
        responses={
            200: openapi.Response(
                description="All time slots for the day updated",
                examples={
                    'application/json': {
                        'message': 'All time slots for Monday activated successfully.',
                        'updated_count': 4
                    }
                }
            )
        }
    )
    def patch(self, request, area_pk, day):
        """Activate or deactivate all time slots for a specific day"""
        area = get_object_or_404(Area, pk=area_pk)
        
        # Validate day
        if not (0 <= day <= 6):
            return Response({
                'error': 'Invalid day. Must be between 0 (Monday) and 6 (Sunday).'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = TimeSlotToggleSerializer(data=request.data)
        if serializer.is_valid():
            is_active = serializer.validated_data['is_active']
            
            # Update all time slots for this day
            time_slots = TimeSlot.objects.filter(area=area, day_of_week=day)
            updated_count = time_slots.update(is_active=is_active)
            
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            day_name = day_names[day]
            
            return Response({
                'message': f'All time slots for {day_name} {"activated" if is_active else "deactivated"} successfully.',
                'updated_count': updated_count
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
