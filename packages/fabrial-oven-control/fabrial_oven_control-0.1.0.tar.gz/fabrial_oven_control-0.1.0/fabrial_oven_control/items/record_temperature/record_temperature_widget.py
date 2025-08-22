from pathlib import Path

from fabrial import ItemWidget, TextDescription
from fabrial.custom_widgets import Widget
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QFormLayout

from ...constants import OVEN_PORT_LABEL
from ...widgets import PortComboBox

NAME = "Record Temperature"
ICON = QIcon(str(Path(__file__).parent.joinpath("tag-label-red.png")))
FILENAME = "temperature.csv"


class RecordTemperatureWidget(ItemWidget):
    """Record the oven's temperature once; widget."""

    def __init__(self, port: str | None):
        layout = QFormLayout()
        self.port_combo_box = PortComboBox(port)
        layout.addRow(OVEN_PORT_LABEL, self.port_combo_box)

        ItemWidget.__init__(
            self,
            Widget(layout),
            NAME,
            ICON,
            TextDescription(
                NAME,
                "Record the oven's temperature once.",
                {OVEN_PORT_LABEL: "The COM port the oven is connected to."},
                {FILENAME: "The recorded temperature."},
            ),
        )
