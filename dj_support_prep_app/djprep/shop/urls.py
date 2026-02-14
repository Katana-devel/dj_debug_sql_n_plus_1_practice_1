from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/recent/', views.products_by_date, name='products_recent'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/dashboard/', views.order_dashboard, name='order_dashboard'),
    path('categories/<int:pk>/products/', views.category_products, name='category_products'),
]
