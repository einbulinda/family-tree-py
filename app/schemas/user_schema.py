from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, constr

class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: constr(min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password:str

class UserRead(BaseModel):
    id: int
    role: str
    is_approved: bool
    created_at: datetime

    class Config:
        from_attribute = True

class Token(BaseModel):
    access_token :str
    token_type:str = "bearer"

class TokenData(BaseModel):
    sub: Optional[str] = None
