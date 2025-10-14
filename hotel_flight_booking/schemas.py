from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional, List
from enum import Enum

class RoomType(str, Enum):
    STANDARD = "standard"
    LARGE = "large"
    PREMIUM = "premium"

class UserCreate(BaseModel):
    name: str
    email: str 
    password: str

    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v

class UserUpdate(BaseModel):
    name: Optional[str] = None

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class HotelFilter(BaseModel):
    city: Optional[str] = None
    stars: Optional[int] = None
    sort_by_stars: bool = False

class HotelCreate(BaseModel):
    name: str
    city: str
    stars: int

    @validator('stars')
    def validate_stars(cls, v):
        if not 1 <= v <= 5:
            raise ValueError('Stars must be between 1 and 5')
        return v

class HotelOut(HotelCreate):
    id: int
    
    class Config:
        from_attributes = True

class RoomFilter(BaseModel):
    hotel_id: Optional[int] = None
    room_type: Optional[RoomType] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    capacity: Optional[int] = None
    sort_by_price: bool = False

class RoomCreate(BaseModel):
    hotel_id: int
    room_type: RoomType
    price: float
    capacity: int
    available: bool = True

    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v

    @validator('capacity')
    def validate_capacity(cls, v):
        if v <= 0:
            raise ValueError('Capacity must be positive')
        return v

class RoomOut(RoomCreate):
    id: int
    
    class Config:
        from_attributes = True

class BookingCreate(BaseModel):
    room_id: int
    start_date: datetime
    end_date: datetime

    @validator('end_date')
    def validate_dates(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v

class BookingByDays(BaseModel):
    room_id: int
    start_date: datetime
    num_days: int

    @validator('num_days')
    def validate_days(cls, v):
        if v <= 0:
            raise ValueError('Number of days must be positive')
        return v

class FlightSearch(BaseModel):
    from_city: str
    to_city: str
    date: datetime
    passengers: int
    via_cities: Optional[List[str]] = None

    @validator('passengers')
    def validate_passengers(cls, v):
        if v <= 0:
            raise ValueError('Passengers count must be positive')
        return v

class FlightCreate(BaseModel):
    from_city: str
    to_city: str
    departure: datetime
    arrival: datetime
    total_seats: int
    price: float

    @validator('arrival')
    def validate_arrival(cls, v, values):
        if 'departure' in values and v <= values['departure']:
            raise ValueError('Arrival must be after departure')
        return v

class FlightOut(BaseModel):
    id: int
    from_city: str
    to_city: str
    departure: datetime
    arrival: datetime
    total_seats: int
    booked_seats: int
    price: float
    available: int
    tags: List[str] = []
    
    class Config:
        from_attributes = True

class FlightBookingCreate(BaseModel):
    flight_ids: List[int]
    passengers: int

    @validator('passengers')
    def validate_passengers(cls, v):
        if v <= 0:
            raise ValueError('Passengers count must be positive')
        return v

class BookingDetails(BaseModel):
    id: int
    user_id: int
    room_id: int
    start_date: datetime
    end_date: datetime
    
    class Config:
        from_attributes = True

class FlightBookingOut(BaseModel):
    id: int
    user_id: int
    flight_id: int
    passengers: int
    booking_date: datetime
    
    class Config:
        from_attributes = True




class FlightSearchResponse(BaseModel):
    id: str  
    from_city: str
    to_city: str
    departure: datetime
    arrival: datetime
    price: float
    available: int
    tags: List[str] = []
    connections: List[int] = []
    duration: Optional[timedelta] = None
    
    class Config:
        from_attributes = True

class FutureDateTime:
    @classmethod
    def validate_future(cls, v):
        if v < datetime.now():
            raise ValueError('Date must be in the future')
        return v