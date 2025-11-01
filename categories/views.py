from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Category, Item
from .serializers import CategoryDetailSerializer, CategorySerializer, CategoryListSerializer, ItemListSerializer, ItemSerializer


class CategoryListCreateView(APIView):
    """List all categories or create a new category"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        tags=["Categories"],
        responses={200: CategoryListSerializer(many=True)}
    )
    def get(self, request):
        """Get all categories"""
        categories = Category.objects.all()
        serializer = CategoryListSerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        tags=["Categories"],
        request_body=CategorySerializer,
        responses={201: CategorySerializer()}
    )
    def post(self, request):
        """Create a new category"""
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    'message': 'Category created successfully.',
                    'category': serializer.data
                }, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({
                    'error': 'A category with this name already exists.'
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryDetailView(APIView):
    """Retrieve, update or delete a category"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        tags=["Categories"],
        responses={200: CategoryDetailSerializer()}
    )
    def get(self, request, pk):
        """Get category details"""
        category = get_object_or_404(Category, pk=pk)
        serializer = CategoryDetailSerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        tags=["Categories"],
        request_body=CategorySerializer,
        responses={200: CategorySerializer()}
    )
    def put(self, request, pk):
        """Update a category"""
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    'message': 'Category updated successfully.',
                    'category': serializer.data
                }, status=status.HTTP_200_OK)
            except IntegrityError:
                return Response({
                    'error': 'A category with this name already exists.'
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        tags=["Categories"],
        request_body=CategorySerializer,
        responses={200: CategorySerializer()}
    )
    def patch(self, request, pk):
        """Partially update a category"""
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    'message': 'Category updated successfully.',
                    'category': serializer.data
                }, status=status.HTTP_200_OK)
            except IntegrityError:
                return Response({
                    'error': 'A category with this name already exists.'
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        tags=["Categories"],
        responses={204: 'Category deleted successfully'}
    )
    def delete(self, request, pk):
        """Delete a category"""
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        return Response({
            'message': 'Category deleted successfully.'
        }, status=status.HTTP_204_NO_CONTENT)
    
class ItemListCreateView(APIView):
    """List all items or create a new item"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        tags=["Items"],
        manual_parameters=[
            openapi.Parameter(
                'category',
                openapi.IN_QUERY,
                description="Filter items by category ID",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={200: ItemListSerializer(many=True)}
    )
    def get(self, request):
        """Get all items with optional category filter"""
        category_id = request.query_params.get('category')
        
        if category_id:
            items = Item.objects.filter(category_id=category_id)
        else:
            items = Item.objects.all()
        
        serializer = ItemListSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        tags=["Items"],
        request_body=ItemSerializer,
        responses={201: ItemSerializer()}
    )
    def post(self, request):
        """Create a new item"""
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    'message': 'Item created successfully.',
                    'item': serializer.data
                }, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({
                    'error': 'An item with this name already exists in this category.'
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ItemDetailView(APIView):
    """Retrieve, update or delete an item"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        tags=["Items"],
        responses={200: ItemSerializer()}
    )
    def get(self, request, pk):
        """Get item details"""
        item = get_object_or_404(Item, pk=pk)
        serializer = ItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        tags=["Items"],
        request_body=ItemSerializer,
        responses={200: ItemSerializer()}
    )
    def put(self, request, pk):
        """Update an item"""
        item = get_object_or_404(Item, pk=pk)
        serializer = ItemSerializer(item, data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    'message': 'Item updated successfully.',
                    'item': serializer.data
                }, status=status.HTTP_200_OK)
            except IntegrityError:
                return Response({
                    'error': 'An item with this name already exists in this category.'
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        tags=["Items"],
        request_body=ItemSerializer,
        responses={200: ItemSerializer()}
    )
    def patch(self, request, pk):
        """Partially update an item"""
        item = get_object_or_404(Item, pk=pk)
        serializer = ItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    'message': 'Item updated successfully.',
                    'item': serializer.data
                }, status=status.HTTP_200_OK)
            except IntegrityError:
                return Response({
                    'error': 'An item with this name already exists in this category.'
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        tags=["Items"],
        responses={204: 'Item deleted successfully'}
    )
    def delete(self, request, pk):
        """Delete an item"""
        item = get_object_or_404(Item, pk=pk)
        item.delete()
        return Response({
            'message': 'Item deleted successfully.'
        }, status=status.HTTP_204_NO_CONTENT)
