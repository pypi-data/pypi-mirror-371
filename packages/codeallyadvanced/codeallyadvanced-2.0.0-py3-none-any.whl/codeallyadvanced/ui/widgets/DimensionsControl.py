
from typing import Callable

from logging import Logger
from logging import getLogger

from wx.lib.sized_controls import SizedPanel

from codeallybasic.Dimensions import Dimensions

from codeallyadvanced.ui.widgets.DualSpinnerControl import DualSpinnerControl
from codeallyadvanced.ui.widgets.DualSpinnerControl import SpinnerValues


class DimensionsControl(DualSpinnerControl):
    """
    A facade around the basic dual spinner control;   Essentially
        * Converts the spinner values to and from the Dimension type;
        * Handles the spinner callback
        * Forwards the spinner values as Dimension values
    """
    DIMENSION_MIN_VALUE: int = 50
    DIMENSION_MAX_VALUE: int = 300

    def __init__(self, sizedPanel: SizedPanel, displayText: str,
                 valueChangedCallback: Callable,
                 minValue: int = DIMENSION_MIN_VALUE, maxValue: int = DIMENSION_MAX_VALUE,
                 setControlsSize: bool = True):
        """

        Args:
            sizedPanel             The parent window
            displayText:           The text to display as the position  title
            valueChangedCallback:  The method to call when the value changes;  The method should expect the
                                   first parameter to be a Dimension argument that is the new value
            minValue:              The minimum dimension value
            maxValue:              The maximum dimension value
            setControlsSize
        """
        self.logger:                     Logger     = getLogger(__name__)
        self._dimensionsChangedCallback: Callable   = valueChangedCallback
        self._dimensions:                Dimensions = Dimensions()

        super().__init__(sizedPanel, displayText, self._onSpinValueChangedCallback, minValue, maxValue, setControlsSize)

    def _setDimensions(self, newValue: Dimensions):
        self._dimensions  = newValue
        self.spinnerValues = SpinnerValues(value0=newValue.width, value1=newValue.height)

    dimensions = property(fset=_setDimensions, doc='Write only property to set dimensions on control')

    def _onSpinValueChangedCallback(self, spinnerValues: SpinnerValues):
        self.logger.info(f'{spinnerValues}')

        self._dimensions.width  = spinnerValues.value0
        self._dimensions.height = spinnerValues.value1

        self._dimensionsChangedCallback(self._dimensions)
