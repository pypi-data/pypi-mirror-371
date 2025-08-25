from pathlib import Path

from fabrial import SequenceStep, StepRunner

from ...utility import oven as oven_util, sequence as sequence_util
from .record_temperature_widget import FILENAME, NAME


class RecordTemperatureStep(SequenceStep):
    """Record the oven's temperature once; step."""

    def __init__(self, port: str):
        self.port = port

    async def run(self, runner: StepRunner, data_directory: Path):  # implementation
        oven = await oven_util.create_oven(self.port, self, runner)
        temperature, _ = await sequence_util.read_temperature_check(oven, self, runner)

        with open(data_directory.joinpath(FILENAME), "w") as f:
            f.write(f"temperature\n{temperature}\n")

    def reset(self):  # implementation
        return  # nothing to do

    def name(self) -> str:  # implementation
        return NAME
