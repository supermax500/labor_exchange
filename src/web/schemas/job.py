from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, field_validator
from pydantic_core.core_schema import ValidationInfo


class JobSchema(BaseModel):
    id: int | None = None
    user_id: int
    title: str | None = None
    description: str | None = None
    salary_from: Decimal | None = None
    salary_to: Decimal | None = None
    is_active: bool | None = False


def valid_salary_range(salary_to: Decimal, validation_context: ValidationInfo) -> None:
    a = validation_context.data["salary_from"]
    b = salary_to
    if a is not None and b is not None:
        if a < 0 or b < 0:
            raise ValueError("Salary must be non-negative")
        if a > b:
            raise ValueError("Bad salary range")
    # return self


class JobCreateSchema(BaseModel):
    title: str
    description: str
    salary_from: Decimal | None = None
    salary_to: Decimal | None = None
    is_active: bool | None = False

    check_salary = field_validator("salary_to", mode="after")(valid_salary_range)


class JobUpdateSchema(BaseModel):
    id: int
    title: Optional[str] = None
    description: Optional[str] = None
    salary_from: Optional[Decimal] = None
    salary_to: Optional[Decimal] = None
    is_active: Optional[bool] = False

    check_salary = field_validator("salary_to", mode="after")(valid_salary_range)
