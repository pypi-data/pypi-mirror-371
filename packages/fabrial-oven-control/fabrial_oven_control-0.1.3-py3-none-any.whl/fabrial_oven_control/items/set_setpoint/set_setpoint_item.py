import typing
from typing import Mapping, Self

from fabrial import Json, SequenceStep, WidgetDataItem

from ...constants import MEASUREMENT_INTERVAL, MINIMUM_MEASUREMENTS, OVEN_PORT, SETPOINT, TOLERANCE
from .set_setpoint_step import SetSetpointStep
from .set_setpoint_widget import SetSetpointWidget


class SetSetpointItem(WidgetDataItem):
    """Set the oven's setpoint and stabilize; item."""

    def __init__(
        self,
        port: str | None,
        setpoint: float,
        measurement_interval_ms: int,
        minimum_measurements: int,
        tolerance: float,
    ):
        self.data_widget = SetSetpointWidget(
            port, setpoint, measurement_interval_ms, minimum_measurements, tolerance
        )

    @classmethod
    def deserialize(cls, serialized_obj: Mapping[str, Json]) -> Self:  # implementation
        item = cls(
            typing.cast(str, serialized_obj[OVEN_PORT]),
            typing.cast(float, serialized_obj[SETPOINT]),
            typing.cast(int, serialized_obj[MEASUREMENT_INTERVAL]),
            typing.cast(int, serialized_obj[MINIMUM_MEASUREMENTS]),
            typing.cast(float, serialized_obj[TOLERANCE]),
        )
        item.data_widget.handle_setpoint_change()
        return item

    def serialize(self) -> dict[str, Json]:  # implementation
        widget = self.data_widget.data_widget
        return {
            OVEN_PORT: widget.port_combo_box.currentText(),
            SETPOINT: widget.temperature_spinbox.value(),
            MEASUREMENT_INTERVAL: widget.interval_spinbox.value(),
            MINIMUM_MEASUREMENTS: widget.minimum_measurements_spinbox.value(),
            TOLERANCE: widget.tolerance_spinbox.value(),
        }

    def widget(self) -> SetSetpointWidget:  # implementation
        return self.data_widget

    def create_sequence_step(self, _) -> SequenceStep:  # implementation
        widget = self.data_widget.data_widget
        return SetSetpointStep(
            widget.port_combo_box.currentText(),
            widget.temperature_spinbox.value(),
            widget.interval_spinbox.value(),
            widget.minimum_measurements_spinbox.value(),
            widget.tolerance_spinbox.value(),
        )
