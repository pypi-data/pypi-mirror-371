from abc import abstractmethod
from typing import Protocol


class Oven(Protocol):
    """
    Protocol for objects that represent ovens. This protocol does not care if the oven uses Celsius
    or Fahrenheit, just be consistent.
    """

    @abstractmethod
    def read_temperature(self) -> float | None:
        """
        Read the oven's temperature. This must free the oven (i.e. close the port) after reading the
        temperature.

        Returns
        -------
        The temperature if it could be read, `None` otherwise.
        """
        ...

    @abstractmethod
    def read_setpoint(self) -> float | None:
        """
        Read the oven's setpoint. This must free the oven (i.e. close the port) after reading the
        setpoint.

        Returns
        -------
        The setpoint if it could be read, `None` otherwise.
        """
        ...

    @abstractmethod
    def set_setpoint(self, setpoint: float) -> bool:
        """
        Set the oven's setpoint. This must free the oven (i.e. close the port) after setting the
        setpoint.

        Returns
        -------
        Whether the operation succeeded.
        """
        ...

    @abstractmethod
    def minimum_setpoint(self) -> float:
        """Get the minimum setpoint. This is expected to be a constant."""
        ...

    @abstractmethod
    def maximum_setpoint(self) -> float:
        """Get the maximum setpoint. This is expected to be a constant."""
        ...
