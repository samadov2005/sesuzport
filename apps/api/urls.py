from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Auth & Profile
    path('auth/login/', views.auth_login_or_register, name='auth_login'),
    path('auth/register/', views.auth_login_or_register, name='auth_register'),
    path('user/profile/', views.get_user_profile, name='user_profile'),

    # Complaints
    path('complaints/create/', views.create_complaint, name='complaint_create'),
    path('complaints/my/', views.get_my_complaints, name='complaints_my'),
    path('complaints/<str:ticket_id>/', views.get_complaint_detail, name='complaint_detail'),

    # Stores
    path('stores/', views.get_stores_list, name='stores_list'),

    # Cashback
    path('cashback/', views.get_cashback_info, name='cashback_info'),

    # Rights & Support
    path('rights/', views.get_rights_list, name='rights_list'),
    path('support/', views.get_support_info, name='support_info'),
]
