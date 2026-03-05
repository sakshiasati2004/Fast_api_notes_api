from pydantic import BaseModel, EmailStr, Field, validator
import re


class UserCreate(BaseModel):
    username: str = Field(..., min_length=1)
    email: EmailStr
    password: str

    @validator("username")
    def username_no_numbers(cls, value):
        if any(char.isdigit() for char in value):
            raise ValueError("Name cannot contain numeric values")
        return value

    @validator("password")
    def strong_password(cls, value):
        if len(value) < 6:
            raise ValueError("Password must be at least 6 characters long")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[0-9]", value):
            raise ValueError("Password must contain at least one number")
        return value


class LoginRequest(BaseModel):
    username: str
    password: str


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)


class NoteUpdate(BaseModel):
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)