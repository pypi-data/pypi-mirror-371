import typing
from typing import Mapping, Self

from fabrial import Json, SequenceStep, WidgetDataItem

from ...constants import OVEN_PORT
from .record_temperature_step import RecordTemperatureStep
from .record_temperature_widget import RecordTemperatureWidget


class RecordTemperatureItem(WidgetDataItem):
    """Record the oven's temperature once; item."""

    def __init__(self, port: str | None = None):
        self.data_widget = RecordTemperatureWidget(port)

    @classmethod
    def deserialize(cls, serialized_obj: Mapping[str, Json]) -> Self:  # implementation
        return cls(typing.cast(str, serialized_obj[OVEN_PORT]))

    def serialize(self) -> dict[str, Json]:  # implementation
        return {OVEN_PORT: self.data_widget.port_combo_box.currentText()}

    def widget(self) -> RecordTemperatureWidget:  # implementation
        return self.data_widget

    def create_sequence_step(self, _) -> SequenceStep:  # implementation
        return RecordTemperatureStep(self.data_widget.port_combo_box.currentText())
