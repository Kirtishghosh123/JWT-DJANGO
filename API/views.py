from itertools import product
from datetime import datetime
from django.db.models import Q, Sum, F
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from . import models
from . import serializers
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from .models import CustomUser, CartProduct, Cart, Product, Order, Category
from .permissions import ConsumerPermissions, SellerPermissions


# Create your views here.

class RegisterUser(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = serializers.UserSerializer

class Products(APIView):

    permission_classes = [IsAuthenticated]
    def get(self, request):
        product_keyword = request.query_params.get('product_name','')
        category_keyword = request.query_params.get('category','')
        products = models.Product.objects.filter(Q(product_name__iexact=product_keyword)|Q(category__category_name__iexact=category_keyword))
        if products != []:
            serializer = serializers.ProductSerializer(products, many=True)
            return Response(serializer.data, status = status.HTTP_200_OK)
        else:
            return Response({"message":"No such Products available"}, status=status.HTTP_404_NOT_FOUND)

class CustomTokenObtainView(TokenObtainPairView):
    serializer_class = serializers.CustomTokenObtainSerializer


class ConsumerCart(APIView):

    permission_classes = [ConsumerPermissions]

    def get(self, request):
        username = request.user.username
        if username is not None:
            products = CartProduct.objects.filter(cart__user__username=username,cart__user__roles__role__iexact= 'consumer').values_list('product__product_name')
            serializer = serializers.CartProductSerializer(products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({
            "error_message" : "Enter correct details"
        }, status=status.HTTP_404_NOT_FOUND)


    def post(self, request):

        custom_user = CustomUser.objects.get(username=request.user.username,id=request.user.id)
        serializer = serializers.CartProductSerializer(data=request.data)
        if serializer.initial_data['product_id'] is not None and serializer.initial_data['quantity'] is not None:
            product = Product.objects.filter(id=serializer.initial_data['product_id']).first()

            if serializer.is_valid():

                quantity = serializer.validated_data['quantity']
                cart, created = Cart.objects.get_or_create(user=custom_user)
                cart_product = CartProduct(cart=cart,product=product,quantity=quantity)
                cart_product.save()
                serializer = serializers.CartProductSerializer(cart_product)
                return Response({"message":"Product has been added"}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error":"check data"}, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request):

        product = Product.objects.filter(id = request.data.get('product_id')).first()
        quantity = request.data.get('quantity')
        if not product:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        custom_user = CustomUser.objects.get(username=request.user.username)
        serializer = serializers.CartProductSerializer(product,data=request.data)
        if serializer.is_valid():
            cart, created = Cart.objects.get_or_create(user=custom_user)
            cart_product = CartProduct.objects.filter(cart=cart, product=product).first()
            if cart_product:
                if quantity == 0:
                    cart_product.delete()
                    return Response({"message":"Product has been removed from cart"}, status=status.HTTP_200_OK)
                else:
                    cart_product.quantity = quantity
                    cart_product.save()

                return Response({
                    "message":"Updated Successfully",
                    "quantity" : quantity
                }, status=status.HTTP_200_OK)
            else:
                if quantity > 0:
                    cart_product = CartProduct.objects.create(cart=cart, product=product, quantity=quantity)
                    return Response({"message":"Product has been added"}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error":"Product not in cart, add product quantity."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):

        product = Product.objects.filter(id=request.data.get('product_id')).first()
        if product is None:
            return Response({"message":"Give specific product id"}, status=status.HTTP_400_BAD_REQUEST)
        custom_user = CustomUser.objects.get(username = request.user.username)
        if custom_user is not None:
            cart, created = Cart.objects.get_or_create(user=custom_user)
            cart_product = CartProduct.objects.filter(cart=cart, product=product).first()
            if cart_product:
                cart_product.delete()
                return Response({"message":"product has been removed"}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"message":"cart is None"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"User not found"}, status=status.HTTP_404_NOT_FOUND)


class CustomerOrder(APIView):

    def post(self, request):
        custom_user = CustomUser.objects.get(username=request.user.username)
        if custom_user:
            cart, created = Cart.objects.get_or_create(user=custom_user)
            cart_product = CartProduct.objects.filter(cart=cart)
            if not cart_product.exists():
                return Response({"message":"Cart Product Doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                total_amount = cart_product.aggregate(total=Sum('product__price'))
                order = Order.objects.create(
                    user = custom_user,
                    total_amount=total_amount['total'],
                    order_date = datetime.now(),
                    status = True
                )
                order.save()
                return Response({"message":"Order has been made"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message":"User not found"}, status=status.HTTP_404_NOT_FOUND)


class SellerProducts(APIView):

    permission_classes = [SellerPermissions]

    def get(self, request):
        username = request.user.username
        if username is not None:
            products = Product.objects.filter(seller__username=username)
            if products:
                serializer = serializers.ProductSerializer(products, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"message":"Product needs to be added"},status=status.HTTP_400_BAD_REQUEST)
        return Response({"message":"Username is empty"}, status=status.HTTP_400_BAD_REQUEST)


    def post(self, request):
        username =request.user.username
        if username is not None:
            custom_user = CustomUser.objects.filter(username=username).first()
            if custom_user is not None:
                category, create = Category.objects.get_or_create(id=request.data.get('product_id'))
                if custom_user:
                    product = Product(product_name = request.data.get('product_name'),description = request.data.get('description'),price= request.data.get('price'), category = category, stock_quantity = request.data.get('stock_quantity'), seller=custom_user )
                    product.save()
                    return Response({"message":"Product has been added to db by seller"}, status=status.HTTP_201_CREATED)
                elif custom_user.DoesNotExist:
                    return Response({"message":"User Does not exist"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message":"User doesnot exist"}, status = status.HTTP_404_NOT_FOUND)
        return Response({"message":"Give proper username"}, status = status.HTTP_400_BAD_REQUEST)


class SellerProductsUpdate(APIView):
    permission_classes = [SellerPermissions]

    def put(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error":"Product deosn't exist"}, status=status.HTTP_404_NOT_FOUND)

        serializer = serializers.ProductSerializer(product,data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product deosn't exist"}, status=status.HTTP_404_NOT_FOUND)

        product.delete()
        return Response({"message":"Product has been deleted"}, status=status.HTTP_204_NO_CONTENT)

class AdminGetAllusers(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        users = CustomUser.objects.all()
        serializer = serializers.UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminSalesSummary(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]
    def get(self, request):
        product = Product.objects.annotate(total_sales=Sum(F('stock_quantity')*F('price'))).values('seller__username','category__category_name','total_sales')
        print(f"Products: {product}")
        product_list = []
        for i in product:
            product_list.append(i)

        # serializer = serializers.ProductSerializer(product, many=True)
        return Response(product_list, status=status.HTTP_200_OK)

