from fabrial import PluginCategory

from .items import (
    IncrementSetpointItem,
    NoStabilizeItem,
    RecordSetpointItem,
    RecordTemperatureItem,
    SetSetpointItem,
)
from .oven import Oven


# Fabrial entry point
def categories() -> list[PluginCategory]:
    return [
        PluginCategory(
            "Quince 10 GCE Lab Oven",
            [
                SetSetpointItem(None, 0, 5000, 150, 1),
                IncrementSetpointItem(None, 10, 5000, 150, 1),
                NoStabilizeItem(None, 0),
                RecordTemperatureItem(),
                RecordSetpointItem(),
            ],
        ),
    ]
