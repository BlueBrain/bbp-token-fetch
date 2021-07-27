import pytest
from blue_brain_token_fetch.duration_converter import (
    convert_duration_to_sec,
    _convert_string_to_time_unit,
)


def test_convert_duration_to_sec():

    duration = "3"
    assert convert_duration_to_sec(duration) == 3.0

    duration = "10seconds"
    assert convert_duration_to_sec(duration) == 10.0

    duration = "0.5h"
    assert convert_duration_to_sec(duration) == 1800.0

    # Errors:

    duration = "-0.5sec"
    with pytest.raises(SystemExit) as e:
        convert_duration_to_sec(duration)
    assert e.value.code == 1

    duration = "time"
    with pytest.raises(SystemExit) as e:
        convert_duration_to_sec(duration)
    assert e.value.code == 1

    duration = "5weeks"
    with pytest.raises(SystemExit) as e:
        convert_duration_to_sec(duration)
    assert e.value.code == 1


def test_convert_string_to_time_unit():

    time_unit = "s"
    assert _convert_string_to_time_unit(time_unit) == 1

    time_unit = "d"
    assert _convert_string_to_time_unit(time_unit) == 86400

    time_unit = "others"
    with pytest.raises(SystemExit) as e:
        _convert_string_to_time_unit(time_unit)
    assert e.value.code == 1
