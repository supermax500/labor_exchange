from dataclasses import dataclass


@dataclass
class Response:
    id: int
    job_id: int
    user_id: int
    message: str
