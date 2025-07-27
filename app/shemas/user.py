from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
import re

def valider_password(cls, value):
    if not re.search(r'[a-z]', value):
            raise ValueError("Le mot de passe doit contenir au moins une lettre minuscule")
    if not re.search(r'[A-Z]', value):
        raise ValueError("Le mot de passe doit contenir au moins une lettre majuscule")
    if not re.search(r'\d', value):
        raise ValueError("Le mot de passe doit contenir au moins un chiffre")
    if not re.search(r'[#?!@$%^&*-]', value):
        raise ValueError("Le mot de passe doit contenir au moins un caractère spécial")
    return value

class RoleOut(BaseModel):
    role_name: Optional[str]

    class Config:    
        from_attributes = True

class UserOut(BaseModel):
    first_name: str
    last_name: str
    email: str
    role: Optional[RoleOut]

    class Config:    
        from_attributes = True

class UserIn(BaseModel): 
    first_name: str = Field(min_length=3, max_length=10, pattern="^[a-zA-Z\-]+$") 
    last_name: str = Field(min_length=3, max_length=10, pattern="^[a-zA-Z\-]+$") 
    email: EmailStr 
    password: str = Field(min_length=8, max_length=20) 

    @field_validator("password")
    def validator(cls, value):
        return valider_password(cls, value)
 
class UserUpdate(BaseModel): 
    first_name: Optional[str] = Field(None, min_length=3, max_length=10, pattern="^[a-zA-Z\-]+$") 
    last_name: Optional[str] = Field(None, min_length=3, max_length=10, pattern="^[a-zA-Z\-]+$") 
    email: Optional[EmailStr] = None 
    password: Optional[str] = Field(None, min_length=8,max_length=20)

    @field_validator("password")
    def validator(cls, value):
        return valider_password(cls, value)