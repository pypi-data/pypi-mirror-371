# mypy: disable-error-code="misc"
import pytest

from core import datetime


class TestCore:
    def test_strftime(self) -> None:
        result = datetime(2023, 5, 1).strftime("%Y/%m/%d %E%EN%EY年")
        assert result == "2023/05/01 R令和5年"

    def test_strptime(self) -> None:
        result = datetime.strptime("2023/05/01 R令和5年", "%Y/%m/%d %E%EN%EY年")
        assert result == datetime(2023, 5, 1)


class TestPadding:
    # strftime tests
    @pytest.mark.parametrize(
        "dt, fmt, expected",
        [
            (datetime(2024, 5, 1), "%_Y", "2024"),
            (datetime(999, 5, 1), "%_Y", " 999"),
            (datetime(2024, 5, 1), "%_m", " 5"),
            (datetime(2024, 12, 1), "%_m", "12"),
            (datetime(2024, 5, 1), "%_d", " 1"),
            (datetime(2024, 5, 12), "%_d", "12"),
            (datetime(2024, 5, 1, 3, 4, 5), "%_H", " 3"),
            (datetime(2024, 5, 1, 13, 4, 5), "%_H", "13"),
            (datetime(2024, 5, 1, 15, 4, 5), "%_I", " 3"),
            (datetime(2024, 5, 1, 3, 4, 5), "%_M", " 4"),
            (datetime(2024, 5, 1, 3, 40, 5), "%_M", "40"),
            (datetime(2024, 5, 1, 3, 4, 5), "%_S", " 5"),
            (datetime(2024, 5, 1, 3, 4, 50), "%_S", "50"),
            (datetime(2024, 1, 8), "%_w", " 1"),  # Monday
            (datetime(2024, 1, 1), "%_j", "  1"),
            (datetime(2024, 4, 10), "%_j", "101"),
            (datetime(2023, 5, 1), "%_EY", " 5"),  # Reiwa 5
            (datetime(1998, 5, 1), "%_EY", "10"),  # Heisei 10
            (
                datetime(2024, 5, 1, 8, 7, 6),
                "%_Y/%_m/%_d %_H:%_M:%_S",
                "2024/ 5/ 1  8: 7: 6",
            ),
        ],
    )
    def test_strftime_padding(self, dt: datetime, fmt: str, expected: str) -> None:
        assert dt.strftime(fmt) == expected

    # strptime tests
    @pytest.mark.parametrize(
        "dt_str, fmt, expected_dt",
        [
            (" 999", "%_Y", datetime(999, 1, 1)),
            ("2024", "%_Y", datetime(2024, 1, 1)),
            (" 5", "%_m", datetime(1900, 5, 1)),
            ("12", "%_m", datetime(1900, 12, 1)),
            (" 1", "%_d", datetime(1900, 1, 1)),
            ("12", "%_d", datetime(1900, 1, 12)),
            (" 3", "%_H", datetime(1900, 1, 1, 3)),
            ("13", "%_H", datetime(1900, 1, 1, 13)),
            ("R 5/ 1", "%E%_EY/%_d", datetime(2023, 1, 1)),
            ("H10/12", "%E%_EY/%_d", datetime(1998, 1, 12)),
            (
                "2024/ 5/ 1  8: 7: 6",
                "%_Y/%_m/%_d %_H:%_M:%_S",
                datetime(2024, 5, 1, 8, 7, 6),
            ),
        ],
    )
    def test_strptime_padding_valid(
        self, dt_str: str, fmt: str, expected_dt: datetime
    ) -> None:
        result = datetime.strptime(dt_str, fmt)
        # Compare only the components present in the format string
        if "Y" in fmt or "y" in fmt or "E" in fmt:
            assert result.year == expected_dt.year
        if "m" in fmt:
            assert result.month == expected_dt.month
        if "d" in fmt:
            assert result.day == expected_dt.day
        if "H" in fmt or "I" in fmt:
            assert result.hour == expected_dt.hour
        if "M" in fmt:
            assert result.minute == expected_dt.minute
        if "S" in fmt:
            assert result.second == expected_dt.second

    @pytest.mark.parametrize(
        "dt_str, fmt",
        [
            ("5", "%_m"),
            ("1", "%_d"),
            ("3", "%_H"),
            ("2024/5/1", "%_Y/%_m/%_d"),
            ("R5/1", "%E%_EY/%_d"),
        ],
    )
    def test_strptime_padding_invalid(self, dt_str: str, fmt: str) -> None:
        with pytest.raises(ValueError):
            datetime.strptime(dt_str, fmt)
