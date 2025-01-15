from django.urls import path
from django.conf import settings
from . import views
from .views import AddToCart, ViewCartView, RemoveFromCart, UpdateCartView, PlaceOrderView, OrderSuccessView, SearchResultsView, MyOrdersView, logout_view
from django.conf.urls.static import static

urlpatterns = [
    # Root URL for the landing page
    path('', views.Landing_page.as_view(), name='landing_page'),
    
    # Authentication URLs
    path('login/', views.Login_Page.as_view(), name='login'),
    path('signup/', views.Signup_View.as_view(), name='signup'),
    
    # Home Page URL
    path('home/', views.HomePage.as_view(), name='home_page'),
    
    # Category-related URLs
    path('categories/', views.Category_List.as_view(), name='categories'),
    path('brands/', views.Brand_List.as_view(), name='brand_list'),
    path('categories/<int:pk>/', views.CategoryBrandView.as_view(), name='category_brands'),
    
    # Product-related URLs
    path('products/<int:brand_id>/', views.Product_List.as_view(), name='product_list'),
    
    # Cart-related URLs
    path('cart/', ViewCartView.as_view(), name='view_cart'),  # View cart
    path('add/<int:product_id>/', AddToCart.as_view(), name='add_to_cart'),
    path('remove/<int:product_id>/', RemoveFromCart.as_view(), name='remove_from_cart'),
    path('update/<int:product_id>/', UpdateCartView.as_view(), name='update_cart'),

    # Order-related URLs
    path('place-order/', PlaceOrderView.as_view(), name='place_order'),  # To place order without a specific product,  # To place order without a specific product
    path('place-order/<int:product_id>/', PlaceOrderView.as_view(), name='place_order_with_product'),  # To place order with specific product

    path('order-success/', OrderSuccessView.as_view(), name='order_success'),  # Redirect to order success
    path('my-orders/', MyOrdersView.as_view(), name='my_orders'),

    # Search-related URLs
    path('search/', SearchResultsView.as_view(), name='search_results'),

    # Change password
    path('change-password/', views.change_password, name='change_password'),

    # Logout 
    path('logout/', logout_view, name='logout')
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)