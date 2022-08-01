import datetime

import pytest

from mqtt_stats.average import TimedAverage


@pytest.fixture
def average():
    return TimedAverage(period=10)


# ganked from
# https://stackoverflow.com/questions/20503373/how-to-monkeypatch-pythons-datetime-datetime-now-with-py-test
# noqa: E501,W505
@pytest.fixture
def freeze(monkeypatch):
    """Now() manager patches datetime return a fixed, settable, value
    (freezes time)
    """
    original = datetime.datetime

    class FreezeMeta(type):
        def __instancecheck__(self, instance):
            if type(instance) == original or type(instance) == Freeze:
                return True

    class Freeze(datetime.datetime):
        __metaclass__ = FreezeMeta

        @classmethod
        def freeze(cls, val):
            cls.frozen = val

        @classmethod
        def now(cls, tz=None):
            return cls.frozen

        @classmethod
        def delta(cls, timedelta=None, **kwargs):
            """Moves time fwd/bwd by the delta"""
            from datetime import timedelta as td

            if not timedelta:
                timedelta = td(**kwargs)
            cls.frozen += timedelta

    monkeypatch.setattr(datetime, "datetime", Freeze)
    Freeze.freeze(original.now())
    return Freeze


def test_average_of_no_values_is_zero(average):
    assert average.avg() == 0.0


def test_average_of_two_numbers_is_correct(average):
    average.add(1)
    average.add(2)

    assert average.avg() == 1.5


def test_older_values_are_removed(average, freeze):
    freeze.freeze(datetime.datetime(2022, 8, 1))
    for val in range(1, 6):
        average.add(val + 2)
        freeze.delta(seconds=3)

    # only last 3 values will be counted as the delta is 3 seconds.
    # 3 * 3 = 9 < 10.
    # 4 * 3 = 12 > 10.
    # last 3 values are [3, 4, 5] + 2
    assert average.avg() == (7 + 6 + 5) / 3
