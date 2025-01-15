from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.job import Job
from models.response import Response


@dataclass
class User:
    id: int
    name: str
    email: str
    hashed_password: str
    is_company: bool

    jobs: list["Job"] = field(default_factory=list)
    responses: list[Response] = field(default_factory=list)
