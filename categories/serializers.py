from rest_framework import serializers
from .models import Category, Item

class ItemListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing items"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Item
        fields = ['id', 'name', 'category_name', 'washing_price', 'drycleaning_price', 'pieces']

class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category CRUD operations"""
    items = ItemListSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'items', 'description', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_name(self, value):
        """Validate category name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Category name is required.")
        
        value = value.strip()
        
        # Check if category name already exists (for create operation)
        if not self.instance:  # Only check during creation
            if Category.objects.filter(name__iexact=value).exists():
                raise serializers.ValidationError(f"Category '{value}' already exists.")
        else:  # During update, exclude the current instance
            if Category.objects.filter(name__iexact=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError(f"Category '{value}' already exists.")
        
        return value

class CategoryDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for category with all items"""
    items = ItemListSerializer(many=True, read_only=True)  # ← This fetches all items
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'items', 'created_at', 'updated_at']

class CategoryListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing categories"""
    
    class Meta:
        model = Category
        fields = ['id', 'name']

class ItemSerializer(serializers.ModelSerializer):
    """Serializer for Item CRUD operations"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Item
        fields = ['id', 'category', 'category_name', 'name', 'description', 
                  'washing_price', 'drycleaning_price', 'pieces', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_name(self, value):
        """Validate item name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Item name is required.")
        return value.strip()
    
    def validate_washing_price(self, value):
        """Validate washing price"""
        if value < 0:
            raise serializers.ValidationError("Washing price cannot be negative.")
        return value
    
    def validate_drycleaning_price(self, value):
        """Validate drycleaning price"""
        if value < 0:
            raise serializers.ValidationError("Drycleaning price cannot be negative.")
        return value
    
    def validate_pieces(self, value):
        """Validate pieces"""
        if value < 1:
            raise serializers.ValidationError("Pieces must be at least 1.")
        return value
    
    def validate(self, data):
        """Validate unique constraint for category and name"""
        category = data.get('category')
        name = data.get('name', '').strip()
        
        # Check if item with same name exists in this category
        if not self.instance:  # Only check during creation
            if Item.objects.filter(category=category, name__iexact=name).exists():
                raise serializers.ValidationError({
                    'name': f"Item '{name}' already exists in this category."
                })
        else:  # During update, exclude the current instance
            if Item.objects.filter(category=category, name__iexact=name).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError({
                    'name': f"Item '{name}' already exists in this category."
                })
        
        return data

class ItemListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing items"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Item
        fields = ['id', 'name', 'category_name', 'washing_price', 'drycleaning_price', 'pieces']

class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category CRUD operations"""
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_name(self, value):
        """Validate category name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Category name is required.")
        
        value = value.strip()
        
        # Check if category name already exists (for create operation)
        if not self.instance:  # Only check during creation
            if Category.objects.filter(name__iexact=value).exists():
                raise serializers.ValidationError(f"Category '{value}' already exists.")
        else:  # During update, exclude the current instance
            if Category.objects.filter(name__iexact=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError(f"Category '{value}' already exists.")
        
        return value