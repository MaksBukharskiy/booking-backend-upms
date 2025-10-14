# routers/hotels.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Hotel, Room
from schemas import HotelFilter, RoomFilter, HotelCreate, RoomCreate, HotelOut, RoomOut  # ← Добавлены импорты!
from auth import get_current_admin

from schemas import HotelOut, RoomOut

router = APIRouter(prefix="/hotels", tags=["Hotels"])

@router.get("/", response_model=list[dict])
def get_hotels(filter: HotelFilter = Depends(), db: Session = Depends(get_db)):
    query = db.query(Hotel)
    if filter.city:
        query = query.filter(Hotel.city == filter.city)
    if filter.stars:
        query = query.filter(Hotel.stars == filter.stars)
    hotels = query.all()
    if filter.sort_by_stars:
        hotels = sorted(hotels, key=lambda h: h.stars, reverse=True)
    return [{"id": h.id, "name": h.name, "city": h.city, "stars": h.stars} for h in hotels]

@router.post("/", response_model=HotelOut, dependencies=[Depends(get_current_admin)])
def create_hotel(hotel: HotelCreate, db: Session = Depends(get_db)):
    db_hotel = Hotel(**hotel.dict())
    db.add(db_hotel)
    db.commit()
    db.refresh(db_hotel)
    return db_hotel

@router.put("/{hotel_id}", response_model=HotelOut, dependencies=[Depends(get_current_admin)])
def update_hotel(hotel_id: int, hotel_update: HotelCreate, db: Session = Depends(get_db)):
    db_hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not db_hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    for key, value in hotel_update.dict().items():
        setattr(db_hotel, key, value)
    db.commit()
    db.refresh(db_hotel)
    return db_hotel

@router.delete("/{hotel_id}", dependencies=[Depends(get_current_admin)])
def delete_hotel(hotel_id: int, db: Session = Depends(get_db)):
    db_hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not db_hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    db.delete(db_hotel)
    db.commit()
    return {"msg": "Hotel deleted"}

@router.get("/rooms", response_model=list[dict])
def get_rooms(filter: RoomFilter = Depends(), db: Session = Depends(get_db)):
    query = db.query(Room).join(Hotel).filter(Room.available == True)
    if filter.hotel_id:
        query = query.filter(Room.hotel_id == filter.hotel_id)
    if filter.room_type:
        query = query.filter(Room.room_type == filter.room_type)
    if filter.min_price:
        query = query.filter(Room.price >= filter.min_price)
    if filter.max_price:
        query = query.filter(Room.price <= filter.max_price)
    if filter.capacity:
        query = query.filter(Room.capacity >= filter.capacity)
    rooms = query.all()
    if filter.sort_by_price:
        rooms = sorted(rooms, key=lambda r: r.price)
    return [{
        "id": r.id,
        "hotel": r.hotel.name,
        "type": r.room_type,
        "price": r.price,
        "capacity": r.capacity
    } for r in rooms]

@router.post("/rooms", response_model=RoomOut, dependencies=[Depends(get_current_admin)])
def create_room(room: RoomCreate, db: Session = Depends(get_db)):
    db_room = Room(**room.dict())
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

@router.put("/rooms/{room_id}", response_model=RoomOut, dependencies=[Depends(get_current_admin)])
def update_room(room_id: int, room_update: RoomCreate, db: Session = Depends(get_db)):
    db_room = db.query(Room).filter(Room.id == room_id).first()
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found")
    for key, value in room_update.dict().items():
        setattr(db_room, key, value)
    db.commit()
    db.refresh(db_room)
    return db_room

@router.delete("/rooms/{room_id}", dependencies=[Depends(get_current_admin)])
def delete_room(room_id: int, db: Session = Depends(get_db)):
    db_room = db.query(Room).filter(Room.id == room_id).first()
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found")
    db.delete(db_room)
    db.commit()
    return {"msg": "Room deleted"}