"""
Contains testing utilities such as a dummy oven class that replaces the Quince 10 GCE oven class
if the plugin is being run from `pytest`.
"""

from fabrial.custom_widgets import Button, DoubleSpinBox, Label, Widget
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QGridLayout

from fabrial_oven_control.oven import Oven


class DummyOven(Oven):
    """A dummy oven used for testing that can have its temperature and setpoint edited."""

    def __init__(self):
        self.temperature = 0.0
        self.setpoint = 0.0
        self.connected = False
        self.testing_minimum_setpoint = 0.0
        self.testing_maximum_setpoint = 0.0

    def read_temperature(self) -> float | None:  # implementation
        return self.temperature if self.connected else None

    def read_setpoint(self) -> float | None:  # implementation
        return self.setpoint if self.connected else None

    def set_setpoint(self, setpoint: float) -> bool:  # implementation
        if self.connected:
            self.setpoint = setpoint
            return True
        return False

    def minimum_setpoint(self) -> float:  # implementation
        return self.testing_minimum_setpoint

    def maximum_setpoint(self) -> float:  # implementation
        return self.testing_maximum_setpoint

    # ----------------------------------------------------------------------------------------------
    # testing methods
    def testing_set_temperature(self, temperature: float):
        """Set the temperature the oven outputs when connected."""
        self.temperature = temperature

    def testing_set_setpoint(self, setpoint: float):
        """Set the setpoint the oven outputs when connected."""
        print("here")
        self.setpoint = setpoint
        print(self.setpoint)

    def testing_set_connected(self, connected: bool):
        """
        Set whether the oven is connected. If it isn't, `read_temperature()` and `read_setpoint()`
        will both return `None`, and `set_setpoint()` will return `False`.
        """
        self.connected = connected

    def testing_set_minimum_setpoint(self, setpoint: float):
        """Set the output of `minimum_setpoint()`."""
        self.testing_minimum_setpoint = setpoint

    def testing_set_maximum_setpoint(self, setpoint: float):
        """Set the output of `maximum_setpoint()`."""
        self.testing_maximum_setpoint = setpoint


global_dummy_oven = DummyOven()


class DummyOvenControlPanel(Widget):
    """Control panel for the dummy oven."""

    def __init__(self):
        layout = QGridLayout()
        Widget.__init__(self, layout)

        self.setWindowTitle("Dummy Oven Control Panel")

        self.connection_label = Label()
        layout.addWidget(
            Button(
                "Connect",
                lambda: global_dummy_oven.testing_set_connected(True),
            ),
            0,
            0,
        )
        layout.addWidget(
            Button(
                "Disconnect",
                lambda: global_dummy_oven.testing_set_connected(False),
            ),
            0,
            1,
        )
        layout.addWidget(self.connection_label, 0, 2)

        self.temperature_label = Label()
        temperature_spinbox = DoubleSpinBox()
        layout.addWidget(temperature_spinbox, 1, 0)
        layout.addWidget(
            Button(
                "Set Temperature",
                lambda: global_dummy_oven.testing_set_temperature(temperature_spinbox.value()),
            ),
            1,
            1,
        )
        layout.addWidget(self.temperature_label, 1, 2)

        self.setpoint_label = Label()
        setpoint_spinbox = DoubleSpinBox()
        layout.addWidget(setpoint_spinbox, 2, 0)
        layout.addWidget(
            Button(
                "Set Setpoint",
                lambda: global_dummy_oven.testing_set_setpoint(setpoint_spinbox.value()),
            ),
            2,
            1,
        )
        layout.addWidget(self.setpoint_label, 2, 2)

        self.minimum_label = Label()
        minimum_spinbox = DoubleSpinBox()
        layout.addWidget(minimum_spinbox, 3, 0)
        layout.addWidget(
            Button(
                "Set Minimum",
                lambda: global_dummy_oven.testing_set_minimum_setpoint(minimum_spinbox.value()),
            ),
            3,
            1,
        )
        layout.addWidget(self.minimum_label, 3, 2)

        self.maximum_label = Label()
        maximum_spinbox = DoubleSpinBox()
        layout.addWidget(maximum_spinbox, 4, 0)
        layout.addWidget(
            Button(
                "Set Maximum",
                lambda: global_dummy_oven.testing_set_maximum_setpoint(maximum_spinbox.value()),
            ),
            4,
            1,
        )
        layout.addWidget(self.maximum_label, 4, 2)

        self.label_update_timer = QTimer()
        self.label_update_timer.setInterval(100)  # 0.1 second interval
        self.label_update_timer.timeout.connect(self.update_labels)
        self.label_update_timer.start()

    def update_labels(self):
        """Update labels (this gets called repeatedly)."""
        self.connection_label.setText(
            "Connected" if global_dummy_oven.connected else "Disconnected"
        )
        self.temperature_label.setText(str(global_dummy_oven.temperature))
        self.setpoint_label.setText(str(global_dummy_oven.setpoint))
        self.minimum_label.setText(str(global_dummy_oven.testing_minimum_setpoint))
        self.maximum_label.setText(str(global_dummy_oven.testing_maximum_setpoint))


global_control_panel: DummyOvenControlPanel | None = None


def instantiate_control_panel():
    """Instantiates the dummy oven control panel."""
    global global_control_panel
    global_control_panel = DummyOvenControlPanel()
    global_control_panel.show()


# need to delay this because we can't create a widget before `Fabrial.main()` runs
QTimer.singleShot(0, instantiate_control_panel)
