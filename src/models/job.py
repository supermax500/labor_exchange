from dataclasses import dataclass, field
from decimal import Decimal

from .response import Response


@dataclass
class Job:
    id: int
    user_id: int
    title: str
    description: str
    salary_from: Decimal
    salary_to: Decimal
    is_active: bool

    responses: list[Response] = field(default_factory=list)
