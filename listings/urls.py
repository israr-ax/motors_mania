from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import CustomLoginView
urlpatterns = [
    path('', views.home, name='home'),
    path('post/', views.post_vehicle, name='post_vehicle'),
    path('toggle-status/<int:vehicle_id>/', views.toggle_status, name='toggle_status'),
    path('favorite/<int:vehicle_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('vehicle/<int:pk>/', views.vehicle_detail, name='vehicle_detail'),

    path('chat/', views.chat_view, name='chat_home'),  # Chat home without user
    path('chat/<int:user_id>/', views.chat_view, name='start_chat'),

    path('signup/', views.signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='listings/auth.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='auth'), name='logout'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('vehicle/<int:vehicle_id>/update-status/', views.update_status, name='update_status'),
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('vehicle/update-status/<int:vehicle_id>/', views.update_vehicle_status, name='update_vehicle_status'),
    path('edit-vehicle/<int:vehicle_id>/', views.edit_vehicle, name='edit_vehicle'),
    
    path('vehicle/<int:vehicle_id>/images/', views.edit_vehicle_image, name='edit_vehicle_image'),
    
    path('vehicle/<int:vehicle_id>/images/json/', views.get_vehicle_images_json, name='vehicle_images_json'),
    
    
    path('saved/', views.saved_vehicles, name='saved_vehicles'),
    path('delete-vehicle/<int:vehicle_id>/', views.delete_vehicle, name='delete_vehicle'),
    
    path('vehicle/image/<int:image_id>/delete/', views.delete_vehicle_image, name='delete_vehicle_image'),

    path('edit-vehicle/', views.edit_vehicle, name='edit_vehicle'),
    path('profile/', views.profile_view, name='profile'),
    path('auth/', views.auth_view, name='auth'),










]
