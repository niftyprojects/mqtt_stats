import datetime


class TimedAverage:
    """Calculates an average of a sequence of numbers over a time period."""

    def __init__(self, period: int):
        """Initialiaze TimedAverage class.

        Arguments:

        period
          Time period, in seconds, to run the average over.
        """
        self.period = datetime.timedelta(seconds=period)
        self.values = []

    def __trim_old(self) -> None:
        tstamp = datetime.datetime.now(datetime.timezone.utc)
        if len(self.values) > 0 and tstamp - self.values[-1][0] > self.period:
            self.values = []
        for i in range(len(self.values)):
            if tstamp - self.values[i][0] <= self.period:
                self.values = self.values[i:]
                break

    def avg(self) -> float:
        """Calculate the average of the passed in values."""
        self.__trim_old()

        if len(self.values) == 0:
            return 0.0
        return sum([x[1] for x in self.values]) / len(self.values)

    def add(self, value: int) -> None:
        """Add a value to the average."""
        self.values.append((datetime.datetime.now(datetime.timezone.utc), value))


class GroupedTimedAverage:
    """Calculates averages over several time periods."""

    def __init__(self, periods: dict[str:int]):
        """Create a group of TimedAverage classes.

        Arguments:

        periods
          Each key is used as a key name for the returned averages. The value
          associated with the key is the period in seconds to average over.
        """
        self.periods = {}
        for k, v in periods.items():
            self.periods[k] = TimedAverage(v)

    def add(self, val: int) -> None:
        """Add a value to all running averages."""
        for a in self.periods.values():
            a.add(val)

    def avg(self) -> dict[str:float]:
        """Calculate all the averages.

        Returns a dictionary of floats, with the keys as provided on initilization."""
        avgs = {}
        for k, v in self.periods.items():
            avgs[k] = v.avg()
        return avgs
