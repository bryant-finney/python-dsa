"""ORM (object-relational mapping) provides data structures for the application."""

from __future__ import annotations

import datetime as dt
import enum
import uuid
from typing import Any

import sqlalchemy
from sqlalchemy import orm

now = dt.datetime.now


def round(datetime: dt.datetime) -> dt.datetime:
    """Floor the given datetime to the nearest hour."""
    return datetime.replace(minute=0, second=0, microsecond=0)


class Color(enum.IntEnum):
    """A cat's fur color."""

    BLACK = enum.auto()
    GRAY = enum.auto()
    ORANGE = enum.auto()
    OTHER = enum.auto()


class Base(orm.DeclarativeBase):
    """Collect metadata for mapping database tables to Python data structures.

    Additionally, it defines a default primary key that will be used by all subclasses for all
    tables.
    """

    id: orm.Mapped[uuid.UUID] = orm.mapped_column(primary_key=True, default=uuid.uuid4)

    @orm.declared_attr.directive
    def __tablename__(cls) -> str:  # noqa: N805
        """The table name is based on the class name."""
        return cls.__name__.lower()

    @classmethod
    def fk(cls, table: str, **kwargs: Any) -> orm.Mapped[uuid.UUID]:
        """Create a foreign key column to the given table."""
        return orm.mapped_column(sqlalchemy.ForeignKey(f'{table}.id'), **kwargs)

    def __repr__(self) -> str:
        """Represent objects by their class name and field values.

        >>> class Example(Base):
        ...     a_field: orm.Mapped[str]

        >>> Example(a_field='a value')
        Example(a_field='a value')
        """
        pairs: list[str] = []
        for field_name in self.__table__.columns.keys():
            value = getattr(self, field_name)
            pairs.append(f'{field_name}={value!r}')

        args = ', '.join(pairs)
        return f'{self.__class__.__name__}({args})'


class Person(Base):
    """A human who might or might not own a cat."""

    given_name: orm.Mapped[str]
    surname: orm.Mapped[str]


class Cat(Base):
    """Store data about a cat."""

    name: orm.Mapped[str]

    age: orm.Mapped[int] = orm.mapped_column(default=0)  # years
    color: orm.Mapped[Color] = orm.mapped_column(default=Color.OTHER)
    lives: orm.Mapped[int] = orm.mapped_column(default=9)

    owner_id: orm.Mapped[uuid.UUID] = Base.fk('person')


class Clinic(Base):
    """A clinic where veterinarians work to care for cats and owners."""

    name: orm.Mapped[str]


class Veterinarian(Person):
    """A person who cares for cats and owners."""

    license_number: orm.Mapped[str]

    # this field is both a primary key and a foreign key
    id: orm.Mapped[uuid.UUID] = Base.fk('person', primary_key=True)
    clinic_id: orm.Mapped[uuid.UUID] = Base.fk('clinic')


class Appointment(Base):
    """A pet owner's appoint to see their vet at the clinic."""

    # default: this time tomorrow, but rounded down to the nearest hour
    start: orm.Mapped[dt.datetime] = orm.mapped_column(
        default=lambda: round(now() + dt.timedelta(days=1))
    )
    duration: orm.Mapped[dt.timedelta] = orm.mapped_column(default=dt.timedelta(minutes=30))

    cat_id: orm.Mapped[uuid.UUID] = Base.fk('cat')
    clinic_id: orm.Mapped[uuid.UUID] = Base.fk('clinic')
    owner_id: orm.Mapped[uuid.UUID] = Base.fk('person')
    veterinarian_id: orm.Mapped[uuid.UUID] = Base.fk('veterinarian')
