from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth import create_access_token, get_password_hash, verify_password, get_current_admin, get_current_user, oauth2_scheme
from database import get_db
from models import User
from schemas import UserCreate, UserUpdate, UserOut, Token
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    
    db_user = User(
        name=user.name, 
        email=user.email, 
        password=hashed_password
    )
    if user.email == "admin@example.com":
        db_user.role = "admin"

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

@router.put("/me", response_model=UserOut)
def update_user_name(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user_update.name:
        current_user.name = user_update.name
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/me", response_model=UserOut)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/__test_auth_schema__", include_in_schema=False)
def __test_auth_schema__(token: str = Depends(oauth2_scheme)):
    return {"msg": "This route exists only to trigger security schema in Swagger"}