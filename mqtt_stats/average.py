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

    def avg(self) -> float:
        """Calculate the average of the passed in values."""
        tstamp = datetime.datetime.now(datetime.timezone.utc)
        for i in range(len(self.values)):
            if tstamp - self.values[i][0] <= self.period:
                self.values = self.values[i:]
                break

        if len(self.values) == 0:
            return 0.0
        return sum([x[1] for x in self.values]) / len(self.values)

    def add(self, value: int) -> None:
        """Add a value to the average."""
        self.values.append((datetime.datetime.now(datetime.timezone.utc), value))
