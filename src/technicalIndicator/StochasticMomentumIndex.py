import pandas as pd

class StochasticMomentumIndex:
    """
    Stochastic MomentumSS Index Technical Indicator class implementation.
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
    def __init__(self, input_data, period=10, smoothing_period=3,
                 double_smoothing_period=3, fill_missing_values=True):
        self._period = period
        self._smoothing_period = smoothing_period
        self._double_smoothing_period = double_smoothing_period
        self._input_data = input_data
        self._dema = None
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
            ``pandas.DatetimeIndex``. It contains one column, the ``smi``.
        Raises:
            NotEnoughInputData: Not enough data for calculating the indicator.
        """
        smi = pd.DataFrame(index=self._input_data.index, columns=['smi'],
                           data=None, dtype='float64')

        # Calculate highest high for the last periods
        smi['highest_high'] = self._input_data['high'].rolling(
            window=self._period, min_periods=self._period, center=False,
            win_type=None, on=None, axis=0, closed=None).max()

        # Calculate highest high for the last periods
        smi['lowest_low'] = self._input_data['low'].rolling(
            window=self._period, min_periods=self._period, center=False,
            win_type=None, on=None, axis=0, closed=None).min()

        # Midpoint between highest high and lowest low
        smi['midpoint'] = (smi['highest_high'] + smi['lowest_low']) / 2

        # Distance of Close from Midpoint
        smi['distance'] = self._input_data['close'] - smi['midpoint']

        # Exponential Moving Average of the distance
        smi['distance_ema'] = smi['distance'].ewm(
            span=self._smoothing_period, min_periods=self._smoothing_period,
            adjust=False, axis=0).mean()

        # Double Exponential Moving Average of the distance
        smi['distance_double_ema'] = smi['distance_ema'].ewm(
            span=self._double_smoothing_period,
            min_periods=self._double_smoothing_period, adjust=False, axis=0
        ).mean()

        # Difference between highest high and lowest low
        smi['hh_ll_diff'] = smi['highest_high'] - smi['lowest_low']

        # Exponential Moving Average of the difference between highest high and
        # lowest low
        smi['hh_ll_diff_ema'] = smi['hh_ll_diff'].ewm(
            span=self._smoothing_period, min_periods=self._smoothing_period,
            adjust=False, axis=0).mean()

        # Double Exponential Moving Average of the difference between highest
        # high and lowest low
        smi['hh_ll_diff_double_ema'] = smi['hh_ll_diff_ema'].ewm(
            span=self._double_smoothing_period,
            min_periods=self._double_smoothing_period, adjust=False, axis=0
        ).mean()

        # Calculate SMI
        smi['smi'] = 100 * (smi['distance_double_ema'] / (
                0.5 * smi['hh_ll_diff_double_ema']))
        dema = smi['smi'].ewm(
                span=self._period, min_periods=self._period, adjust=False,
                axis=0).mean()
        self._dema = dema.round(4)
        return smi[['smi']].round(4)


    def getSMIAndDema(self):
        """
        Gets latest SMI and DEMA
        """
        return (self._ti_data['smi'][-1], self._dema[-1])

    def getTiSignal(self):
        """
        Calculates and returns the trading signal for the calculated technical
        indicator.
        Returns:
            {('hold', 0), ('buy', -1), ('sell', 1)}: The calculated trading
            signal.
        """

        # Not enough data for calculating trading signal
        if len(self._ti_data.index) < 2:
            return 'hold'

        # Buy when SMI falls below -40
        if self._ti_data['smi'].iat[-2] > -40. > self._ti_data['smi'].iat[-1]:
            return 'buy'

        # Sell when SMI raises above +40
        if self._ti_data['smi'].iat[-2] < 40. < self._ti_data['smi'].iat[-1]:
            return 'sell'

        return 'hold'