import csv
import math
import time
from contextlib import AsyncExitStack
from datetime import datetime
from pathlib import Path
from typing import TextIO

from fabrial import SequenceStep, StepCancellation, StepRunner
from fabrial.plotting import LineHandle, PlotSettings, SymbolParams

from ..oven import Oven

MAXIMUM_ALLOWED_DISCONNECTS = 5


# public
class StabilizeTask:
    """
    Utility class that sets an oven's setpoint and waits for the temperature to stabilize.

    Parameters
    ----------
    oven
        The oven to use. It must already be connected.
    measurement_interval_ms
        The measurement interval in milliseconds.
    minimum_measurements
        The minimum number of within-**tolerance** measurements that need to be taken for the
        temperature to be "stable".
    tolerance
        How far off the temperature can be from the setpoint before the measurement is considered
        "unstable".
    step
        The step calling this function.
    runner
        The `StepRunner` running **step**.
    data_directory
        Where the step is recording data.
    temperature_filename
        The name of the file to record the temperatures to.

    Notes
    -----
    - The **oven** must already be connected, and the caller is responsible for disconnecting it.
    - This class will ensure the **setpoint** is within the oven's allowed range and will prompt
    the user if the setpoint is invalid.
    """

    def __init__(
        self,
        oven: Oven,
        measurement_interval_ms: int,
        minimum_measurements: int,
        tolerance: float,
        step: SequenceStep,
        runner: StepRunner,
        data_directory: Path,
        temperature_filename: str,
    ):
        self.oven = oven
        self.measurement_interval = measurement_interval_ms / 1000  # convert from ms to seconds
        self.minimum_measurements = minimum_measurements
        self.tolerance = tolerance
        self.step = step
        self.runner = runner
        self.data_directory = data_directory
        self.temperature_filename = temperature_filename

    # public
    async def run(self, selected_setpoint: float):
        """
        Set the oven's setpoint and wait for the temperature to stabilize. Record and plot the
        temperature while stabilizing.
        """
        # make sure the setpoint is within range
        setpoint = await clamp_setpoint(selected_setpoint, self.oven, self.step, self.runner)

        # set the setpoint
        await set_setpoint_check(setpoint, self.oven, self.step, self.runner)

        async with AsyncExitStack() as exit_stack:
            # more setup
            file = await self.create_temperature_file(exit_stack)
            # set up the plot
            plot_handle = await exit_stack.enter_async_context(
                self.runner.create_plot(
                    self.step,
                    "Oven",
                    PlotSettings("Oven Temperature", "Time (s)", "Temperature (°C)"),
                )
            )
            line_handle = await plot_handle.add_line(None, None, SymbolParams("o", "orange", 2))

            # how many "stable" measurements we've taken
            stable_measurement_count = 0
            # record the start time
            start_time = time.time()

            while stable_measurement_count < self.minimum_measurements:
                # we use this to account for the time it takes to measure
                current_time = time.time()

                # read the temperature
                temperature, failure_count = await read_temperature_check(
                    self.oven, self.step, self.runner
                )
                # punish failed measurements by making stabilization take longer. Clamp to 0
                stable_measurement_count = max(stable_measurement_count - failure_count, 0)
                # record data
                await self.record_measurement(file, start_time, temperature, line_handle)
                # only temperatures within tolerance are "stable"
                if abs(setpoint - temperature) <= self.tolerance:
                    stable_measurement_count += 1
                else:  # otherwise we are unstable; reset
                    stable_measurement_count = 0

                # wait for the next time so we measure on an interval
                await self.step.sleep_until(current_time + self.measurement_interval)

    async def record_measurement(
        self, file: TextIO, start_time: float, temperature: float, line_handle: LineHandle
    ):
        """
        Record the measurement datetime, temperature, and oven setpoint.

        Raises
        ------
        StepCancellation
            The user asked to cancel the step.
        """
        setpoint = await read_setpoint_check(self.oven, self.step, self.runner)
        csv.writer(file, lineterminator="\n").writerow([str(datetime.now()), temperature, setpoint])
        # add the datapoint to the line
        line_handle.add_point(time.time() - start_time, temperature)

    # private
    async def create_temperature_file(self, exit_stack: AsyncExitStack) -> TextIO:
        """
        Try to create the temperature file. If the operation fails, ask the user whether we should
        retry.

        Raises
        ------
        StepCancellation
            The user asked to cancel the step.
        """
        while True:
            try:
                file = exit_stack.enter_context(
                    # line buffered
                    open(self.data_directory.joinpath(self.temperature_filename), "w", 1)
                )
                # write the header
                csv.writer(file, lineterminator="\n").writerow(
                    ["Datetime", "Temperature", "Setpoint"]
                )
                return file
            except OSError:
                await self.runner.prompt_retry_cancel(
                    self.step, "Failed to create temperatures file."
                )
            await self.step.sleep(0)


