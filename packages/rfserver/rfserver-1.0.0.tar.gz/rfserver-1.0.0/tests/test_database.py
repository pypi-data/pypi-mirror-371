

from rfserver.db.database import DetailDataBaseManager


def test_search_power_frequency():
    min_power = 56
    max_power = 60
    min_frequency = 103
    max_frequency = 109
    result = DetailDataBaseManager.search_power_frequency(min_power, max_power, min_frequency, max_frequency)

    assert result is not None
    assert type(result) is type([])

