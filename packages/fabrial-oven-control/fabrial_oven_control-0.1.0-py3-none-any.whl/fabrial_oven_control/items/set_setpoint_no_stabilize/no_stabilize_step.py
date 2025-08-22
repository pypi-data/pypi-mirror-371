from pathlib import Path
from typing import Any

from fabrial import SequenceStep, StepRunner

from ...utility import oven as oven_util, sequence as sequence_util
from .no_stabilize_widget import BASE_NAME


class NoStabilizeStep(SequenceStep):
    """Set the oven's setpoint without waiting for the temperature to stabilize; step."""

    def __init__(self, port: str, setpoint: float):
        self.port = port
        self.setpoint = setpoint

    async def run(self, runner: StepRunner, data_directory: Path):  # implementation
        oven = await oven_util.create_oven(self.port, self, runner)
        # clamp the setpoint
        setpoint = await sequence_util.clamp_setpoint(self.setpoint, oven, self, runner)
        # set the setpoint
        await sequence_util.set_setpoint_check(setpoint, oven, self, runner)

    def reset(self):  # implementation
        return  # nothing to do here

    def name(self) -> str:
        return BASE_NAME

    def metadata(self) -> dict[str, Any]:
        return {"Selected Oven Port": self.port, "Selected Setpoint": self.setpoint}
