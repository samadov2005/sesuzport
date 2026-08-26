import json
import pytest
from django.test import Client
from apps.users.models import TelegramUser, UserRole
from apps.stores.models import Store, SafetyStatus
from apps.rights.models import ConsumerRight


@pytest.mark.django_db
def test_mobile_auth_login_and_profile():
    client = Client()
    
    # 1. Register / Login
    payload = {
        'phone_number': '+998901234567',
        'full_name': 'Ali Valiyev',
        'language': 'uz'
    }
    response = client.post('/api/v1/auth/login/', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert 'token' in data
    token = data['token']
    assert data['user']['full_name'] == 'Ali Valiyev'
    
    # 2. Get Profile with token
    profile_resp = client.get('/api/v1/user/profile/', HTTP_AUTHORIZATION=f'Bearer {token}')
    assert profile_resp.status_code == 200
    pdata = profile_resp.json()
    assert pdata['success'] is True
    assert pdata['user']['phone_number'] == '+998901234567'


@pytest.mark.django_db
def test_mobile_complaint_lifecycle():
    client = Client()
    
    # Register user
    auth_resp = client.post('/api/v1/auth/login/', data=json.dumps({
        'phone_number': '+998991112233',
        'full_name': 'Hasan Rahimov'
    }), content_type='application/json')
    token = auth_resp.json()['token']
    
    # Create complaint
    complaint_data = {
        'description': "Muddati 2 oy o'tgan sut mahsuloti sotilmoqda",
        'latitude': 41.311081,
        'longitude': 69.240562,
        'image': 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/'
    }
    resp = client.post(
        '/api/v1/complaints/create/',
        data=json.dumps(complaint_data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token}'
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data['success'] is True
    assert 'ticket_id' in data
    ticket_id = data['ticket_id']
    
    # Get user's complaints
    list_resp = client.get('/api/v1/complaints/my/', HTTP_AUTHORIZATION=f'Bearer {token}')
    assert list_resp.status_code == 200
    assert list_resp.json()['count'] == 1
    assert list_resp.json()['complaints'][0]['ticket_id'] == ticket_id


@pytest.mark.django_db
def test_mobile_stores_and_rights_endpoints():
    client = Client()
    
    # Create sample store
    Store.objects.create(
        name="Korzinka Test",
        address="Toshkent sh.",
        latitude=41.31,
        longitude=69.24,
        safety_status=SafetyStatus.GREEN
    )
    
    # Create sample right
    ConsumerRight.objects.create(
        title="Sifatli mahsulot olish huquqi",
        content="Iste'molchi qonun bo'yicha sifatli tovar talab qilishi mumkin",
        order=1
    )
    
    # Stores list
    stores_resp = client.get('/api/v1/stores/?status=GREEN&lat=41.31&lng=69.24')
    assert stores_resp.status_code == 200
    s_data = stores_resp.json()
    assert s_data['success'] is True
    assert s_data['count'] == 1
    assert s_data['stores'][0]['name'] == 'Korzinka Test'
    
    # Rights list
    rights_resp = client.get('/api/v1/rights/')
    assert rights_resp.status_code == 200
    assert rights_resp.json()['count'] == 1
    
    # Support info
    supp_resp = client.get('/api/v1/support/')
    assert supp_resp.status_code == 200
    assert supp_resp.json()['support']['telegram_admin'] == 'sesport_admin'
