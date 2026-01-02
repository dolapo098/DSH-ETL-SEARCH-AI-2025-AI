from typing import Any, Generic, List, Optional, TypeVar, Protocol

T = TypeVar("T")


class IBaseRepository(Protocol, Generic[T]):
    """
    Interface for the base repository providing standard data access operations.
    """

    async def get_by_id(self, id: Any) -> Optional[T]:
        """
        Retrieves an entity by its identifier.

        Args:
            id (Any): The identifier of the entity.

        Returns:
            Optional[T]: The entity if found, otherwise None.
        """
        ...

    async def update(self, entity: T) -> T:
        """
        Updates an existing entity.

        Args:
            entity (T): The entity to update.

        Returns:
            T: The updated entity.
        """
        ...

    async def get_single(self, **filters) -> Optional[T]:
        """
        Retrieves a single entity based on the provided filters.

        Args:
            **filters: Arbitrary keyword arguments representing filter criteria.

        Returns:
            Optional[T]: The matching entity if found, otherwise None.
        """
        ...

    async def get_many(self, *filter_expressions) -> List[T]:
        """
        Retrieves multiple entities based on filter expressions.

        Args:
            *filter_expressions: SQLAlchemy filter expressions.

        Returns:
            List[T]: A list of matching entities.
        """
        ...

