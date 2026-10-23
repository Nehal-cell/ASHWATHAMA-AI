
from math import radians, sin, cos, asin, sqrt
from typing import Any


def _distance_meters(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    """Calculate the approximate distance between two GPS points."""
    earth_radius_meters = 6_371_000

    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    haversine = (
        sin(delta_lat / 2) ** 2
        + cos(lat1_rad)
        * cos(lat2_rad)
        * sin(delta_lon / 2) ** 2
    )

    haversine = min(1.0, max(0.0, haversine))

    return 2 * earth_radius_meters * asin(sqrt(haversine))


def group_location_points(
    records: list[dict[str, Any]],
    radius_meters: float = 100,
) -> list[dict[str, Any]]:
    """
    Group nearby GPS points into approximate location clusters.

    Each input record must contain latitude and longitude.
    Records without valid coordinates are skipped.

    This function groups coordinates only. It does not identify
    a home, workplace, person, or exact physical address.
    """
    if radius_meters <= 0:
        raise ValueError("radius_meters must be greater than zero.")

    clusters: list[dict[str, Any]] = []

    for record in records:
        try:
            latitude = float(record["latitude"])
            longitude = float(record["longitude"])
        except (KeyError, TypeError, ValueError):
            continue

        if (
            not -90 <= latitude <= 90
            or not -180 <= longitude <= 180
        ):
            continue

        matching_cluster = None

        for cluster in clusters:
            distance = _distance_meters(
                latitude,
                longitude,
                cluster["center_latitude"],
                cluster["center_longitude"],
            )

            if distance <= radius_meters:
                matching_cluster = cluster
                break

        if matching_cluster is None:
            clusters.append(
                {
                    "center_latitude": latitude,
                    "center_longitude": longitude,
                    "point_count": 1,
                    "points": [record],
                }
            )
        else:
            matching_cluster["points"].append(record)
            matching_cluster["point_count"] += 1

            points = matching_cluster["points"]

            matching_cluster["center_latitude"] = sum(
                float(point["latitude"]) for point in points
            ) / len(points)

            matching_cluster["center_longitude"] = sum(
                float(point["longitude"]) for point in points
            ) / len(points)

    return clusters


from collections import Counter
from datetime import datetime, timedelta, timezone


from collections import Counter
from datetime import datetime, timedelta, timezone


def summarize_location_visits(
    clusters: list[dict],
    timezone_offset_hours: float = 5.5,
) -> list[dict]:
    """
    Summarize GPS observations using UTC dates and local-time patterns.

    Distinct dates preserve UTC-date behavior. Daily counts,
    weekday/weekend patterns, and time-of-day buckets use local time.
    Observation gaps are not treated as continuous presence.
    """
    if not -12 <= timezone_offset_hours <= 14:
        raise ValueError("timezone_offset_hours is out of range.")

    local_timezone = timezone(
        timedelta(hours=timezone_offset_hours)
    )
    summaries = []

    for cluster in clusters:
        visit_dates = set()
        daily_point_counts = Counter()
        weekday_dates = set()
        weekend_dates = set()
        weekday_point_count = 0
        weekend_point_count = 0
        time_of_day_counts = Counter()
        valid_timestamps = []

        for point in cluster.get("points", []):
            event_time = point.get("event_time")

            if not isinstance(event_time, datetime):
                continue

            if event_time.tzinfo is None:
                continue

            utc_time = event_time.astimezone(timezone.utc)
            local_time = event_time.astimezone(local_timezone)
            valid_timestamps.append(local_time)

            # Preserve the original UTC-date behavior.
            visit_dates.add(utc_time.date())

            # Local-date metrics use the configured timezone.
            local_date = local_time.date()
            daily_point_counts[local_date] += 1

            if local_date.weekday() < 5:
                weekday_point_count += 1
                weekday_dates.add(local_date)
            else:
                weekend_point_count += 1
                weekend_dates.add(local_date)

            hour = local_time.hour

            if 6 <= hour < 12:
                time_of_day_counts["morning"] += 1
            elif 12 <= hour < 17:
                time_of_day_counts["afternoon"] += 1
            elif 17 <= hour < 21:
                time_of_day_counts["evening"] += 1
            else:
                time_of_day_counts["night"] += 1

        for bucket in ("morning", "afternoon", "evening", "night"):
            time_of_day_counts.setdefault(bucket, 0)

        summaries.append(
            {
                "center_latitude": cluster["center_latitude"],
                "center_longitude": cluster["center_longitude"],
                "point_count": cluster["point_count"],
                "distinct_dates": len(visit_dates),
                "valid_timestamps": len(valid_timestamps),
                "visit_dates": sorted(visit_dates),
                "daily_point_counts": dict(daily_point_counts),
                "first_observed_at": (
                    min(valid_timestamps) if valid_timestamps else None
                ),
                "last_observed_at": (
                    max(valid_timestamps) if valid_timestamps else None
                ),
                "weekday_point_count": weekday_point_count,
                "weekend_point_count": weekend_point_count,
                "weekday_dates": sorted(weekday_dates),
                "weekend_dates": sorted(weekend_dates),
                "time_of_day_counts": dict(time_of_day_counts),
                "timezone_offset_hours": timezone_offset_hours,
            }
        )

    return summaries
from datetime import timedelta, timezone


def summarize_overnight_presence(
    clusters: list[dict],
    night_start_hour: int = 22,
    night_end_hour: int = 6,
    timezone_offset_hours: float = 5.5,
) -> list[dict]:
    """
    Summarize GPS points recorded during local overnight hours.

    Dates are counted by the local calendar date on which the
    overnight period starts. This is a pattern summary, not proof
    that a location is someone's home.
    """
    if not 0 <= night_start_hour <= 23:
        raise ValueError("night_start_hour must be between 0 and 23.")

    if not 0 <= night_end_hour <= 23:
        raise ValueError("night_end_hour must be between 0 and 23.")

    if night_start_hour == night_end_hour:
        raise ValueError("Night start and end hours must differ.")

    if not -12 <= timezone_offset_hours <= 14:
        raise ValueError("timezone_offset_hours is out of range.")

    local_timezone = timezone(
        timedelta(hours=timezone_offset_hours)
    )
    summaries = []

    for cluster in clusters:
        overnight_dates = set()
        overnight_point_count = 0

        for point in cluster.get("points", []):
            event_time = point.get("event_time")

            if not isinstance(event_time, datetime):
                continue

            if event_time.tzinfo is None:
                continue

            local_time = event_time.astimezone(local_timezone)
            hour = local_time.hour

            if night_start_hour > night_end_hour:
                is_overnight = (
                    hour >= night_start_hour or hour < night_end_hour
                )
            else:
                is_overnight = (
                    night_start_hour <= hour < night_end_hour
                )

            if not is_overnight:
                continue

            overnight_point_count += 1

            # After midnight, assign the point to the previous night's date.
            night_date = local_time.date()

            if hour < night_end_hour:
                night_date -= timedelta(days=1)

            overnight_dates.add(night_date)

        summaries.append(
            {
                "center_latitude": cluster["center_latitude"],
                "center_longitude": cluster["center_longitude"],
                "point_count": cluster["point_count"],
                "overnight_point_count": overnight_point_count,
                "distinct_overnight_dates": len(overnight_dates),
                "overnight_dates": sorted(overnight_dates),
            }
        )

    return summaries
