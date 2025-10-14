# main.py
from fastapi import FastAPI
from database import engine, Base
from routers import users, hotels, bookings, flights

app = FastAPI(debug=True)

Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(hotels.router)
app.include_router(bookings.router)
app.include_router(flights.router)

@app.get("/")
def root():
    return {"message": "Welcome to Hotel & Flight Booking API!"}