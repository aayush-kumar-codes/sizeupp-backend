from rest_framework import serializers
from product.models import *
from dashboard.models import Reviews







class SizeQuantityPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SizeQuantityPrice
        fields = "__all__"


class subsubcategory_serializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSubSubCategory
        fields = "__all__"

class subcategory_serializer(serializers.ModelSerializer):
    subsubcategories = subsubcategory_serializer(many=True, read_only=True)

    class Meta:
        model = ProductSubCategory
        fields = "__all__"


class ColourFamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = ColourFamily
        fields = '__all__'
        
        



class category_serializer(serializers.ModelSerializer):
    subcategories = subcategory_serializer(many=True, read_only=True)

    class Meta:
        model = ProductCategory
        fields = "__all__"


class ProductImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = ('img',)

class product_serializer(serializers.ModelSerializer):
    category = category_serializer()
    subcategory = subcategory_serializer()
    subsubcategory = subsubcategory_serializer()
    sqp = SizeQuantityPriceSerializer(many=True, read_only=True)
    images = ProductImagesSerializer(many=True, read_only=True, source='productimages_set')  # Assuming 'productimages_set' is the related name
    color_family = ColourFamilySerializer()
    class Meta:
        model = Product
        fields = "__all__"
        
        
# class size_quantity_price_serializer(serializers.ModelSerializer):
#     class Meta:
#         model = SizeQuantityPrice
#         fields = "__all__"
    
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviews
        fields = "__all__"
        



class DiscountCouponSerializers(serializers.ModelSerializer):
    class Meta:
        model = DiscountCoupon
        fields = '__all__'

class DiscountEventsSerialize(serializers.ModelSerializer):
    subsubcategory_products = serializers.SerializerMethodField()

    class Meta:
        model = DiscountEvents
        fields = '__all__'
        
    def get_subsubcategory_products(self, obj):
        # Get the products related to the subsubcategories in the DiscountEvent
        products = Product.objects.filter(subsubcategory__in=obj.subsubcategory.all())
        product_serialize = product_serializer(products, many=True)
        return product_serialize.data
