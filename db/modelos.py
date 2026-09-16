"""Modelos ORM (tablas de la base de datos)."""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
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


class Asesor(Base):
    __tablename__ = "asesor"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asesor_id_origen: Mapped[str | None] = mapped_column(String)
    nombre: Mapped[str | None] = mapped_column(String)
    punto_venta_id: Mapped[str | None] = mapped_column(String)
    empresa_id: Mapped[str | None] = mapped_column(String)
    capacidad_diaria: Mapped[int | None] = mapped_column(Integer)
    activo: Mapped[bool | None] = mapped_column(Boolean)
    fecha_ingreso: Mapped[datetime | None] = mapped_column(DateTime)


class CatalogoMoto(Base):
    __tablename__ = "catalogo_moto"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sku: Mapped[str | None] = mapped_column(String)
    marca: Mapped[str | None] = mapped_column(String)
    linea: Mapped[str | None] = mapped_column(String)
    cilindraje: Mapped[int | None] = mapped_column(Integer)
    segmento: Mapped[str | None] = mapped_column(String)
    precio_lista: Mapped[int | None] = mapped_column(Integer)
    unidades_disponibles: Mapped[int | None] = mapped_column(Integer)


class Disponibilidad(Base):
    __tablename__ = "disponibilidad"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sku: Mapped[str | None] = mapped_column(String)
    punto_venta_id: Mapped[str | None] = mapped_column(String)
