from pydantic import BaseModel
from typing import Optional

class ImageUpdate(BaseModel):
    logo_id: Optional[int] = None