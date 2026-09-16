"""Modelos ORM (tablas de la base de datos)."""
from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Lead(Base):
    __tablename__ = "lead"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lead_id_origen: Mapped[str | None] = mapped_column(String)
    empresa_id: Mapped[str | None] = mapped_column(String)
    punto_venta_id: Mapped[str | None] = mapped_column(String)
    canal: Mapped[str | None] = mapped_column(String)
    fecha_registro: Mapped[datetime | None] = mapped_column(DateTime)
    nombre: Mapped[str | None] = mapped_column(String)
    telefono: Mapped[str | None] = mapped_column(String)
    email: Mapped[str | None] = mapped_column(String)
    ciudad: Mapped[str | None] = mapped_column(String)
    modelo_interes: Mapped[str | None] = mapped_column(String)
    estado: Mapped[str | None] = mapped_column(String)
    fecha_primer_contacto: Mapped[datetime | None] = mapped_column(DateTime)
    campania: Mapped[str | None] = mapped_column(String)
