from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

class JobSchema(BaseModel):
    id: Optional[int] = None
    user_id: int
    title: str
    description: str
    salary_from: Decimal
    salary_to: Decimal
    is_active: Optional[bool] = False
