from pydantic import BaseModel

class TokenOut(BaseModel):
    access_token: str
    token_type: str

    class Config:    
        from_attributes = True

class TokenData(BaseModel):
    email : str | None = None