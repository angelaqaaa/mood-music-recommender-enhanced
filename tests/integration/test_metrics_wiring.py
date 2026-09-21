"""Tests that the recommendation and search callbacks actually record metrics.

The MetricsCollector methods existed for a long time before anything called
them, so /metrics reported zeros no matter how much traffic the app saw.
These tests drive the real callbacks and assert the counters move, so that
regression cannot come back quietly.
"""

import pytest
from dash._callback_context import context_value
from dash._utils import AttributeDict

from src.musicrec.core.engine import MusicRecommender
from src.musicrec.main import create_sample_data
from src.musicrec.metrics.collector import metrics_collector
from src.musicrec.web.app import MusicRecommenderDashApp


@pytest.fixture(scope="module")
def dash_app():
    """Build the Dash app once against sample data."""
    return MusicRecommenderDashApp(MusicRecommender(create_sample_data()))


def _unwrap(callback):
    """Get the plain function out of Dash's callback wrapper.

    Dash wraps a registered callback in one that expects an outputs_list
    argument it only has during a real request. The assert is deliberate: if
    a future Dash version drops __wrapped__, these tests must fail loudly
    rather than quietly stop exercising the callback.
    """
    inner = getattr(callback, "__wrapped__", None)
    assert inner is not None, "Dash callback is no longer wrapped; update this test"
    return inner


@pytest.fixture
def callbacks(dash_app):
    """Return the recommendation and search callbacks, with metrics reset."""
    metrics_collector.reset_metrics()
    registered = {
        key: entry["callback"]
        for key, entry in dash_app.app.callback_map.items()
        if "callback" in entry
    }
    recommend = next(k for k in registered if "recommendations-table.children" in k)
    search = next(k for k in registered if "track-selection-dropdown.options" in k)
    return _unwrap(registered[recommend]), _unwrap(registered[search])


def call_recommend(fn, n_clicks, active_tab, genre):
    """Invoke the recommendation callback the way Dash would."""
    return fn(n_clicks, active_tab, genre, None, "bfs", 2, 5, None, None, 10, 10)


class TestMetricsWiring:
    """The counters behind /metrics have to move when work happens."""

    def test_starts_at_zero(self, callbacks):
        """Resetting leaves every counter at zero."""
        assert metrics_collector.get_metrics()["total_requests"] == 0

    def test_no_click_is_not_a_request(self, callbacks):
        """Firing without a click must not count as a request."""
        recommend, _ = callbacks
        call_recommend(recommend, None, "genre", "rock")

        assert metrics_collector.get_metrics()["total_requests"] == 0

    def test_missing_genre_records_a_failure(self, callbacks):
        """Asking for genre recommendations with no genre is a failure."""
        recommend, _ = callbacks
        call_recommend(recommend, 1, "genre", None)

        metrics = metrics_collector.get_metrics()
        assert metrics["total_requests"] == 1
        assert metrics["failed_requests"] == 1
        assert metrics["successful_requests"] == 0
        assert metrics["request_types"]["recommendation_failures"] == 1

    def test_missing_track_records_a_failure(self, callbacks):
        """Asking for similar tracks with no track selected is a failure."""
        recommend, _ = callbacks
        call_recommend(recommend, 1, "track", None)

        metrics = metrics_collector.get_metrics()
        assert metrics["total_requests"] == 1
        assert metrics["failed_requests"] == 1

    def test_real_recommendation_records_a_success_with_latency(
        self, callbacks, dash_app
    ):
        """A recommendation that returns results counts as a success."""
        recommend, _ = callbacks
        genre = dash_app.recommender.get_available_genres()[0]
        call_recommend(recommend, 1, "genre", genre)

        metrics = metrics_collector.get_metrics()
        assert metrics["total_requests"] == 1
        assert metrics["successful_requests"] == 1
        assert metrics["failed_requests"] == 0
        assert metrics["request_types"]["recommendation"] == 1
        assert metrics["average_latency_ms"] > 0
        assert metrics["success_rate_percent"] == 100.0

    def test_search_records_a_success(self, callbacks):
        """Running a track search counts as a success under its own type."""
        _, search = callbacks
        context_value.set(
            AttributeDict(
                triggered_inputs=[
                    {"prop_id": "track-selection-dropdown.value", "value": "test"}
                ]
            )
        )
        search("test", None, None)

        metrics = metrics_collector.get_metrics()
        assert metrics["total_requests"] == 1
        assert metrics["successful_requests"] == 1
        assert metrics["request_types"]["search"] == 1

    def test_short_search_is_not_a_request(self, callbacks):
        """A search below the minimum length never reaches the engine."""
        _, search = callbacks
        context_value.set(
            AttributeDict(
                triggered_inputs=[
                    {"prop_id": "track-selection-dropdown.value", "value": "ab"}
                ]
            )
        )
        search("ab", None, None)

        assert metrics_collector.get_metrics()["total_requests"] == 0

    def test_success_rate_reflects_a_mix(self, callbacks, dash_app):
        """Two failures and one success give a third success rate."""
        recommend, _ = callbacks
        genre = dash_app.recommender.get_available_genres()[0]
        call_recommend(recommend, 1, "genre", None)
        call_recommend(recommend, 1, "track", None)
        call_recommend(recommend, 1, "genre", genre)

        metrics = metrics_collector.get_metrics()
        assert metrics["total_requests"] == 3
        assert metrics["successful_requests"] == 1
        assert metrics["failed_requests"] == 2
        assert round(metrics["success_rate_percent"]) == 33
