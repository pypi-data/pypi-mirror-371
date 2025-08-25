from fabrial.custom_widgets import DoubleSpinBox, PortComboBox, SpinBox, Widget
from PyQt6.QtWidgets import QFormLayout

from .constants import INTERVAL_LABEL, MINIMUM_MEASUREMENTS_LABEL, OVEN_PORT_LABEL, TOLERANCE_LABEL


class OvenStabilizationWidget(Widget):
    """
    Contains entries for running a temperature stabilization step.

    Parameters
    ----------
    temperature_label
        The label to use for the temperature spinbox.
    minimum_temperature
        The minimum value for the temperature spinbox.
    maximum_temperature
        The maximum value for the temperature spinbox.
    port
        The initial port to select.
    temperature
        The initial value of the temperature spinbox.
    measurement_interval_ms
        The initial value of the measurement interval spinbox.
    minimum_measurements
        The initial value of the minimum measurements spinbox.
    tolerance
        The initial value of the tolerance spinbox.
    """

    def __init__(
        self,
        temperature_label: str,
        minimum_temperature: float,
        maximum_temperature: float,
        port: str | None,
        temperature: float,
        measurement_interval_ms: int,
        minimum_measurements: int,
        tolerance: float,
    ):
        layout = QFormLayout()
        Widget.__init__(self, layout)

        self.port_combo_box = PortComboBox(port)
        self.temperature_spinbox = DoubleSpinBox(
            2, minimum_temperature, maximum_temperature, temperature
        )
        self.interval_spinbox = SpinBox(10, initial_value=measurement_interval_ms)
        self.minimum_measurements_spinbox = SpinBox(2, initial_value=minimum_measurements)
        self.tolerance_spinbox = DoubleSpinBox(2, initial_value=tolerance)

        for label, widget in (
            (OVEN_PORT_LABEL, self.port_combo_box),
            (temperature_label, self.temperature_spinbox),
            (INTERVAL_LABEL, self.interval_spinbox),
            (MINIMUM_MEASUREMENTS_LABEL, self.minimum_measurements_spinbox),
            (TOLERANCE_LABEL, self.tolerance_spinbox),
        ):
            layout.addRow(label, widget)
