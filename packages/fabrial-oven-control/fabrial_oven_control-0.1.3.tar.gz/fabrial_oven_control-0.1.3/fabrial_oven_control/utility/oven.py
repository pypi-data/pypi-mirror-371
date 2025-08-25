import os

from fabrial import SequenceStep, StepRunner

from ..oven import Oven
from ..quince10GCE import Quince10GCEOven

if os.environ.get("PYTEST_VERSION") is None:  # we're running normally

    async def create_oven(port: str, step: SequenceStep, runner: StepRunner) -> Oven:
        """Try to create a `Quince10GCEOven`, asking the user whether we should retry on failure."""
        while True:
            try:
                return Quince10GCEOven(port)
            except OSError:
                await runner.prompt_retry_cancel(step, "Failed to connect to oven.")

else:  # we're being run by `pytest`, so we'll return the dummy test oven
    print("Running in test mode and using a dummy oven")
    from dummy_oven import global_dummy_oven  # type: ignore

    async def create_oven(port: str, step: SequenceStep, runner: StepRunner) -> Oven:
        """Return the global dummy oven for testing."""
        return global_dummy_oven
