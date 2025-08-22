import typing
from typing import Mapping, Self

from fabrial import Json, SequenceStep, WidgetDataItem

from ...constants import OVEN_PORT, SETPOINT
from .no_stabilize_step import NoStabilizeStep
from .no_stabilize_widget import NoStabilizeWidget


class NoStabilizeItem(WidgetDataItem):
    """Set the oven's setpoint without waiting for the temperature to stabilize; item."""

    def __init__(self, port: str | None, setpoint: float):
        self.data_widget = NoStabilizeWidget(port, setpoint)

    @classmethod
    def deserialize(cls, serialized_obj: Mapping[str, Json]) -> Self:  # implementation
        item = cls(
            typing.cast(str, serialized_obj[OVEN_PORT]),
            typing.cast(float, serialized_obj[SETPOINT]),
        )
        item.data_widget.handle_setpoint_change()
        return item

    def serialize(self) -> dict[str, Json]:  # implementation
        return {
            OVEN_PORT: self.data_widget.port_combo_box.currentText(),
            SETPOINT: self.data_widget.setpoint_spinbox.value(),
        }

    def widget(self) -> NoStabilizeWidget:  # implementation
        return self.data_widget

    def create_sequence_step(self, _) -> SequenceStep:  # implementation
        return NoStabilizeStep(
            self.data_widget.port_combo_box.currentText(), self.data_widget.setpoint_spinbox.value()
        )
