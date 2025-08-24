from pathlib import Path

from fabrial import FilesDescription, ItemWidget, Substitutions
from PyQt6.QtGui import QIcon

from ...constants import (
    INTERVAL_LABEL,
    MINIMUM_MEASUREMENTS_LABEL,
    OVEN_PORT_LABEL,
    SETPOINT_LABEL,
    TEMPERATURES_FILENAME,
    TOLERANCE_LABEL,
)
from ...quince10GCE import MAXIMUM_SETPOINT, MINIMUM_SETPOINT
from ...widgets import OvenStabilizationWidget

BASE_NAME = "Set Setpoint"
DIRECTORY = Path(__file__).parent
ICON = QIcon(str(DIRECTORY.joinpath("thermometer--arrow.png")))
DESCRIPTIONS_DIRECTORY = DIRECTORY.joinpath("descriptions")


class SetSetpointWidget(ItemWidget):
    """Set the oven's setpoint and stabilize; widget."""

    def __init__(
        self,
        port: str | None,
        setpoint: float,
        measurement_interval_ms: int,
        minimum_measurements: int,
        tolerance: float,
    ):
        self.data_widget = OvenStabilizationWidget(
            SETPOINT_LABEL,
            MINIMUM_SETPOINT,
            MAXIMUM_SETPOINT,
            port,
            setpoint,
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
                        "SETPOINT": SETPOINT_LABEL,
                        "INTERVAL": INTERVAL_LABEL,
                        "MINIMUM_MEASUREMENTS": MINIMUM_MEASUREMENTS_LABEL,
                        "TOLERANCE": TOLERANCE_LABEL,
                    },
                    data_recording={"TEMPERATURE_FILE": TEMPERATURES_FILENAME},
                ),
            ),
        )

        self.data_widget.temperature_spinbox.editingFinished.connect(self.handle_setpoint_change)

    def handle_setpoint_change(self):
        """Handle the value of the setpoint spinbox changing."""
        self.setWindowTitle(f"{BASE_NAME} ({self.data_widget.temperature_spinbox.value()} degrees)")
