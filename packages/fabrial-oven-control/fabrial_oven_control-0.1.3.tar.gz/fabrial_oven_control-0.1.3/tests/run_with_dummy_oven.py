"""
I couldn't come up with an automated way to test this plugin's integration with Fabrial, so this is
the best we have for now.
"""

import fabrial


def test_fabrial_integration():
    """
    Launches `Fabrial` but uses a `DummyOven` instead of a `Quince10GCEOven`, then shows a control
    panel for the dummy oven.
    """
    fabrial.main()
