import typing
from typing import Mapping, Self

from fabrial import Json, SequenceStep, WidgetDataItem

from ...constants import OVEN_PORT
from .record_setpoint_step import RecordSetpointStep
from .record_setpoint_widget import RecordSetpointWidget


class RecordSetpointItem(WidgetDataItem):
    """Record the oven's setpoint once; item."""

    def __init__(self, port: str | None = None):
        self.data_widget = RecordSetpointWidget(port)

    @classmethod
    def deserialize(cls, serialized_obj: Mapping[str, Json]) -> Self:  # implementation
        return cls(typing.cast(str, serialized_obj[OVEN_PORT]))

    def serialize(self) -> dict[str, Json]:  # implementation
        return {OVEN_PORT: self.data_widget.port_combo_box.currentText()}

    def widget(self) -> RecordSetpointWidget:  # implementation
        return self.data_widget

    def create_sequence_step(self, _) -> SequenceStep:  # implementation
        return RecordSetpointStep(self.data_widget.port_combo_box.currentText())
