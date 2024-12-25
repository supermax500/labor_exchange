from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, model_validator
from typing_extensions import Self


class JobSchema(BaseModel):
    id: Optional[int] = None
    user_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    salary_from: Optional[Decimal] = None
    salary_to: Optional[Decimal] = None
    is_active: Optional[bool] = False


class JobCreateSchema(BaseModel):
    user_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    salary_from: Optional[Decimal] = None
    salary_to: Optional[Decimal] = None
    is_active: Optional[bool] = False

    @model_validator(mode="after")
    def valid_salary_range(self) -> Self:
        a = self.salary_from
        b = self.salary_to
        if a is not None and b is not None:
            if a < 0 or b < 0:
                raise ValueError("Salary must be non-negative")
            if a > b:
                raise ValueError("Bad salary range")
        return self


class JobUpdateSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    salary_from: Optional[Decimal] = None
    salary_to: Optional[Decimal] = None
    is_active: Optional[bool] = False

    @model_validator(mode="after")
    def valid_salary_range(self) -> Self:
        a = self.salary_from
        b = self.salary_to
        if a is not None and b is not None:
            if a < 0 or b < 0:
                raise ValueError("Salary must be non-negative")
            if a > b:
                raise ValueError("Bad salary range")
        return self
