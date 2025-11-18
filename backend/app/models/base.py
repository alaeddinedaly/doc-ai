"""SQLAlchemy base model."""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """Declarative base class with naming helpers."""

    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa: D401
        """Generate snake_case table names."""

        name = cls.__name__
        snake = []
        for char in name:
            if char.isupper() and snake:
                snake.append("_")
            snake.append(char.lower())
        return "".join(snake)

