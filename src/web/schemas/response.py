from typing import Optional

from pydantic import BaseModel

class ResponseSchema(BaseModel):
    id: Optional[int] = None
    job_id: int
    user_id: int
    message: str
