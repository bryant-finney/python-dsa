"""Define database connections and queries."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any, Protocol, Sequence, TypeVar, overload

import sqlalchemy
from sqlalchemy import orm, select, util

import models

if TYPE_CHECKING:
    from sqlalchemy.engine.interfaces import (
        _CoreAnyExecuteParams,  # pyright: ignore[reportPrivateUsage]
    )
    from sqlalchemy.engine.result import ScalarResult
    from sqlalchemy.orm._typing import OrmExecuteOptionsParameter
    from sqlalchemy.orm.session import _BindArguments  # pyright: ignore[reportPrivateUsage]
    from sqlalchemy.sql.selectable import TypedReturnsRows

    T = TypeVar('T')


class SessionProtocol(Protocol):
    """Define a protocol for database sessions that can execute queries.

    To learn more about protocols: https://dev.to/shameerchagani/what-is-a-protocol-in-python-3fl1
    """

    @overload
    def scalars(
        self,
        statement: TypedReturnsRows[tuple[T]],
        params: _CoreAnyExecuteParams | None = None,
        *,
        execution_options: OrmExecuteOptionsParameter = util.EMPTY_DICT,
        bind_arguments: _BindArguments | None = None,
        **kw: Any,
    ) -> ScalarResult[T]: ...

    @overload
    def scalars(
        self,
        statement: sqlalchemy.Executable,
        params: _CoreAnyExecuteParams | None = None,
        *,
        execution_options: OrmExecuteOptionsParameter = util.EMPTY_DICT,
        bind_arguments: _BindArguments | None = None,
        **kw: Any,
    ) -> sqlalchemy.ScalarResult[Any]: ...


class QueryMixin(SessionProtocol):
    """Define methods to query the database; used as a mixin instead of inheritance.

    The methods in this class use SQLAlchemy's ORM to send SQL queries to the database.
    """

    def get_appointments(self, veterinarian: models.Veterinarian) -> Sequence[models.Appointment]:
        """Retrieve all appointments for the given veterinarian."""

        query = select(models.Appointment).where(
            models.Appointment.veterinarian_id == veterinarian.id
        )
        return self.scalars(query).all()

    def get_cat(self, appointment: models.Appointment) -> models.Cat:
        """Retrieve the cat who was seen at the given appointment."""

        query = select(models.Cat).where(models.Cat.id == appointment.cat_id)
        return self.scalars(query).one()

    def get_clinic(self, name: str) -> models.Clinic:
        """Retrieve the clinic with the given name."""

        query = select(models.Clinic).where(models.Clinic.name == name)
        return self.scalars(query).one()

    def list_cats_seen_at(self, clinic_name: str) -> list[models.Cat]:
        """Retrieve all cats seen at the given clinic."""

        clinic = self.get_clinic(clinic_name)
        veterinarians = self.list_veterinarians(clinic)

        all_cats: list[models.Cat] = []
        for veterinarian in veterinarians:
            appointments = self.get_appointments(veterinarian)
            for appointment in appointments:
                cat = self.get_cat(appointment)
                if cat not in all_cats:
                    all_cats.append(cat)

        return all_cats

    def list_clinic_names(self) -> Sequence[str]:
        """Retrieve the names of all clinics in the database."""

        query = select(models.Clinic.name)
        return self.scalars(query).all()

    def list_veterinarians(
        self: SessionProtocol, clinic: models.Clinic
    ) -> Sequence[models.Veterinarian]:
        """Return all veterinarians who work at the given clinic."""

        query = select(models.Veterinarian).where(models.Veterinarian.clinic_id == clinic.id)
        return self.scalars(query).all()


class Session(orm.Session, QueryMixin):
    """Connect to the database for executing queries."""

    @classmethod
    def connect(cls, name: str, **kwargs: Any) -> Session:
        engine = sqlalchemy.create_engine(f'sqlite:///{name}', **kwargs)
        return cls(bind=engine)

    def scalars(
        self,
        statement: sqlalchemy.Executable,
        params: _CoreAnyExecuteParams | None = None,
        *,
        execution_options: OrmExecuteOptionsParameter = util.EMPTY_DICT,
        bind_arguments: _BindArguments | None = None,
        **kw: Any,
    ) -> sqlalchemy.ScalarResult[Any]:
        # add a short delay to simulate a remote database connection
        time.sleep(0.01)
        return super().scalars(
            statement,
            params,
            execution_options=execution_options,
            bind_arguments=bind_arguments,
            **kw,
        )
