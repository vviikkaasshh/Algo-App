import pandas as pd
from .ValidateInputData import *

class DoubleExponentialMovingAverage:
    """
    Stochastic Momentum Index Technical Indicator class implementation.
    Args:
        input_data (pandas.DataFrame): The input data. Required input columns
            are ``high``, ``low``, ``close``. The index is of type
            ``pandas.DatetimeIndex``.
        period (int, default=5): The past periods to be used for the
            calculation of the indicator.
        smoothing_period (int, default=3): The number of periods to be used
            when smoothing.
        double_smoothing_period (int, default=3): The number of periods to
            be used when double smoothing.
        fill_missing_values (bool, default=True): If set to True, missing
            values in the input data are being filled.
    Attributes:
        _input_data (pandas.DataFrame): The ``input_data`` after preprocessing.
        _ti_data (pandas.DataFrame): The calculated indicator. Index is of type
            ``pandas.DatetimeIndex``. It contains one column, the ``smi``.
        _properties (dict): Indicator properties.
        _calling_instance (str): The name of the class.
    Raises:
        WrongTypeForInputParameter: Input argument has wrong type.
        WrongValueForInputParameter: Unsupported value for input argument.
        NotEnoughInputData: Not enough data for calculating the indicator.
        TypeError: Type error occurred when validating the ``input_data``.
        ValueError: Value error occurred when validating the ``input_data``.
    """
    def __init__(self, input_data, period=10):
        self._period = period
        self._input_data = validateInputData(input_data,
                              ["close"])
        self._ti_data = self._calculateTi()

    def getTiData(self):
        """
        Returns the Technical Indicator values for the whole period.
        Returns:
            pandas.DataFrame: The Technical Indicator values.
        """

        return self._ti_data
        
    def _calculateTi(self):
        """
        Calculates the technical indicator for the given input data. The input
        data are taken from an attribute of the parent class.
        Returns:
            pandas.DataFrame: The calculated indicator. Index is of type
            ``pandas.DatetimeIndex``. It contains one column, the ``dema``.
        Raises:
            NotEnoughInputData: Not enough data for calculating the indicator.
        """

        # Not enough data for the requested period
        if len(self._input_data.index) < self._period:
            raise Exception('Double Exponential Moving Average',
                                     self._period, len(self._input_data.index))

        dema = pd.DataFrame(index=self._input_data.index, columns=['dema'],
                            data=0, dtype='float64')

        # Exponential moving average of prices
        ema = self._input_data.ewm(
                span=self._period, min_periods=self._period, adjust=False,
                axis=0).mean()

        # Exponential moving average of the exponential moving average
        # ema_of_ema = ema.ewm(
        #     span=self._period, min_periods=self._period, adjust=False,
        #     axis=0).mean()

        # dema['dema'] = (2 * ema) - ema_of_ema

        return ema.round(4)

    def getTiSignal(self):
        """
        Calculates and returns the trading signal for the calculated technical
        indicator.
        Returns:
            {('hold', 0), ('buy', -1), ('sell', 1)}: The calculated trading
            signal.
        """

        # Not enough data for calculating trading signal
        if len(self._ti_data.index) < 1:
            return 'hold'

        # Close price is below Moving Average
        if self._input_data['close'].iat[-1] < self._ti_data['dema'].iat[-1]:
            return 'buy'

        return 'hold'