from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user, get_current_admin
from models import Booking, Room, User
from schemas import BookingCreate, BookingByDays, BookingDetails
import datetime

router = APIRouter(prefix="/bookings", tags=["Bookings"])

@router.post("/", response_model=BookingDetails,
    summary="Book a room",
    description="Book a room for specific dates"
)
def book_room(
    booking: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if booking.start_date >= booking.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date"
        )
    
    if booking.start_date < datetime.datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot book in the past"
        )

    room = db.query(Room).filter(Room.id == booking.room_id, Room.available == True).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not available")

    conflicting_booking = db.query(Booking).filter(
        Booking.room_id == booking.room_id,
        Booking.start_date < booking.end_date,
        Booking.end_date > booking.start_date
    ).first()
    
    if conflicting_booking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room is already booked for these dates"
        )

    new_booking = Booking(
        user_id=current_user.id,
        room_id=booking.room_id,
        start_date=booking.start_date,
        end_date=booking.end_date
    )
    
    db.add(new_booking)
    try:
        db.commit()
        db.refresh(new_booking)
        return new_booking
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Booking failed"
        )

@router.post("/by-days", response_model=BookingDetails,
    summary="Book room by days count",
    description="Book a room for specific number of days"
)
def book_room_by_days(
    booking: BookingByDays,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if booking.start_date < datetime.datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot book in the past"
        )

    end_date = booking.start_date + datetime.timedelta(days=booking.num_days)
    booking_create = BookingCreate(
        room_id=booking.room_id,
        start_date=booking.start_date,
        end_date=end_date
    )
    return book_room(booking_create, current_user, db)

@router.get("/my-bookings", response_model=list[BookingDetails],
    summary="Get user's bookings",
    description="Get all bookings for current user"
)
def get_my_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bookings = db.query(Booking).filter(Booking.user_id == current_user.id).all()
    return bookings

@router.delete("/{booking_id}",
    summary="Cancel booking",
    description="Cancel a booking (users can cancel only their own, admins can cancel any)"
)
def cancel_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if current_user.role != "admin" and booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No permission to cancel this booking")

    room = db.query(Room).filter(Room.id == booking.room_id).first()
    if room:
        room.available = True
    
    db.delete(booking)
    db.commit()
    return {"msg": "Booking cancelled"}