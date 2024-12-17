from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from storage.sqlalchemy.client import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, comment="Идентификатор вакансии")
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), comment="Идентификатор пользователя"
    )

    # добавьте ваши колонки сюда
    title: Mapped[str] = mapped_column(comment="Название вакансии")
    description: Mapped[str] = mapped_column(comment="Описание вакансии")
    salary_from: Mapped[Decimal] = mapped_column(Numeric(10, 2), comment="Зарплата от")
    salary_to: Mapped[Decimal] = mapped_column(Numeric(10, 2), comment="Зарплата до")
    is_active: Mapped[bool] = mapped_column(comment="Активна ли вакансия")
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, comment="Дата создания записи")

    user: Mapped["User"] = relationship(back_populates="jobs")  # noqa
    responses: Mapped["Response"] = relationship(back_populates="job")  # noqa
