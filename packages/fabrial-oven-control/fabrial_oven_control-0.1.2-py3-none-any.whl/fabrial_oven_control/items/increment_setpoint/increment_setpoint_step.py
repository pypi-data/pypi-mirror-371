from pathlib import Path
from typing import Any

from fabrial import SequenceStep, StepRunner

from ...constants import TEMPERATURES_FILENAME
from ...utility import oven as oven_util, sequence as sequence_util
from ...utility.sequence import StabilizeTask
from .increment_setpoint_widget import BASE_NAME


class IncrementSetpointStep(SequenceStep):
    """Increment the oven's setpoint and stabilize; step."""

    def __init__(
        self,
        port: str,
        increment: float,
        measurement_interval_ms: int,
        minimum_measurements: int,
        tolerance: float,
    ):
        self.port = port
        self.increment = increment
        self.measurement_interval_ms = measurement_interval_ms
        self.minimum_measurements = minimum_measurements
        self.tolerance = tolerance

    async def run(self, runner: StepRunner, data_directory: Path):  # implementation
        oven = await oven_util.create_oven(self.port, self, runner)
        # read the current setpoint and add the increment
        setpoint = await sequence_util.read_setpoint_check(oven, self, runner) + self.increment

        await StabilizeTask(
            oven,
            self.measurement_interval_ms,
            self.minimum_measurements,
            self.tolerance,
            self,
            runner,
            data_directory,
            TEMPERATURES_FILENAME,
        ).run(setpoint)

    def reset(self):  # implementation
        return  # nothing to do

    def name(self) -> str:
        return BASE_NAME

    def metadata(self) -> dict[str, Any]:
        return {
            "Selected Oven Port": self.port,
            "Selected Increment": self.increment,
            "Selected Measurement Interval (ms)": self.measurement_interval_ms,
            "Selected Minimum Measurements": self.minimum_measurements,
            "Selected Tolerance": self.tolerance,
        }
