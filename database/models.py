from datetime import datetime

from database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, DateTime, func, Date, Time, Boolean, UniqueConstraint


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    surname: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)
    hash_password: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=True)

    procedures: Mapped[list["Procedures"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    tokens: Mapped[list["TokenUser"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    entries: Mapped[list["EntryCosmetology"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

class Procedures(Base):
    __tablename__ = "procedures"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    name_procedures: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)

    user: Mapped["User"] = relationship(back_populates="procedures")
    entries_cosmetology: Mapped[list["EntryCosmetology"]] = relationship(back_populates="procedure")


class TokenUser(Base):
    __tablename__ = "token_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    token_hash: Mapped[str] = mapped_column(String, nullable=False)

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    is_working: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    user: Mapped["User"] = relationship(back_populates="tokens")


class EntryCosmetology(Base):
    __tablename__ = "entry_cosmologies"

    # Создаем уникальность записи, чтобы два человека в случае одновременной записи, не могли бы записаться.
    __table_args__ = (
        UniqueConstraint(
            "entry_date",
            "entry_time",
            name="uq_entry_date_time",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"),nullable=False)
    procedure_id: Mapped[int] = mapped_column(ForeignKey("procedures.id", ondelete="CASCADE"),nullable=False)
    entry_date: Mapped[Date] = mapped_column(Date, nullable=False)
    entry_time: Mapped[Time] = mapped_column(Time, nullable=False)

    user: Mapped["User"] = relationship(
        back_populates="entries",
    )
    procedure: Mapped["Procedures"] = relationship(back_populates="entries_cosmetology")

