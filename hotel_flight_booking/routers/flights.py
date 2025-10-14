from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Flight, FlightBooking, User
from schemas import FlightCreate, FlightBookingCreate, FlightBookingOut
from auth import get_current_admin, get_current_user

router = APIRouter(prefix="/flights", tags=["Flights"])

@router.get("/")
def search_flights(
    from_city: str,
    to_city: str,
    passengers: int = 1,
    db: Session = Depends(get_db)
):
    """Простой поиск рейсов"""
    flights = db.query(Flight).filter(
        Flight.from_city == from_city,
        Flight.to_city == to_city,
        (Flight.total_seats - Flight.booked_seats) >= passengers
    ).all()
    
    return [{
        "id": f.id,
        "from": f.from_city,
        "to": f.to_city, 
        "departure": f.departure,
        "arrival": f.arrival,
        "price": f.price,
        "available": f.total_seats - f.booked_seats
    } for f in flights]

@router.post("/", dependencies=[Depends(get_current_admin)])
def create_flight(flight: FlightCreate, db: Session = Depends(get_db)):
    db_flight = Flight(**flight.dict())
    db.add(db_flight)
    db.commit()
    db.refresh(db_flight)
    return db_flight

@router.post("/book")
def book_flight(
    booking: FlightBookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Бронирование рейса"""
    for flight_id in booking.flight_ids:
        flight = db.query(Flight).filter(Flight.id == flight_id).first()
        if not flight:
            raise HTTPException(status_code=404, detail=f"Flight {flight_id} not found")
        
        if (flight.total_seats - flight.booked_seats) < booking.passengers:
            raise HTTPException(status_code=400, detail=f"Not enough seats on flight {flight_id}")
        
        flight.booked_seats += booking.passengers
        flight_booking = FlightBooking(
            user_id=current_user.id,
            flight_id=flight_id,
            passengers=booking.passengers
        )
        db.add(flight_booking)
    
    db.commit()
    return {"msg": "Flight booked successfully"}

@router.get("/my-bookings", response_model=list[FlightBookingOut])
def get_my_flight_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bookings = db.query(FlightBooking).filter(
        FlightBooking.user_id == current_user.id
    ).all()
    return bookings