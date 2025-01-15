from dataclasses import dataclass, field
from decimal import Decimal

from models.response import Response
from models.user import User

@dataclass
class Job:
    id: int
    user_id: int
    title: str
    description: str
    salary_from: Decimal
    salary_to: Decimal
    is_active: bool

    user: User = field(default_factory=User)
    responses: list[Response] = field(default_factory=list)
