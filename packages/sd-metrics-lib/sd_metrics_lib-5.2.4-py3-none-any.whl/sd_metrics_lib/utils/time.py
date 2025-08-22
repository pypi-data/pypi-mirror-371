from sd_metrics_lib.utils.enums import VelocityTimeUnit

SECONDS_IN_HOUR = 3600
WORKING_HOURS_PER_DAY = 8
WORKING_DAYS_PER_WEEK = 5
WORKING_WEEKS_IN_MONTH = 4

# Python's date.weekday(): Monday=0
WEEKDAY_FRIDAY = 4


def get_seconds_in_day() -> int:
    return WORKING_HOURS_PER_DAY * SECONDS_IN_HOUR


def convert_time(
        spent_time_in_seconds: int,
        time_unit: VelocityTimeUnit,
        ideal_working_hours_per_day: int = WORKING_HOURS_PER_DAY
) -> float:
    if spent_time_in_seconds is None:
        return 0
    if time_unit == VelocityTimeUnit.HOUR:
        return spent_time_in_seconds / SECONDS_IN_HOUR
    elif time_unit == VelocityTimeUnit.DAY:
        return spent_time_in_seconds / SECONDS_IN_HOUR / ideal_working_hours_per_day
    elif time_unit == VelocityTimeUnit.WEEK:
        return spent_time_in_seconds / SECONDS_IN_HOUR / ideal_working_hours_per_day / WORKING_DAYS_PER_WEEK
    elif time_unit == VelocityTimeUnit.MONTH:
        return spent_time_in_seconds / SECONDS_IN_HOUR / ideal_working_hours_per_day / WORKING_DAYS_PER_WEEK / WORKING_WEEKS_IN_MONTH
