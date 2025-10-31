from django.db import IntegrityError
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Area, Postcode, TimeSlot
from .serializers import (
    AreaSerializer, AreaListSerializer, AreaDetailSerializer,
    PostcodeSerializer, PostcodeListSerializer, TimeSlotBulkCreateSerializer, TimeSlotSerializer
)


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
        """Create a new area"""
        serializer = AreaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Area created successfully.',
                'area': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AreaDetailView(APIView):
    """Retrieve, update or delete an area"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        tags=["Areas"],
        responses={200: AreaDetailSerializer()}
    )
    def get(self, request, pk):
        """Get area details with all associated postcodes"""
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
            serializer.save()
            return Response({
                'message': 'Area updated successfully.',
                'area': serializer.data
            }, status=status.HTTP_200_OK)
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
            serializer.save()
            return Response({
                'message': 'Area updated successfully.',
                'area': serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        tags=["Areas"],
        responses={204: 'Area deleted successfully'}
    )
    def delete(self, request, pk):
        """Delete an area"""
        area = get_object_or_404(Area, pk=pk)
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
            serializer.save()
            return Response({
                'message': 'Postcode created successfully.',
                'postcode': serializer.data
            }, status=status.HTTP_201_CREATED)
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
            serializer.save()
            return Response({
                'message': 'Postcode updated successfully.',
                'postcode': serializer.data
            }, status=status.HTTP_200_OK)
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
            serializer.save()
            return Response({
                'message': 'Postcode updated successfully.',
                'postcode': serializer.data
            }, status=status.HTTP_200_OK)
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
    
class TimeSlotListCreateView(APIView):
    """List all time slots or create a new time slot"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        tags=["Time Slots"],
        manual_parameters=[
            openapi.Parameter(
                'area',
                openapi.IN_QUERY,
                description="Filter time slots by area ID",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'day_of_week',
                openapi.IN_QUERY,
                description="Filter time slots by day of week",
                type=openapi.TYPE_STRING
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
    def get(self, request):
        """Get all time slots with optional filters"""
        queryset = TimeSlot.objects.all()
        
        # Apply filters
        area_id = request.query_params.get('area')
        day_of_week = request.query_params.get('day_of_week')
        is_active = request.query_params.get('is_active')
        
        if area_id:
            queryset = queryset.filter(area_id=area_id)
        if day_of_week:
            queryset = queryset.filter(day_of_week=day_of_week)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        serializer = TimeSlotSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        tags=["Time Slots"],
        request_body=TimeSlotSerializer,
        responses={201: TimeSlotSerializer()}
    )
    def post(self, request):
        """Create a new time slot"""
        serializer = TimeSlotSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    'message': 'Time slot created successfully.',
                    'time_slot': serializer.data
                }, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({
                    'error': 'This time slot already exists for the selected area and day.'
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TimeSlotBulkCreateView(APIView):
    """Create multiple time slots at once"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        tags=["Time Slots"],
        request_body=TimeSlotBulkCreateSerializer,
        responses={201: 'Time slots created successfully'}
    )
    def post(self, request):
        """Create multiple time slots for specific days"""
        serializer = TimeSlotBulkCreateSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            created_count = len(result['created'])
            skipped_count = len(result['skipped'])
            
            response_data = {
                'message': f'Successfully created {created_count} time slot(s).',
                'created_count': created_count,
                'skipped_count': skipped_count,
            }
            
            if result['skipped']:
                response_data['skipped'] = result['skipped']
                response_data['message'] += f' {skipped_count} slot(s) were skipped (already exist).'
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TimeSlotDetailView(APIView):
    """Retrieve, update or delete a time slot"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        tags=["Time Slots"],
        responses={200: TimeSlotSerializer()}
    )
    def get(self, request, pk):
        """Get time slot details"""
        time_slot = get_object_or_404(TimeSlot, pk=pk)
        serializer = TimeSlotSerializer(time_slot)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        tags=["Time Slots"],
        request_body=TimeSlotSerializer,
        responses={200: TimeSlotSerializer()}
    )
    def put(self, request, pk):
        """Update a time slot"""
        time_slot = get_object_or_404(TimeSlot, pk=pk)
        serializer = TimeSlotSerializer(time_slot, data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    'message': 'Time slot updated successfully.',
                    'time_slot': serializer.data
                }, status=status.HTTP_200_OK)
            except IntegrityError:
                return Response({
                    'error': 'This time slot already exists for the selected area and day.'
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        tags=["Time Slots"],
        request_body=TimeSlotSerializer,
        responses={200: TimeSlotSerializer()}
    )
    def patch(self, request, pk):
        """Partially update a time slot"""
        time_slot = get_object_or_404(TimeSlot, pk=pk)
        serializer = TimeSlotSerializer(time_slot, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    'message': 'Time slot updated successfully.',
                    'time_slot': serializer.data
                }, status=status.HTTP_200_OK)
            except IntegrityError:
                return Response({
                    'error': 'This time slot already exists for the selected area and day.'
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        tags=["Time Slots"],
        responses={204: 'Time slot deleted successfully'}
    )
    def delete(self, request, pk):
        """Delete a time slot"""
        time_slot = get_object_or_404(TimeSlot, pk=pk)
        time_slot.delete()
        return Response({
            'message': 'Time slot deleted successfully.'
        }, status=status.HTTP_204_NO_CONTENT)
