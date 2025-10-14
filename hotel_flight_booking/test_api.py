import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_full_api():
    print("🚀 Начинаем тестирование API...")
    
    print("1. Регистрируем админа...")
    admin_data = {
        "name": "Admin User",
        "email": "admin@example.com",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/users/register", json=admin_data)
    print(f"   Регистрация админа: {response.status_code}")
    admin_info = response.json()
    print(f"   Админ создан: {admin_info}")
    
    print("2. Логинимся как админ...")
    login_data = {
        "username": "admin@example.com",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/users/login", data=login_data)
    print(f"   Логин админа: {response.status_code}")
    admin_token = response.json()["access_token"]
    print(f"   Токен админа получен")
    
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    
    print("3. Создаем отель...")
    hotel_data = {
        "name": "Grand Hotel",
        "city": "Moscow",
        "stars": 5
    }
    response = requests.post(f"{BASE_URL}/hotels/", json=hotel_data, headers=headers_admin)
    print(f"   Создание отеля: {response.status_code}")
    hotel_info = response.json()
    print(f"   Отель создан: {hotel_info}")
    
    print("4. Создаем номер...")
    room_data = {
        "hotel_id": 1,
        "room_type": "premium",
        "price": 200.0,
        "capacity": 2
    }
    response = requests.post(f"{BASE_URL}/hotels/rooms", json=room_data, headers=headers_admin)
    print(f"   Создание номера: {response.status_code}")
    room_info = response.json()
    print(f"   Номер создан: {room_info}")
    
    print("5. Создаем рейсы...")
    flight1_data = {
        "from_city": "Moscow",
        "to_city": "Paris",
        "departure": (datetime.now() + timedelta(days=1)).isoformat(),
        "arrival": (datetime.now() + timedelta(days=1, hours=4)).isoformat(),
        "total_seats": 100,
        "price": 300.0
    }
    response = requests.post(f"{BASE_URL}/flights/", json=flight1_data, headers=headers_admin)
    print(f"   Рейс 1 создан: {response.status_code}")
    
    flight2_data = {
        "from_city": "Paris",
        "to_city": "London",
        "departure": (datetime.now() + timedelta(days=1, hours=5)).isoformat(),
        "arrival": (datetime.now() + timedelta(days=1, hours=6)).isoformat(),
        "total_seats": 80,
        "price": 150.0
    }
    response = requests.post(f"{BASE_URL}/flights/", json=flight2_data, headers=headers_admin)
    print(f"   Рейс 2 создан: {response.status_code}")
    
    print("6. Регистрируем пользователя...")
    user_data = {
        "name": "Test User",
        "email": "user@test.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/users/register", json=user_data)
    print(f"   Регистрация пользователя: {response.status_code}")
    user_info = response.json()
    print(f"   Пользователь создан: {user_info}")
    
    print("7. Логинимся как пользователь...")
    user_login_data = {
        "username": "user@test.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/users/login", data=user_login_data)
    print(f"   Логин пользователя: {response.status_code}")
    user_token = response.json()["access_token"]
    print(f"   Токен пользователя получен")
    
    headers_user = {"Authorization": f"Bearer {user_token}"}
    
    print("8. Бронируем номер...")
    booking_data = {
        "room_id": 1,
        "start_date": (datetime.now() + timedelta(days=2)).isoformat(),
        "end_date": (datetime.now() + timedelta(days=5)).isoformat()
    }
    response = requests.post(f"{BASE_URL}/bookings/", json=booking_data, headers=headers_user)
    print(f"   Бронирование номера: {response.status_code}")
    if response.status_code == 200:
        booking_info = response.json()
        print(f"   Номер забронирован: {booking_info}")
    
    print("9. Ищем рейсы с пересадками...")
    search_params = {
        "from_city": "Moscow",
        "to_city": "London",
        "date": (datetime.now() + timedelta(days=1)).isoformat(),
        "passengers": 2,
        "via_cities": ["Paris"]
    }
    response = requests.get(f"{BASE_URL}/flights/", params=search_params, headers=headers_user)
    print(f"   Поиск рейсов: {response.status_code}")
    flights = response.json()
    print(f"   Найдено рейсов: {len(flights)}")
    
    if len(flights) > 0:
        print("10. Бронируем перелет...")
        flight_booking_data = {
            "flight_ids": [1, 2],
            "passengers": 2
        }
        response = requests.post(f"{BASE_URL}/flights/book", json=flight_booking_data, headers=headers_user)
        print(f"   Бронирование перелета: {response.status_code}")
        if response.status_code == 200:
            flight_booking_info = response.json()
            print(f"   Перелет забронирован: {flight_booking_info}")
    
    print("✅ Тестирование завершено!")
    
    print("\n📊 ИТОГИ:")
    print(f"   - Админ: {admin_info['email']} (id: {admin_info['id']})")
    print(f"   - Пользователь: {user_info['email']} (id: {user_info['id']})")
    print(f"   - Отель: Grand Hotel (id: 1)")
    print(f"   - Номер: premium (id: 1)")
    print(f"   - Рейсы: 2 создано")
    print(f"   - Бронирования: номер и перелет")


def test_flights_fixed():
    """Тестируем исправленные рейсы"""
    print("\n🔧 Тестируем исправленные рейсы...")
    
    login_data = {"username": "admin@example.com", "password": "admin123"}
    response = requests.post(f"{BASE_URL}/users/login", data=login_data)
    admin_token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    flight_data = {
        "from_city": "Moscow",
        "to_city": "Berlin", 
        "departure": (datetime.now() + timedelta(hours=2)).isoformat(),
        "arrival": (datetime.now() + timedelta(hours=4)).isoformat(),
        "total_seats": 50,
        "price": 200.0
    }
    
    response = requests.post(f"{BASE_URL}/flights/", json=flight_data, headers=headers)
    print(f"Создание рейса: {response.status_code}")
    if response.status_code == 200:
        print("✅ Рейс создан успешно!")
        flight_info = response.json()
        print(f"   Рейс: {flight_info}")
        
        search_params = {
            "from_city": "Moscow",
            "to_city": "Berlin", 
            "date": (datetime.now() + timedelta(hours=1)).isoformat(),
            "passengers": 1
        }
        response = requests.get(f"{BASE_URL}/flights/", params=search_params)
        print(f"Поиск рейсов: {response.status_code}")
        flights = response.json()
        print(f"Найдено рейсов: {len(flights)}")
        
    else:
        print(f"❌ Ошибка: {response.text}")

if __name__ == "__main__":
    test_full_api()
    test_flights_fixed() 