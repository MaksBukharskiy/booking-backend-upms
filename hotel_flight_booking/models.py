from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

flight_connections = Table(
    'flight_connections', Base.metadata,
    Column('flight_id', Integer, ForeignKey('flights.id')),
    Column('connection_id', Integer, ForeignKey('flights.id'))
)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True)
    password = Column(String)
    role = Column(String, default="user")
    bookings = relationship("Booking", back_populates="user")
    flight_bookings = relationship("FlightBooking", back_populates="user")

class Hotel(Base):
    __tablename__ = 'hotels'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    city = Column(String)
    stars = Column(Integer)
    rooms = relationship("Room", back_populates="hotel")

class Room(Base):
    __tablename__ = 'rooms'
    id = Column(Integer, primary_key=True)
    hotel_id = Column(Integer, ForeignKey('hotels.id'))
    room_type = Column(String)
    price = Column(Float)
    capacity = Column(Integer)
    available = Column(Boolean, default=True)
    hotel = relationship("Hotel", back_populates="rooms")
    bookings = relationship("Booking", back_populates="room")

class Booking(Base):
    __tablename__ = 'bookings'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    room_id = Column(Integer, ForeignKey('rooms.id'))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    user = relationship("User", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")


class Flight(Base):
    __tablename__ = 'flights'
    id = Column(Integer, primary_key=True)
    from_city = Column(String)
    to_city = Column(String)
    departure = Column(DateTime)
    arrival = Column(DateTime)
    total_seats = Column(Integer)
    booked_seats = Column(Integer, default=0)
    price = Column(Float)
    bookings = relationship("FlightBooking", back_populates="flight")

class FlightBooking(Base):
    __tablename__ = 'flight_bookings'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    flight_id = Column(Integer, ForeignKey('flights.id'))
    passengers = Column(Integer)
    booking_date = Column(DateTime, default=datetime.now)
    user = relationship("User", back_populates="flight_bookings")
    flight = relationship("Flight", back_populates="bookings")