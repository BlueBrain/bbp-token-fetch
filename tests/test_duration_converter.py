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
    with pytest.raises(ValueError) as e:
        convert_duration_to_sec(duration)
    assert "The number detected in the input duration need to be positive" in str(
        e.value
    )

    duration = "time"
    with pytest.raises(TypeError) as e:
        convert_duration_to_sec(duration)
    assert "not of the form:\n'{float > 0}{{eventual unit of time}}'" in str(e.value)

    duration = "5weeks"
    with pytest.raises(ValueError) as e:
        convert_duration_to_sec(duration)
    assert (
        "does not correspond to these time units : seconds, minutes, hours, days"
        in str(e.value)
    )


def test_convert_string_to_time_unit():

    time_unit = "s"
    assert _convert_string_to_time_unit(time_unit) == 1

    time_unit = "d"
    assert _convert_string_to_time_unit(time_unit) == 86400

    time_unit = "others"
    with pytest.raises(ValueError) as e:
        _convert_string_to_time_unit(time_unit)
    assert (
        "does not correspond to these time units : seconds, minutes, hours, days"
        in str(e.value)
    )
