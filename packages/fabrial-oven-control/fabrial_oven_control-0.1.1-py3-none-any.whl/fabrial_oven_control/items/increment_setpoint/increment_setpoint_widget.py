from pathlib import Path

from fabrial import FilesDescription, ItemWidget, Substitutions
from PyQt6.QtGui import QIcon

from ...constants import (
    INCREMENT_LABEL,
    INTERVAL_LABEL,
    MINIMUM_MEASUREMENTS_LABEL,
    OVEN_PORT_LABEL,
    TEMPERATURES_FILENAME,
    TOLERANCE_LABEL,
)
from ...quince10GCE import MAXIMUM_SETPOINT
from ...widgets import OvenStabilizationWidget

BASE_NAME = "Increment Setpoint"
DIRECTORY = Path(__file__).parent
ICON = QIcon(str(DIRECTORY.joinpath("thermometer--plus.png")))
DESCRIPTIONS_DIRECTORY = DIRECTORY.joinpath("descriptions")


class IncrementSetpointWidget(ItemWidget):
    """Increment the oven's setpoint and stabilize; widget."""

    def __init__(
        self,
        port: str | None,
        increment: float,
        measurement_interval_ms: int,
        minimum_measurements: int,
        tolerance: float,
    ):
        self.data_widget = OvenStabilizationWidget(
            INCREMENT_LABEL,
            -MAXIMUM_SETPOINT,
            MAXIMUM_SETPOINT,
            port,
            increment,
            measurement_interval_ms,
            minimum_measurements,
            tolerance,
        )

        ItemWidget.__init__(
            self,
            self.data_widget,
            BASE_NAME,
            ICON,
            FilesDescription(
                DESCRIPTIONS_DIRECTORY,
                BASE_NAME,
                Substitutions(
                    parameters={
                        "OVEN_PORT": OVEN_PORT_LABEL,
                        "INCREMENT": INCREMENT_LABEL,
                        "INTERVAL": INTERVAL_LABEL,
                        "MINIMUM_MEASUREMENTS": MINIMUM_MEASUREMENTS_LABEL,
                        "TOLERANCE": TOLERANCE_LABEL,
                    },
                    data_recording={"TEMPERATURE_FILE": TEMPERATURES_FILENAME},
                ),
            ),
        )

        self.data_widget.temperature_spinbox.editingFinished.connect(self.handle_increment_change)

    def handle_increment_change(self):
        """Handle the value of the increment spinbox changing."""
        self.setWindowTitle(f"{BASE_NAME} ({self.data_widget.temperature_spinbox.value()} degrees)")
