
from src.evidence.location_intelligence import group_location_points
def test_location_visit_summary_tracks_daily_counts_and_time_range():
    clusters = [
        {
            "center_latitude": 28.6,
            "center_longitude": 77.2,
            "point_count": 3,
            "points": [
                {
                    "event_time": datetime(
                        2026, 1, 15, 9, 0, tzinfo=timezone.utc
                    )
                },
                {
                    "event_time": datetime(
                        2026, 1, 15, 11, 30, tzinfo=timezone.utc
                    )
                },
                {
                    "event_time": datetime(
                        2026, 1, 16, 14, 0, tzinfo=timezone.utc
                    )
                },
            ],
        }
    ]

    summaries = summarize_location_visits(clusters)
    summary = summaries[0]

    assert summary["daily_point_counts"] == {
        datetime(2026, 1, 15, tzinfo=timezone.utc).date(): 2,
        datetime(2026, 1, 16, tzinfo=timezone.utc).date(): 1,
    }
    assert summary["first_observed_at"] == datetime(
        2026, 1, 15, 9, 0, tzinfo=timezone.utc
    )
    assert summary["last_observed_at"] == datetime(
        2026, 1, 16, 14, 0, tzinfo=timezone.utc
    )


def test_nearby_points_are_grouped_together():
    records = [
        {"latitude": 28.6000, "longitude": 77.2000},
        {"latitude": 28.6001, "longitude": 77.2001},
        {"latitude": 28.6002, "longitude": 77.2001},
    ]

    clusters = group_location_points(records, radius_meters=100)

    assert len(clusters) == 1
    assert clusters[0]["point_count"] == 3


def test_far_apart_points_form_separate_clusters():
    records = [
        {"latitude": 28.6000, "longitude": 77.2000},
        {"latitude": 28.7000, "longitude": 77.3000},
    ]

    clusters = group_location_points(records, radius_meters=100)

    assert len(clusters) == 2
    assert all(cluster["point_count"] == 1 for cluster in clusters)


def test_invalid_coordinates_are_skipped():
    records = [
        {"latitude": 28.6000, "longitude": 77.2000},
        {"latitude": 120, "longitude": 77.2000},
        {"latitude": "invalid", "longitude": 77.2000},
    ]

    clusters = group_location_points(records)

    assert len(clusters) == 1
    assert clusters[0]["point_count"] == 1


from datetime import datetime, timezone

from src.evidence.location_intelligence import summarize_location_visits


def test_location_visits_count_distinct_dates():
    clusters = [
        {
            "center_latitude": 28.6,
            "center_longitude": 77.2,
            "point_count": 3,
            "points": [
                {
                    "event_time": datetime(
                        2026, 1, 15, 20, 0, tzinfo=timezone.utc
                    )
                },
                {
                    "event_time": datetime(
                        2026, 1, 15, 22, 0, tzinfo=timezone.utc
                    )
                },
                {
                    "event_time": datetime(
                        2026, 1, 16, 6, 0, tzinfo=timezone.utc
                    )
                },
            ],
        }
    ]

    summaries = summarize_location_visits(clusters)

    assert summaries[0]["point_count"] == 3
    assert summaries[0]["valid_timestamps"] == 3
    assert summaries[0]["distinct_dates"] == 2
    assert len(summaries[0]["visit_dates"]) == 2


from datetime import datetime, timezone

from src.evidence.location_intelligence import summarize_overnight_presence


def test_overnight_presence_counts_distinct_nights():
    clusters = [
        {
            "center_latitude": 28.6,
            "center_longitude": 77.2,
            "point_count": 4,
            "points": [
                {
                    "event_time": datetime(
                        2026, 1, 15, 22, 30, tzinfo=timezone.utc
                    )
                },
                {
                    "event_time": datetime(
                        2026, 1, 16, 2, 0, tzinfo=timezone.utc
                    )
                },
                {
                    "event_time": datetime(
                        2026, 1, 16, 22, 15, tzinfo=timezone.utc
                    )
                },
                {
                    "event_time": datetime(
                        2026, 1, 17, 3, 0, tzinfo=timezone.utc
                    )
                },
            ],
        }
    ]

    summaries = summarize_overnight_presence(
        clusters,
        night_start_hour=22,
        night_end_hour=6,
        timezone_offset_hours=0,
    )

    assert summaries[0]["overnight_point_count"] == 4
    assert summaries[0]["distinct_overnight_dates"] == 2

def test_location_visit_summary_counts_weekdays_and_weekends():
    clusters = [
        {
            "center_latitude": 28.6,
            "center_longitude": 77.2,
            "point_count": 3,
            "points": [
                # Thursday
                {
                    "event_time": datetime(
                        2026, 1, 15, 9, 0, tzinfo=timezone.utc
                    )
                },
                # Saturday
                {
                    "event_time": datetime(
                        2026, 1, 17, 10, 0, tzinfo=timezone.utc
                    )
                },
                # Sunday
                {
                    "event_time": datetime(
                        2026, 1, 18, 11, 0, tzinfo=timezone.utc
                    )
                },
            ],
        }
    ]

    summary = summarize_location_visits(clusters)[0]

    assert summary["weekday_point_count"] == 1
    assert summary["weekend_point_count"] == 2
    assert summary["weekday_dates"] == [
        datetime(2026, 1, 15).date()
    ]
    assert summary["weekend_dates"] == [
        datetime(2026, 1, 17).date(),
        datetime(2026, 1, 18).date(),
    ]

def test_location_visit_summary_counts_local_time_of_day_buckets():
    clusters = [
        {
            "center_latitude": 28.6,
            "center_longitude": 77.2,
            "point_count": 4,
            "points": [
                # 09:00 IST — morning
                {
                    "event_time": datetime(
                        2026, 1, 15, 3, 30, tzinfo=timezone.utc
                    )
                },
                # 13:00 IST — afternoon
                {
                    "event_time": datetime(
                        2026, 1, 15, 7, 30, tzinfo=timezone.utc
                    )
                },
                # 18:00 IST — evening
                {
                    "event_time": datetime(
                        2026, 1, 15, 12, 30, tzinfo=timezone.utc
                    )
                },
                # 23:00 IST — night
                {
                    "event_time": datetime(
                        2026, 1, 15, 17, 30, tzinfo=timezone.utc
                    )
                },
            ],
        }
    ]

    summary = summarize_location_visits(
        clusters,
        timezone_offset_hours=5.5,
    )[0]

    assert summary["time_of_day_counts"] == {
        "morning": 1,
        "afternoon": 1,
        "evening": 1,
        "night": 1,
    }