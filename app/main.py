from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware   
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine
from .dependencies import get_db
from .auth import hash_password, verify_password, create_access_token
from .notes import router as notes_router

# Create tables in database
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS Middleware (Allow All Origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Allow any origin
    allow_credentials=False,    # Safer when using "*"
    allow_methods=["*"],        # Allow all HTTP methods
    allow_headers=["*"],        # Allow all headers 
)


@app.post("/register", tags=["Users"])
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):

    # Check duplicate username
    existing_user = db.query(models.User).filter(
        models.User.username == user.username
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this username already exists"
        )

    # Check duplicate email
    existing_email = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )

    # Create new user
    new_user = models.User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}


@app.post("/login", tags=["Users"])
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(
        models.User.username == request.username
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not verify_password(request.password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token = create_access_token({"user_id": user.id})

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# Include Notes router
app.include_router(notes_router)