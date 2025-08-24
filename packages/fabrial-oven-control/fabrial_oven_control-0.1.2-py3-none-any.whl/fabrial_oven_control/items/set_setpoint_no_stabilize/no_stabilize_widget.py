from pathlib import Path

from fabrial import ItemWidget, TextDescription
from fabrial.custom_widgets import DoubleSpinBox, Widget
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QFormLayout

from ...constants import OVEN_PORT_LABEL, SETPOINT_LABEL
from ...quince10GCE import MAXIMUM_SETPOINT, MINIMUM_SETPOINT
from ...widgets import PortComboBox

BASE_NAME = "Set Setpoint No Stabilization"
ICON = QIcon(str(Path(__file__).parent.joinpath("thermometer.png")))


class NoStabilizeWidget(ItemWidget):
    """Set the oven's setpoint without waiting for the temperature to stabilize; widget."""

    def __init__(self, port: str | None, setpoint: float):
        layout = QFormLayout()
        self.port_combo_box = PortComboBox(port)
        self.setpoint_spinbox = DoubleSpinBox(2, MINIMUM_SETPOINT, MAXIMUM_SETPOINT, setpoint)
        layout.addRow(OVEN_PORT_LABEL, self.port_combo_box)
        layout.addRow(SETPOINT_LABEL, self.setpoint_spinbox)

        ItemWidget.__init__(
            self,
            Widget(layout),
            BASE_NAME,
            ICON,
            TextDescription(
                BASE_NAME,
                "Set the oven's setpoint without waiting for it to stabilize.",
                {
                    OVEN_PORT_LABEL: "The COM port the oven is connected to.",
                    SETPOINT_LABEL: "The setpont to set the oven to.",
                },
            ),
        )

        self.setpoint_spinbox.editingFinished.connect(self.handle_setpoint_change)

    def handle_setpoint_change(self):
        """Handle the value of the setpoint spinbox changing."""
        self.setWindowTitle(f"{BASE_NAME} ({self.setpoint_spinbox.value()} degrees)")
