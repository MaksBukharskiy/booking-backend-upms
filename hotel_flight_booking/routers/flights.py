from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Flight, FlightBooking, User
from schemas import FlightSearch, FlightCreate, FlightOut, FlightBookingCreate, FlightBookingOut
from auth import get_current_admin, get_current_user
import datetime
from sqlalchemy import and_, or_

router = APIRouter(prefix="/flights", tags=["Flights"])

MAX_CONNECTION_HOURS = 24

@router.get("/", response_model=List[dict],
    summary="Search flights",
    description="Search for flights with optional connections via specified cities"
)


@router.get("/", response_model=List[dict])
def search_flights(
    from_city: str,
    to_city: str, 
    date: datetime,
    passengers: int = 1,
    db: Session = Depends(get_db)
):
    try:
        flights = db.query(Flight).filter(
            Flight.from_city == from_city,
            Flight.to_city == to_city,
            Flight.departure >= date.replace(hour=0, minute=0),
            Flight.departure < date.replace(hour=23, minute=59),
            (Flight.total_seats - Flight.booked_seats) >= passengers
        ).all()
        
        result = []
        for flight in flights:
            result.append({
                "id": flight.id,
                "from": flight.from_city,
                "to": flight.to_city,
                "departure": flight.departure,
                "arrival": flight.arrival,
                "price": flight.price,
                "available": flight.total_seats - flight.booked_seats,
                "tags": ["direct"]
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/book", response_model=FlightBookingOut,
    summary="Book flight",
    description="Book a flight or complex route with connections"
)
def book_flight(
    booking: FlightBookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Book single flight or complex route with connections
    flight_ids format:
    - [123] for direct flight
    - [123, 456] for connection route
    """
    
    flights_to_book = []
    for flight_id in booking.flight_ids:
        flight = db.query(Flight).filter(Flight.id == flight_id).first()
        if not flight:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Flight {flight_id} not found"
            )
        
        if (flight.total_seats - flight.booked_seats) < booking.passengers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough seats on flight {flight_id}"
            )
        
        flights_to_book.append(flight)

    if len(booking.flight_ids) > 1:
        for i in range(len(flights_to_book) - 1):
            current_flight = flights_to_book[i]
            next_flight = flights_to_book[i + 1]
            
            if current_flight.to_city != next_flight.from_city:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid route: {current_flight.to_city} -> {next_flight.from_city}"
                )
            
            if next_flight.departure <= current_flight.arrival:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid connection timing between flights {current_flight.id} and {next_flight.id}"
                )

    bookings = []
    for flight in flights_to_book:
        flight.booked_seats += booking.passengers
        flight_booking = FlightBooking(
            user_id=current_user.id,
            flight_id=flight.id,
            passengers=booking.passengers
        )
        db.add(flight_booking)
        bookings.append(flight_booking)

    try:
        db.commit()
        for booking in bookings:
            db.refresh(booking)
        
        return bookings[0]
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Booking failed"
        )

@router.get("/my-bookings", response_model=List[FlightBookingOut],
    summary="Get user's flight bookings",
    description="Get all flight bookings for current user"
)
def get_my_flight_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bookings = db.query(FlightBooking).filter(
        FlightBooking.user_id == current_user.id
    ).all()
    return bookings

@router.post("/", response_model=FlightOut, 
    dependencies=[Depends(get_current_admin)],
    summary="Create flight (admin only)",
    description="Create a new flight - admin access required"
)
def create_flight(flight: FlightCreate, db: Session = Depends(get_db)):
    db_flight = Flight(**flight.dict())
    db.add(db_flight)
    db.commit()
    db.refresh(db_flight)
    return db_flight

@router.put("/{flight_id}", response_model=FlightOut, 
    dependencies=[Depends(get_current_admin)],
    summary="Update flight (admin only)",
    description="Update flight information - admin access required"
)
def update_flight(flight_id: int, flight_update: FlightCreate, db: Session = Depends(get_db)):
    db_flight = db.query(Flight).filter(Flight.id == flight_id).first()
    if not db_flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    for key, value in flight_update.dict().items():
        setattr(db_flight, key, value)
    
    db.commit()
    db.refresh(db_flight)
    return db_flight

@router.delete("/{flight_id}", 
    dependencies=[Depends(get_current_admin)],
    summary="Delete flight (admin only)",
    description="Delete a flight - admin access required"
)
def delete_flight(flight_id: int, db: Session = Depends(get_db)):
    db_flight = db.query(Flight).filter(Flight.id == flight_id).first()
    if not db_flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    active_bookings = db.query(FlightBooking).filter(
        FlightBooking.flight_id == flight_id
    ).count()
    
    if active_bookings > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete flight with active bookings"
        )
    
    db.delete(db_flight)
    db.commit()
    return {"msg": "Flight deleted"}