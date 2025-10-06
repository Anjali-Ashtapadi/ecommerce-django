from django.urls import path
from . import views

urlpatterns=[
    path('',views.homepage,name='home'),
    path('store/',views.store,name='store'),
    path('store/category/<slug:category_slug>/',views.store,name='product_by_category'),
    path('store/category/<slug:category_slug>/<slug:product_slug>/',views.product_detail,name='product_detail'),
    path('cart/',views.cart,name='cart'),
    path('add_to_cart/<int:product_id>/',views.add_to_cart,name='add_to_cart'),
    path('remove_cart/<int:product_id>/<int:cart_item_id>/',views.remove_cart,name='remove_cart'),
     path('remove_total_cart/<int:product_id>/<int:cart_item_id>/',views.remove_total_cart,name='remove_total_cart'),
     path('store/search',views.search,name='search'),

    
]