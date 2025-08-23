from fabrial import SequenceStep, StepRunner

from ..quince10GCE import Quince10GCEOven


async def create_oven(port: str, step: SequenceStep, runner: StepRunner) -> Quince10GCEOven:
    """Try to create a `Quince10GCEOven`, asking the user whether we should retry on failure."""
    while True:
        try:
            return Quince10GCEOven(port)
        except OSError:
            await runner.prompt_retry_cancel(step, "Failed to connect to oven.")