# public
async def set_setpoint_check(setpoint: float, oven: Oven, step: SequenceStep, runner: StepRunner):
    """
    Try to set the oven's setpoint to **setpoint**. If the operation fails
    `MAXIMUM_ALLOWED_DISCONNECTS` times, ask the user if they want to retry or cancel the step.

    Raises
    ------
    StepCancellation
        The user asked to cancel the step.

    Notes
    -----
    This function *does not* clamp the setpoint to the oven's allowed range. You are responsible
    for ensuring the setpoint is valid.
    """
    while True:
        # try to set the setpoint
        disconnect_count = 0
        while not oven.set_setpoint(setpoint):
            disconnect_count += 1
            if disconnect_count < MAXIMUM_ALLOWED_DISCONNECTS:
                await step.sleep(1)  # arbitrary delay
                continue

            # we couldn't set the setpoint; ask the user what to do
            await runner.prompt_retry_cancel(step, "Failed to set the oven's setpoint.")
            disconnect_count = 0  # reset the disconnect count

        # make sure the setpoint was actually set
        measured_setpoint = await read_setpoint_check(oven, step, runner)
        if not math.isclose(measured_setpoint, setpoint):
            await runner.prompt_retry_cancel(step, "The oven's setpoint was not actually set.")
            continue

        return  # if we get here we successfully set the setpoint


# public
async def read_temperature_check(
    oven: Oven, step: SequenceStep, runner: StepRunner
) -> tuple[float, int]:
    """
    Read the **oven**'s temperature. If the read fails `MAXIMUM_ALLOWED_DISCONNECTS` times, ask
    the user try retry or cancel the **step**.

    Returns
    -------
    A tuple of (the temperature, how many times we failed to measure).

    Raises
    ------
    StepCancellation
        The user asked to cancel the step.
    """
    failure_count = 0
    disconnect_count = 0
    while (temperature := oven.read_temperature()) is None:
        failure_count += 1
        disconnect_count += 1
        if disconnect_count < MAXIMUM_ALLOWED_DISCONNECTS:
            await step.sleep(1)  # arbitrary delay
            continue

        # notify the user
        await runner.prompt_retry_cancel(step, "Failed to read oven temperature.")
        disconnect_count = 0

    return (temperature, failure_count)


# public
async def read_setpoint_check(oven: Oven, step: SequenceStep, runner: StepRunner) -> float:
    """
    Try to read the **oven**'s setpoint. If the read fails `MAXIMUM_ALLOWED_DISCONNECTS` times, ask
    the user try retry or cancel the **step**.

    Returns
    -------
    The setpoint.

    Raises
    ------
    StepCancellation
        The user asked to cancel the step.
    """
    disconnect_count = 0
    while (setpoint := oven.read_setpoint()) is None:
        disconnect_count += 1
        if disconnect_count < MAXIMUM_ALLOWED_DISCONNECTS:
            await step.sleep(1)  # arbitrary delay
            continue

        # notify the user
        await runner.prompt_retry_cancel(step, "Failed to read oven setpoint.")
        disconnect_count = 0

    return setpoint


# public
async def clamp_setpoint(
    setpoint: float, oven: Oven, step: SequenceStep, runner: StepRunner
) -> float:
    """
    Check that the **setpoint** is within the **oven**'s allowed range. If not, prompt the user on
    whether the clamp the setpoint or cancel the step.

    Returns
    -------
    A valid setpoint (possibly the original).

    Raises
    ------
    StepCancellation
        The user asked to cancel the step.
    """
    if setpoint < (minimum := oven.minimum_setpoint()):
        await prompt_for_clamp(
            "The selected setpoint is below the oven's minimum."
            "\n\nClamp to the minimum or cancel this step?",
            step,
            runner,
        )
        return minimum
    elif setpoint > (maximum := oven.maximum_setpoint()):
        await prompt_for_clamp(
            "The selected setpoint is above the oven's maximum."
            "\n\nClamp to the maximum or cancel this step?",
            step,
            runner,
        )
        return maximum

    return setpoint  # if it's within range just return the original


# private
async def prompt_for_clamp(message: str, step: SequenceStep, runner: StepRunner):
    """
    Prompt the user whether to clamp the setpoint or cancel the step.

    Raises
    ------
    StepCancellation
        The user asked to cancel the step.
    """
    match (response := await runner.prompt_user(step, message, {0: "Clamp", 1: "Cancel Step"})):
        case 0:  # clamp
            return
        case 1:  # cancel the step
            raise StepCancellation
        case _:  # this should never run
            raise ValueError(f"Got {response} but expected 0 or 1")
