from minimalmodbus import Instrument

from .oven import Oven

# Celsius
MINIMUM_SETPOINT = 0.0
MAXIMUM_SETPOINT = 232.0

TEMPERATURE_REGISTER = 1
SETPOINT_REGISTER = 0
NUMBER_OF_DECIMALS = 1


class Quince10GCEOven(Oven):
    """
    Represents a physical [Quincy 10 GCE lab oven](https://quincylab.com/digital-lab-ovens).

    Parameters
    ----------
    port
        The port (i.e. "COM4") to use.

    Raises
    ------
    SerialException
        The port cannot be opened.
    """

    def __init__(self, port: str):
        # this instantly opens the serial port so it could throw an error
        # `close_port_after_each_call` ensures multiple instances can exist simultaneously
        self.instrument = Instrument(port, 1)

    def read_temperature(self) -> float | None:  # implementation
        try:
            return float(self.instrument.read_register(TEMPERATURE_REGISTER, NUMBER_OF_DECIMALS))
        except OSError:
            return None

    def read_setpoint(self) -> float | None:  # implementation
        try:
            return float(self.instrument.read_register(SETPOINT_REGISTER, NUMBER_OF_DECIMALS))
        except OSError:
            return None

    def set_setpoint(self, setpoint: float) -> bool:  # implementation
        try:
            self.instrument.write_register(SETPOINT_REGISTER, setpoint, NUMBER_OF_DECIMALS)
            return True
        except OSError:
            return False

    def minimum_setpoint(self) -> float:  # implementation
        return MINIMUM_SETPOINT

    def maximum_setpoint(self) -> float:  # implementation
        return MAXIMUM_SETPOINT
