from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from arbitrage_os.auth.schemas import Token, UserCreate, UserOut
from arbitrage_os.auth.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user, # Ensure this is imported from security.py
    create_access_token,
    get_current_active_user,
    get_password_hash, # Ensure this is imported from security.py
)
from arbitrage_os.db.database import SessionLocal
from arbitrage_os.db.models import User as DBUser # Import the User model

router = APIRouter()

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me/", response_model=UserOut) # Use UserOut for response
async def read_users_me(current_user: Annotated[DBUser, Depends(get_current_active_user)]):
    return current_user

# Endpoint to create a new user
@router.post("/register/", response_model=UserOut) # Use UserOut for response
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(DBUser).filter(DBUser.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password) # Use user.password from UserCreate
    db_user = DBUser(username=user.username, email=user.email, full_name=user.full_name, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
