
from django.urls import path
from . import views

urlpatterns = [
    path('api/register/user', views.RegisterUser.as_view(), name = 'register'),
    path('api/public/products/search/', views.Products.as_view(), name = 'products'),
    path('api/public/login/',views.CustomTokenObtainView.as_view(), name = 'login'),
    path('api/auth/consumer/cart', views.ConsumerCart.as_view(), name='consumer-cart'),
    path('api/auth/consumer/order', views.CustomerOrder.as_view(), name='consumer-post-order'),
    path('api/auth/seller/order', views.SellerProducts.as_view(), name='seller-products'),
    path('api/auth/seller/order/<int:product_id>/', views.SellerProductsUpdate.as_view(), name='seller-products-update-delete'),
    path('api/admin/sales-summary', views.AdminSalesSummary.as_view(), name='admin-sales-summary'),
    path('api/admin/users', views.AdminGetAllusers.as_view(), name='admin-all-users'),
]
