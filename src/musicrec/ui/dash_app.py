"""CSC111 Winter 2025: A Mood-Driven Music Recommender with Genre Hierarchies

Module for creating the visualization interface of the music recommender system.
This module builds a Dash application for interactive music recommendations.

Copyright and Usage Information
===============================
This file is Copyright (c) 2025 Qian (Angela) Su & Mengxuan (Connie) Guo.
"""

import time
from datetime import datetime

import dash
import networkx as nx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, State, callback_context, dcc, html

from ..metrics.collector import metrics_collector
from .explanations import generate_explanation, get_top_features
from .keyboard_navigation import KEYBOARD_NAVIGATION_JS
from .search import SearchEngine
from .styles import BUTTON_STYLES, CONTAINER_STYLES, RESPONSIVE_STYLES

# Optional import for code analysis
try:
    import python_ta
except ImportError:
    python_ta = None


class MusicRecommenderDashApp:
    """A Dash application for the mood-driven music recommender system.

    This class creates an interactive web interface for exploring and visualizing
    music recommendations based on genre, mood, and similarity.

    Instance Attributes:
        - recommender: The music recommender engine
        - app: The Dash application
    """

    def __init__(self, recommender):
        """Initialize the Dash application with a recommender engine.

        Args:
            recommender: The music recommender engine
        """
        self.recommender = recommender
        self.search_engine = SearchEngine(
            recommender, enable_fuzzy=True, fuzzy_threshold=0.6
        )
        self.app = dash.Dash(__name__, suppress_callback_exceptions=True)

        # Add custom CSS styles and JavaScript
        self.app.index_string = (
            """
        <!DOCTYPE html>
        <html>
            <head>
                {%metas%}
                <title>{%title%}</title>
                {%favicon%}
                {%css%}
                <style>
                """
            + RESPONSIVE_STYLES
            + """
                </style>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body>
                {%app_entry%}
                <footer>
                    {%config%}
                    {%scripts%}
                    {%renderer%}
                    <script>
                    """
            + KEYBOARD_NAVIGATION_JS
            + """
                    </script>
                </footer>
            </body>
        </html>
        """
        )

        # Set the app layout
        self.app.layout = self._create_layout()

        # Register callbacks
        self._register_callbacks()

        # Add metrics endpoint
        self._add_metrics_endpoint()

    def _create_layout(self):
        """Create the layout for the Dash application.

        Returns:
            The main layout div
        """
        # Get available genres, moods, and a sample of tracks
        genres = self.recommender.get_available_genres()
        moods = self.recommender.get_available_moods()

        # Get all tracks for the dropdown (no limit to make all songs available)
        all_tracks = []
        for track_id, node in self.recommender.genre_tree.tracks.items():
            # Get track and artist name with proper decoding
            track_name = node.data.get("track_name", track_id)
            artist_name = node.data.get("artist_name", "Unknown")

            # Create display name
            display_name = f"{track_name} - {artist_name}"

            all_tracks.append({"label": display_name, "value": track_id})

        # Sort tracks alphabetically by display name
        all_tracks.sort(key=lambda x: x["label"].lower())

        # Create the layout
        layout = html.Div(
            [
                html.Header(
                    [
                        html.H1(
                            "Mood-Driven Music Recommender with Genre Hierarchies",
                            style={"textAlign": "center", "marginBottom": "30px"},
                            id="main-title",
                        )
                    ],
                    role="banner",
                ),
                # Skip link for accessibility
                html.A(
                    "Skip to main content",
                    href="#main-content",
                    className="sr-only",
                    style={
                        "position": "absolute",
                        "left": "-10000px",
                        "top": "auto",
                        "width": "1px",
                        "height": "1px",
                        "overflow": "hidden",
                    },
                    tabIndex="1",
                ),
                # Metrics panel
                html.Div(
                    id="metrics-panel",
                    className="metrics-panel",
                    style={"display": "none"},
                ),
                # Main content area with responsive layout
                html.Main(
                    [
                        html.Div(
                            className="main-layout",
                            children=[
                                # Controls section
                                html.Section(
                                    [
                                        html.H3(
                                            "Search Options",
                                            id="search-options-heading",
                                        ),
                                        # Loading indicator
                                        html.Div(
                                            [
                                                html.Div(className="loading-spinner"),
                                                html.Span(
                                                    "Finding recommendations...",
                                                    **{"aria-live": "polite"},
                                                ),
                                            ],
                                            id="loading-indicator",
                                            className="loading-indicator",
                                            style={"display": "none"},
                                            role="status",
                                        ),
                                        # Search Type tabs
                                        dcc.Tabs(
                                            id="search-type-tabs",
                                            value="genre-mood",
                                            children=[
                                                dcc.Tab(
                                                    label="Search by Genre/Mood",
                                                    value="genre-mood",
                                                    children=[
                                                        # Genre selection
                                                        html.Label("Select Genre:"),
                                                        dcc.Dropdown(
                                                            id="genre-dropdown",
                                                            options=[
                                                                {
                                                                    "label": genre,
                                                                    "value": genre,
                                                                }
                                                                for genre in genres
                                                            ],
                                                            value=(
                                                                genres[0]
                                                                if genres
                                                                else None
                                                            ),
                                                            clearable=False,
                                                        ),
                                                        # Mood selection
                                                        html.Label(
                                                            "Select Mood (Optional):"
                                                        ),
                                                        dcc.Dropdown(
                                                            id="mood-dropdown",
                                                            options=[
                                                                {
                                                                    "label": mood,
                                                                    "value": mood,
                                                                }
                                                                for mood in moods
                                                            ],
                                                            value=None,
                                                            clearable=True,
                                                        ),
                                                        # Search method
                                                        html.Label("Search Method:"),
                                                        dcc.RadioItems(
                                                            id="search-method",
                                                            options=[
                                                                {
                                                                    "label": "Breadth-First Search (BFS)",
                                                                    "value": "bfs",
                                                                },
                                                                {
                                                                    "label": "Depth-First Search (DFS)",
                                                                    "value": "dfs",
                                                                },
                                                                {
                                                                    "label": "Direct Search",
                                                                    "value": "direct",
                                                                },
                                                            ],
                                                            value="direct",
                                                            labelStyle={
                                                                "display": "block"
                                                            },
                                                        ),
                                                        # Explanations for search methods
                                                        html.Div(
                                                            id="search-method-explanation",
                                                            style={
                                                                "margin-top": "10px",
                                                                "padding": "8px",
                                                                "background-color": "#f8f9fa",
                                                                "border-left": "3px solid #007bff",
                                                                "font-size": "12px",
                                                                "color": "#6c757d",
                                                            },
                                                            children=[
                                                                html.P(
                                                                    "📍 Direct Search: Finds tracks exactly matching your genre/mood selections"
                                                                ),
                                                                html.P(
                                                                    "🌐 BFS (Breadth-First): Explores related genres level by level, finding diverse recommendations"
                                                                ),
                                                                html.P(
                                                                    "🎯 DFS (Depth-First): Digs deep into specific genre paths, finding focused recommendations"
                                                                ),
                                                            ],
                                                        ),
                                                        # Number of results to show - set default to 50
                                                        html.Label(
                                                            "Number of Results:"
                                                        ),
                                                        dcc.Slider(
                                                            id="results-count-slider",
                                                            min=5,
                                                            max=100,
                                                            step=5,
                                                            value=50,  # Changed to 50
                                                            marks={
                                                                i: str(i)
                                                                for i in range(
                                                                    5, 101, 10
                                                                )
                                                            },
                                                        ),
                                                        # Search options for BFS/DFS
                                                        html.Div(
                                                            [
                                                                html.Label(
                                                                    "Max Depth (BFS):"
                                                                ),
                                                                dcc.Slider(
                                                                    id="max-depth-slider",
                                                                    min=1,
                                                                    max=5,
                                                                    step=1,
                                                                    value=2,
                                                                    marks={
                                                                        i: str(i)
                                                                        for i in range(
                                                                            1, 6
                                                                        )
                                                                    },
                                                                ),
                                                                html.Label(
                                                                    "Max Breadth (DFS):"
                                                                ),
                                                                dcc.Slider(
                                                                    id="max-breadth-slider",
                                                                    min=1,
                                                                    max=10,
                                                                    step=1,
                                                                    value=5,
                                                                    marks={
                                                                        i: str(i)
                                                                        for i in range(
                                                                            1, 11, 2
                                                                        )
                                                                    },
                                                                ),
                                                            ],
                                                            id="search-options",
                                                            style={"marginTop": "15px"},
                                                        ),
                                                    ],
                                                ),
                                                dcc.Tab(
                                                    label="Search by Track",
                                                    value="track",
                                                    children=[
                                                        # Track selection dropdown with help text
                                                        html.Label("Select a Track:"),
                                                        html.Div(
                                                            [
                                                                html.P(
                                                                    "Type at least 3 characters to search for tracks by name or artist.",
                                                                    style={
                                                                        "fontSize": "0.9em",
                                                                        "color": "#666",
                                                                        "marginBottom": "5px",
                                                                    },
                                                                ),
                                                                html.P(
                                                                    "🎵 This feature finds tracks with similar audio characteristics (tempo, energy, mood) to your selected song.",
                                                                    style={
                                                                        "fontSize": "0.85em",
                                                                        "color": "#007bff",
                                                                        "marginBottom": "10px",
                                                                        "fontStyle": "italic",
                                                                    },
                                                                ),
                                                            ]
                                                        ),
                                                        dcc.Dropdown(
                                                            id="track-selection-dropdown",
                                                            options=all_tracks,  # Show all tracks initially
                                                            value=None,
                                                            placeholder="Type to search for a track...",
                                                            clearable=True,
                                                            searchable=True,
                                                        ),
                                                        # Track info display
                                                        html.Div(
                                                            id="selected-track-info",
                                                            style={
                                                                "marginTop": "10px",
                                                                "fontSize": "0.9em",
                                                            },
                                                        ),
                                                        # Number of recommendations - set default to 50
                                                        html.Label(
                                                            "Number of Recommendations:"
                                                        ),
                                                        dcc.Slider(
                                                            id="num-recommendations-slider",
                                                            min=5,
                                                            max=100,
                                                            step=5,
                                                            value=50,  # Changed to 50
                                                            marks={
                                                                i: str(i)
                                                                for i in range(
                                                                    5, 101, 10
                                                                )
                                                            },
                                                        ),
                                                        html.Div(
                                                            [
                                                                html.P(
                                                                    "This tab helps you find tracks similar to a specific song.",
                                                                    style={
                                                                        "marginTop": "20px",
                                                                        "fontSize": "0.9em",
                                                                        "color": "#666",
                                                                    },
                                                                ),
                                                                html.P(
                                                                    "1. Select a track from the dropdown (or use the 'Similar' button on recommendations)",
                                                                    style={
                                                                        "fontSize": "0.9em",
                                                                        "color": "#666",
                                                                    },
                                                                ),
                                                                html.P(
                                                                    "2. Click 'Search' to find similar tracks",
                                                                    style={
                                                                        "fontSize": "0.9em",
                                                                        "color": "#666",
                                                                    },
                                                                ),
                                                                html.P(
                                                                    "Note: If no recommendations appear, this track may not have enough similar songs in the database.",
                                                                    style={
                                                                        "fontSize": "0.9em",
                                                                        "color": "#bb0000",
                                                                        "fontWeight": "bold",
                                                                    },
                                                                ),
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),
                                        # Search button
                                        html.Button(
                                            "Search",
                                            id="search-button",
                                            className="primary-button",
                                            **{"aria-describedby": "search-status"},
                                            style={
                                                "marginTop": "20px",
                                                "width": "100%",
                                                "padding": "10px",
                                                "backgroundColor": "#4CAF50",
                                                "color": "white",
                                                "border": "none",
                                                "borderRadius": "4px",
                                                "cursor": "pointer",
                                                "fontSize": "16px",
                                                "fontWeight": "bold",
                                            },
                                        ),
                                    ],
                                    className="controls-container",
                                    **{"aria-labelledby": "search-options-heading"},
                                    role="form",
                                ),
                                # Results section with maximum height and scrolling
                                html.Section(
                                    [
                                        html.H3(
                                            "Recommendations",
                                            id="recommendations-heading",
                                        ),
                                        # Status indicator
                                        html.Div(
                                            id="search-status",
                                            style={
                                                "marginBottom": "10px",
                                                "color": "#666",
                                            },
                                        ),
                                        # Recommendation results table with scrolling
                                        html.Div(
                                            id="recommendations-table",
                                            style={
                                                "overflowX": "auto",
                                                "overflowY": "auto",
                                                "maxHeight": "500px",
                                            },
                                        ),
                                    ],
                                    className="results-container",
                                    **{"aria-labelledby": "recommendations-heading"},
                                    role="region",
                                    **{"aria-live": "polite"},
                                ),
                            ],
                        )
                    ],
                    id="main-content",
                    role="main",
                ),
                # Visualization section
                html.Div(
                    [
                        html.H3("Visualization", style={"textAlign": "center"}),
                        # Tabs for different visualizations
                        dcc.Tabs(
                            [
                                # Bubble chart for audio features
                                dcc.Tab(
                                    label="Audio Features",
                                    children=[
                                        html.Div(
                                            [
                                                html.P(
                                                    "This visualization shows the energy and valence of recommended tracks.",
                                                    style={
                                                        "textAlign": "center",
                                                        "marginBottom": "5px",
                                                    },
                                                ),
                                                html.Div(
                                                    [
                                                        html.P(
                                                            "Bubble size represents popularity/similarity and color represents genre.",
                                                            style={
                                                                "textAlign": "center",
                                                                "marginBottom": "5px",
                                                            },
                                                        ),
                                                        html.P(
                                                            "💡 This chart shows the relationship between Valence (happiness) and Energy. Hover over bubbles for track details.",
                                                            style={
                                                                "textAlign": "center",
                                                                "fontSize": "12px",
                                                                "color": "#6c757d",
                                                                "marginBottom": "10px",
                                                            },
                                                        ),
                                                    ]
                                                ),
                                                dcc.Graph(
                                                    id="track-features-bubble-chart",
                                                    style={"height": "600px"},
                                                ),
                                            ]
                                        )
                                    ],
                                ),
                                # Similarity graph visualization
                                dcc.Tab(
                                    label="Similarity Network",
                                    children=[
                                        html.Div(
                                            [
                                                html.P(
                                                    "This visualization shows connections between similar tracks.",
                                                    style={
                                                        "textAlign": "center",
                                                        "marginBottom": "5px",
                                                    },
                                                ),
                                                html.P(
                                                    "🔗 Each node is a track, connected lines show similarity. Larger nodes = more connections. Click nodes to explore.",
                                                    style={
                                                        "textAlign": "center",
                                                        "fontSize": "12px",
                                                        "color": "#6c757d",
                                                        "marginBottom": "10px",
                                                    },
                                                ),
                                            ]
                                        ),
                                        dcc.Graph(
                                            id="similarity-graph",
                                            style={"height": "700px"},
                                        ),
                                    ],
                                ),
                            ]
                        ),
                    ],
                    style={"clear": "both", "padding": "20px"},
                ),
                # Store for selected track ID (for similarity recommendations)
                dcc.Store(id="selected-track-store"),
                # Store for current recommendations
                dcc.Store(id="current-recommendations-store"),
                # Hidden div for page load trigger
                html.Div(id="page-load-trigger", style={"display": "none"}),
            ],
            className="main-container",
        )

        return layout

    def _register_callbacks(self):
        """Register the Dash callbacks for interactive functionality."""

        # Track selection dropdown callback
        @self.app.callback(
            [
                Output("track-selection-dropdown", "options"),
                Output("selected-track-info", "children"),
            ],
            [
                Input("track-selection-dropdown", "search_value"),
                Input("track-selection-dropdown", "value"),
                Input("selected-track-store", "data"),
            ],
        )
        def update_track_dropdown_and_info(
            search_value, selected_track_dropdown, selected_track_store
        ):
            """Filter track dropdown options and display track info."""
            ctx = callback_context
            trigger_id = (
                ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None
            )

            # Handle track dropdown filtering when searching
            if trigger_id == "track-selection-dropdown" and search_value:
                if len(search_value) < 3:
                    # Show a message if search term is too short
                    return dash.no_update, "Type at least 3 characters to search"

                # Use SearchEngine with fuzzy search for better results
                search_results = self.search_engine.search_tracks(search_value)

                # Convert search results to dropdown format
                matched_tracks = []
                for result in search_results:
                    display_name = result["display_name"]
                    track_id = result["track_id"]
                    matched_tracks.append({"label": display_name, "value": track_id})

                # Show default message if no track selected yet
                return matched_tracks, "Select a track and click 'Search'"

            # Show track info when a track is selected
            selected_id = selected_track_dropdown or selected_track_store
            if selected_id:
                track_info = self.recommender.get_track_info(selected_id)
                if track_info:
                    # Get properly decoded names
                    track_name = track_info.get("track_name", selected_id)
                    artist_name = track_info.get("artist_name", "Unknown")
                    genre_path = " > ".join(track_info["genre_path"])
                    moods = ", ".join(track_info["mood_tags"])

                    info_html = [
                        html.Div(
                            [
                                html.Strong("Selected: "),
                                html.Span(f"{track_name} by {artist_name}"),
                            ]
                        ),
                        html.Div([html.Strong("Genre: "), html.Span(genre_path)]),
                        html.Div([html.Strong("Mood Tags: "), html.Span(moods)]),
                    ]

                    return dash.no_update, info_html

            # Default return if no other conditions met
            return dash.no_update, "Select a track and click 'Search'"

        # Set selected track when Similar button is clicked
        @self.app.callback(
            [
                Output("selected-track-store", "data"),
                Output("track-selection-dropdown", "value"),
                Output("search-type-tabs", "value"),
            ],
            [
                Input(
                    {"type": "track-button", "index": dash.dependencies.ALL}, "n_clicks"
                )
            ],
            [State({"type": "track-button", "index": dash.dependencies.ALL}, "id")],
        )
        def track_selection_callback(n_clicks_values, ids_values):
            """Handle 'Similar' button clicks to set the selected track."""
            ctx = callback_context

            # Return no update if not triggered or no clicks
            if not ctx.triggered or not any(n_clicks_values):
                return dash.no_update, dash.no_update, dash.no_update

            # Get the ID of the clicked component
            button_idx = next((i for i, val in enumerate(n_clicks_values) if val), None)
            if button_idx is None:
                return dash.no_update, dash.no_update, dash.no_update

            # Get the track_id from the clicked button
            track_id = ids_values[button_idx]["index"]
            print(f"Similar button clicked for track: {track_id}")

            # Set both track store and dropdown to the same track ID
            # This ensures consistent track selection
            return track_id, track_id, "track"

        # Get recommendations based on search criteria
        @self.app.callback(
            [
                Output("recommendations-table", "children"),
                Output("search-status", "children"),
                Output("current-recommendations-store", "data"),
                Output("loading-indicator", "style"),
                Output("search-button", "disabled"),
            ],
            [
                Input("search-button", "n_clicks"),
                # Add this input to trigger the callback when tab changes
                Input("search-type-tabs", "value"),
            ],
            [
                State("genre-dropdown", "value"),
                State("mood-dropdown", "value"),
                State("search-method", "value"),
                State("max-depth-slider", "value"),
                State("max-breadth-slider", "value"),
                State("track-selection-dropdown", "value"),
                State("selected-track-store", "data"),
                State("num-recommendations-slider", "value"),
                State("results-count-slider", "value"),
            ],
        )
        def update_recommendations(
            n_clicks,
            active_tab,
            genre,
            mood,
            search_method,
            max_depth,
            max_breadth,
            track_dropdown,
            track_store,
            num_recommendations,
            results_count,
        ):
            """Update recommendations based on search criteria."""
            # Initialize variables
            recommendations = []
            status_message = ""
            ctx = callback_context
            trigger_id = (
                ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None
            )

            # Only process if search button was clicked or tab changed after a search
            if n_clicks is None:
                return (
                    html.Div(),
                    "Select search criteria and click 'Search'",
                    [],
                    {"display": "none"},
                    False,
                )

            # Show loading during processing
            # (In production, you might want to handle this differently)
            # Add a small delay to demonstrate loading indicator
            time.sleep(0.5)

            # Determine which tab is active and generate recommendations accordingly
            if active_tab == "track":  # Track selection tab
                # Get the selected track ID (either from dropdown or store)
                selected_track = track_dropdown or track_store

                if not selected_track:
                    return (
                        html.Div("Please select a track first."),
                        "No track selected",
                        [],
                        {"display": "none"},
                        False,
                    )

                # Get track info for the status message
                track_info = self.recommender.get_track_info(selected_track)
                track_name = (
                    track_info.get("track_name", selected_track)
                    if track_info
                    else selected_track
                )

                # Get limit for number of recommendations
                limit = num_recommendations or 50  # Default to 50

                print(
                    f"Getting recommendations similar to track: {selected_track}, limit: {limit}"
                )

                # Get recommendations similar to the selected track
                recommendations = self.recommender.recommend_similar_to_track(
                    track_id=selected_track, limit=limit
                )

                status_message = f"Showing recommendations similar to: {track_name}"

            else:  # Genre/Mood tab
                if not genre:
                    return (
                        html.Div("Please select a genre."),
                        "No genre selected",
                        [],
                        {"display": "none"},
                        False,
                    )

                # Get the number of results to show
                limit = results_count or 50  # Default to 50

                print(
                    f"Genre search: {genre}, mood: {mood}, method: {search_method}, limit: {limit}"
                )

                # Get recommendations based on search method
                if search_method == "bfs":
                    recommendations = self.recommender.bfs_recommend(
                        genre=genre, mood=mood, max_depth=max_depth, limit=limit
                    )
                    method_display = "Breadth-First Search"

                elif search_method == "dfs":
                    recommendations = self.recommender.dfs_recommend(
                        genre=genre, mood=mood, max_breadth=max_breadth, limit=limit
                    )
                    method_display = "Depth-First Search"

                elif mood:
                    # If mood is specified, search by both genre and mood
                    recommendations = self.recommender.recommend_by_genre_and_mood(
                        genre=genre, mood=mood, limit=limit
                    )
                    method_display = "Direct Search"

                else:
                    # Default to genre search
                    recommendations = self.recommender.recommend_by_genre(
                        genre=genre, limit=limit
                    )
                    method_display = "Direct Search"

                status_message = f"Using {method_display} for genre: {genre}"
                if mood:
                    status_message += f", mood: {mood}"
                status_message += f" (showing up to {limit} results)"

            # Check if recommendations were found
            if not recommendations or len(recommendations) == 0:
                no_results_message = "No recommendations found."
                if active_tab == "track":
                    no_results_message += (
                        " This track may not have enough similar songs in the database."
                    )
                else:
                    no_results_message += " Try different search criteria."

                return (
                    html.Div(no_results_message),
                    status_message,
                    [],
                    {"display": "none"},
                    False,
                )

            # Create responsive recommendation cards
            recommendation_cards = []
            for i, rec in enumerate(recommendations):
                # Get properly decoded text fields
                track_display = rec.get("track_name", rec["track_id"])
                artist_name = rec.get("artist_name", "Unknown")
                genre_path = " > ".join(rec["genre_path"])
                mood_tags = ", ".join(rec["mood_tags"])

                # Create streaming link for the track
                # Using the track name and artist to search
                search_query = f"{track_display} {artist_name}"
                encoded_query = search_query.replace(" ", "+")
                streaming_url = f"https://music.youtube.com/search?q={encoded_query}"

                # Generate explanation for this recommendation
                explanation = generate_explanation(
                    rec,
                    "similarity" if active_tab == "track" else "genre_mood",
                    similarity_score=rec.get("similarity_score"),
                    source_track=rec.get("source_track"),
                )

                # Create responsive recommendation card
                card = html.Div(
                    [
                        # Track title and artist
                        html.Div(
                            [
                                html.A(
                                    track_display,
                                    href=streaming_url,
                                    target="_blank",
                                    className="recommendation-title",
                                    style={
                                        "color": "#1DB954",
                                        "textDecoration": "none",
                                    },
                                    title=f"Listen to {track_display} on YouTube Music",
                                    tabIndex="0",
                                ),
                                html.Div(
                                    f"by {artist_name}",
                                    className="recommendation-details",
                                ),
                            ],
                            style={"marginBottom": "10px"},
                        ),
                        # Audio features and genre info
                        html.Div(
                            [
                                html.Span(
                                    f"Genre: {genre_path}",
                                    style={"marginRight": "15px"},
                                ),
                                html.Span(
                                    f"Moods: {mood_tags}" if mood_tags else "",
                                    style={"marginRight": "15px"},
                                ),
                                html.Span(
                                    f"Energy: {rec.get('energy', 'N/A'):.2f}"
                                    if "energy" in rec
                                    else ""
                                ),
                                html.Span(
                                    f" | Valence: {rec.get('valence', 'N/A'):.2f}"
                                    if "valence" in rec
                                    else ""
                                ),
                            ],
                            className="recommendation-details",
                            style={"marginBottom": "10px"},
                        ),
                        # Explanation text
                        html.Div(
                            explanation,
                            className="recommendation-explanation",
                            **{
                                "aria-label": f"Why this track was recommended: {explanation}"
                            },
                        ),
                        # Action button
                        html.Div(
                            [
                                html.Button(
                                    "Find Similar",
                                    id={
                                        "type": "track-button",
                                        "index": rec["track_id"],
                                    },
                                    className="secondary-button",
                                    title="Find tracks similar to this one",
                                    **{
                                        "aria-label": f"Find tracks similar to {track_display}"
                                    },
                                    style={
                                        "backgroundColor": "#2196F3",
                                        "color": "white",
                                        "border": "none",
                                        "padding": "8px 16px",
                                        "borderRadius": "4px",
                                        "cursor": "pointer",
                                        "fontSize": "14px",
                                    },
                                )
                            ],
                            style={"textAlign": "right", "marginTop": "10px"},
                        ),
                    ],
                    className="recommendation-item",
                    tabIndex="0",
                    id=f"recommendation-{i}",
                    role="option",
                    **{
                        "aria-label": f"Recommendation {i + 1}: {track_display} by {artist_name}",
                        "aria-selected": "false",
                        "aria-posinset": str(i + 1),
                        "aria-setsize": str(len(recommendations)),
                    },
                )

                recommendation_cards.append(card)

            # Create container for recommendation cards
            recommendations_container = html.Div(
                recommendation_cards,
                className="recommendations-container",
                id="recommendations-list",
                role="listbox",
                **{
                    "aria-label": f"List of {len(recommendations)} recommendations",
                    "aria-multiselectable": "false",
                    "aria-activedescendant": (
                        "recommendation-0" if recommendations else ""
                    ),
                },
            )

            return (
                recommendations_container,
                status_message,
                recommendations,
                {"display": "none"},
                False,
            )

        # Metrics panel callback
        @self.app.callback(
            [
                Output("metrics-panel", "children"),
                Output("metrics-panel", "style"),
            ],
            [Input("current-recommendations-store", "data")],
        )
        def update_metrics_panel(recommendations):
            """Update the metrics panel with current metrics."""
            metrics = metrics_collector.get_metrics()

            if not metrics["total_requests"]:
                return html.Div(), {"display": "none"}

            metrics_content = html.Div(
                [
                    html.H4("Usage Metrics"),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        str(metrics["total_requests"]),
                                        className="metric-value",
                                    ),
                                    html.Div(
                                        "Total Requests", className="metric-label"
                                    ),
                                ],
                                className="metric-item",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        f"{metrics['success_rate_percent']:.1f}%",
                                        className="metric-value",
                                    ),
                                    html.Div("Success Rate", className="metric-label"),
                                ],
                                className="metric-item",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        f"{metrics['average_latency_ms']:.1f}ms",
                                        className="metric-value",
                                    ),
                                    html.Div("Avg Latency", className="metric-label"),
                                ],
                                className="metric-item",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        str(
                                            len(recommendations)
                                            if recommendations
                                            else 0
                                        ),
                                        className="metric-value",
                                    ),
                                    html.Div("Results Found", className="metric-label"),
                                ],
                                className="metric-item",
                            ),
                        ],
                        className="metrics-grid",
                    ),
                ]
            )

            return metrics_content, {"display": "block"}

        # Focus management callback (clientside for performance)
        self.app.clientside_callback(
            """
            function(recommendations_data) {
                return window.dash_clientside.keyboard.focusFirstRecommendation(recommendations_data);
            }
            """,
            Output("recommendations-list", "data-focus-trigger"),
            [Input("current-recommendations-store", "data")],
        )

        # Keyboard navigation initialization callback
        self.app.clientside_callback(
            """
            function(n_clicks, current_recommendations) {
                return window.dash_clientside.keyboard.handleKeyboardNavigation(n_clicks, current_recommendations);
            }
            """,
            Output("recommendations-list", "data-keyboard-init"),
            [
                Input("search-button", "n_clicks"),
                Input("current-recommendations-store", "data"),
            ],
        )

        # Update bubble chart visualization
        @self.app.callback(
            Output("track-features-bubble-chart", "figure"),
            [Input("current-recommendations-store", "data")],
        )
        def update_features_bubble_chart(recommendations):
            """Create a bubble chart visualization of track audio features."""
            # If there are no recommendations, return an empty chart
            if not recommendations or len(recommendations) == 0:
                fig = go.Figure()
                fig.update_layout(
                    title="No data to display",
                    annotations=[
                        dict(
                            text="Search for recommendations to see track audio features",
                            showarrow=False,
                            xref="paper",
                            yref="paper",
                            x=0.5,
                            y=0.5,
                        )
                    ],
                    xaxis=dict(title="Valence (Positivity)"),
                    yaxis=dict(title="Energy"),
                    height=600,
                )
                return fig

            # Process the recommendations data for visualization
            track_data = []

            try:
                for rec in recommendations:
                    # Skip tracks without energy or valence values
                    if "energy" not in rec or "valence" not in rec:
                        continue

                    # Extract the primary genre
                    genre = rec["genre_path"][0] if rec["genre_path"] else "unknown"

                    # Calculate popularity
                    popularity = (
                        rec.get("similarity", 0.7) * 100 if "similarity" in rec else 75
                    )

                    # Get proper text values
                    track_name = rec.get("track_name", rec["track_id"])
                    artist_name = rec.get("artist_name", "Unknown")
                    mood_tags = ", ".join(rec["mood_tags"])

                    track_data.append(
                        {
                            "track_name": track_name,
                            "artist_name": artist_name,
                            "genre": genre,
                            "energy": rec["energy"],
                            "valence": rec["valence"],
                            "mood_tags": mood_tags,
                            "popularity": popularity,
                        }
                    )

            except Exception as e:
                print(f"Error processing track data: {e}")
                # Return a basic error message
                fig = go.Figure()
                fig.update_layout(
                    title="Error processing data",
                    annotations=[
                        dict(
                            text=f"Error: {str(e)}",
                            showarrow=False,
                            xref="paper",
                            yref="paper",
                            x=0.5,
                            y=0.5,
                        )
                    ],
                    xaxis=dict(title="Valence (Positivity)"),
                    yaxis=dict(title="Energy"),
                    height=600,
                )
                return fig

            # Create DataFrame for plotting
            df = pd.DataFrame(track_data)

            if df.empty:
                # Return empty chart
                fig = go.Figure()
                fig.update_layout(
                    title="No audio feature data available",
                    annotations=[
                        dict(
                            text="Try different search criteria to see track audio features",
                            showarrow=False,
                            xref="paper",
                            yref="paper",
                            x=0.5,
                            y=0.5,
                        )
                    ],
                    xaxis=dict(title="Valence (Positivity)"),
                    yaxis=dict(title="Energy"),
                    height=600,
                )
                return fig

            # Create bubble chart
            fig = px.scatter(
                df,
                x="valence",
                y="energy",
                size="popularity",
                color="genre",
                hover_name="track_name",
                hover_data={
                    "artist_name": True,
                    "mood_tags": True,
                    "genre": True,
                    "energy": ":.2f",
                    "valence": ":.2f",
                    "popularity": False,
                },
                size_max=50,
                opacity=0.7,
            )

            # Update layout
            fig.update_layout(
                title="Audio Features: Energy vs. Valence",
                xaxis=dict(
                    title="Valence (Positivity)", range=[0, 1], gridcolor="lightgray"
                ),
                yaxis=dict(title="Energy", range=[0, 1], gridcolor="lightgray"),
                height=600,
                legend_title="Genre",
                plot_bgcolor="rgba(240, 245, 250, 0.95)",
                margin=dict(l=40, r=40, t=50, b=40),
            )

            # Add quadrant labels and reference lines
            fig.add_shape(
                type="line",
                x0=0.5,
                y0=0,
                x1=0.5,
                y1=1,
                line=dict(color="gray", width=1, dash="dash"),
            )

            fig.add_shape(
                type="line",
                x0=0,
                y0=0.5,
                x1=1,
                y1=0.5,
                line=dict(color="gray", width=1, dash="dash"),
            )

            fig.add_annotation(
                text="Chill/Relaxed",
                xref="x",
                yref="y",
                x=0.25,
                y=0.25,
                showarrow=False,
                font=dict(size=10, color="gray"),
            )

            fig.add_annotation(
                text="Happy/Energetic",
                xref="x",
                yref="y",
                x=0.75,
                y=0.75,
                showarrow=False,
                font=dict(size=10, color="gray"),
            )

            fig.add_annotation(
                text="Sad/Depressive",
                xref="x",
                yref="y",
                x=0.25,
                y=0.75,
                showarrow=False,
                font=dict(size=10, color="gray"),
            )

            fig.add_annotation(
                text="Peaceful/Positive",
                xref="x",
                yref="y",
                x=0.75,
                y=0.25,
                showarrow=False,
                font=dict(size=10, color="gray"),
            )

            return fig

        # Update similarity graph visualization
        @self.app.callback(
            Output("similarity-graph", "figure"),
            [Input("current-recommendations-store", "data")],
            [
                State("search-type-tabs", "value"),
                State("genre-dropdown", "value"),
                State("mood-dropdown", "value"),
                State("track-selection-dropdown", "value"),
                State("selected-track-store", "data"),
            ],
        )
        def update_similarity_graph(
            recommendations,
            active_tab,
            selected_genre,
            mood,
            selected_track_dropdown,
            selected_track_store,
        ):
            """Create a network visualization of track similarities."""
            if not recommendations or len(recommendations) == 0:
                # Create a basic figure with instructions
                fig = go.Figure()
                fig.update_layout(
                    title="Click 'Search' to see the similarity network",
                    annotations=[
                        dict(
                            text="This visualization shows connections between similar tracks",
                            showarrow=False,
                            xref="paper",
                            yref="paper",
                            x=0.5,
                            y=0.5,
                        )
                    ],
                )
                return fig

            # Extract track IDs from recommendations
            track_ids = [rec["track_id"] for rec in recommendations]

            # Create dictionary mapping track_ids to display names with proper decoding
            track_names = {}
            for rec in recommendations:
                track_names[rec["track_id"]] = rec.get("track_name", rec["track_id"])

            # Get the similarity graph as a subgraph
            subgraph = self.recommender.similarity_graph.graph.subgraph(track_ids)

            # Use networkx spring layout for node positions
            pos = nx.spring_layout(subgraph, seed=42)

            # Create edge trace
            edge_x = []
            edge_y = []
            edge_widths = []

            for u, v, data in subgraph.edges(data=True):
                x0, y0 = pos[u]
                x1, y1 = pos[v]

                # Add edge coordinates
                edge_x.append(x0)
                edge_x.append(x1)
                edge_x.append(None)
                edge_y.append(y0)
                edge_y.append(y1)
                edge_y.append(None)

                # Store edge width based on weight
                weight = data.get("weight", 0.5)
                edge_widths.append(weight * 2)

            # Create edge trace
            edge_trace = go.Scatter(
                x=edge_x,
                y=edge_y,
                line=dict(width=2.5, color="#888"),
                hoverinfo="none",
                mode="lines",
            )

            # Create node trace
            node_x = []
            node_y = []
            node_text = []
            node_size = []
            node_color = []
            hover_text = []

            # Define genre colors mapping
            genre_colors = {
                "rock": 0,
                "metal": 0.2,
                "electronic": 0.4,
                "hip-hop": 0.6,
                "acoustic": 0.8,
                "jazz": 1.0,
            }

            for node_id in subgraph.nodes():
                x, y = pos[node_id]
                node_x.append(x)
                node_y.append(y)

                # Get track info
                track_info = self.recommender.get_track_info(node_id)

                # Use track name if available
                track_name = track_names.get(node_id, node_id)

                # Create hover text with properly decoded values
                hover = f"Track: {track_name}<br>"
                if track_info:
                    artist_name = track_info.get("artist_name", "Unknown")
                    genre_path = " > ".join(track_info["genre_path"])
                    mood_tags = ", ".join(track_info["mood_tags"])

                    hover += f"Artist: {artist_name}<br>"
                    hover += f"Genre: {genre_path}<br>"
                    hover += f"Mood: {mood_tags}<br>"
                    if "energy" in track_info:
                        hover += f"Energy: {track_info['energy']:.2f}<br>"
                    if "valence" in track_info:
                        hover += f"Valence: {track_info['valence']:.2f}"

                hover_text.append(hover)

                # Node size based on degree centrality
                degree = len(list(subgraph.neighbors(node_id)))
                node_size.append(20 + degree * 5)

                # Node color based on genre
                color_value = 0  # Default
                if track_info and track_info["genre_path"]:
                    # Map genres to colors
                    for g in track_info["genre_path"]:
                        if g in genre_colors:
                            color_value = genre_colors[g]
                            break

                node_color.append(color_value)

                # Save track name for display
                node_text.append(track_name)

            # Create node trace
            node_trace = go.Scatter(
                x=node_x,
                y=node_y,
                mode="markers+text",
                hoverinfo="text",
                text=node_text,
                textposition="top center",
                hovertext=hover_text,
                marker=dict(
                    showscale=True,
                    colorscale="Viridis",
                    size=node_size,
                    color=node_color,
                    line=dict(width=2, color="#333"),
                    colorbar=dict(
                        title="Genre",
                        thickness=15,
                        tickvals=list(genre_colors.values()),
                        ticktext=list(genre_colors.keys()),
                    ),
                ),
            )

            # Determine the title based on search method
            if active_tab == "track":
                track_id = selected_track_dropdown or selected_track_store
                if track_id:
                    track_info = self.recommender.get_track_info(track_id)
                    if track_info:
                        track_name = track_info.get("track_name", track_id)
                        title_text = f"Similarity Network for '{track_name}'"
                    else:
                        title_text = "Similarity Network for Selected Track"
                else:
                    title_text = "Similarity Network for Recommendations"
            else:
                if selected_genre:
                    title_text = f"Similarity Network for '{selected_genre}' Tracks"
                    if mood:
                        title_text += f" with '{mood}' Mood"
                else:
                    title_text = "Similarity Network for Recommendations"

            # Create the figure with both traces
            fig = go.Figure(data=[edge_trace, node_trace])

            # Update layout settings
            fig.update_layout(
                title=title_text,
                showlegend=False,
                hovermode="closest",
                margin=dict(b=20, l=5, r=5, t=40),
                height=700,
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor="rgba(240, 245, 250, 0.95)",
            )

            return fig

        # This callback triggers search when Similar button is clicked and tab changes
        @self.app.callback(
            Output("search-button", "n_clicks"),
            [
                Input("selected-track-store", "data"),
                Input("track-selection-dropdown", "value"),
            ],
            prevent_initial_call=True,
        )
        def auto_search_on_track_selection(selected_track, dropdown_track):
            """Trigger a search when a track is selected."""
            # Get the context to determine which input triggered this
            ctx = callback_context
            if not ctx.triggered:
                return dash.no_update

            trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

            # Only trigger search if selection changed via Similar button
            if trigger_id == "selected-track-store" and selected_track:
                print(
                    f"Auto-searching for track: {selected_track} (from Similar button)"
                )
                return 1  # Trigger one click

            return dash.no_update

    def _add_metrics_endpoint(self):
        """Add metrics and health endpoints to the Flask server."""

        @self.app.server.route("/metrics")
        def get_metrics():
            """Return current metrics as JSON."""
            import json

            from flask import Response

            metrics = metrics_collector.get_metrics()
            return Response(
                json.dumps(metrics, indent=2),
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"},
            )

        @self.app.server.route("/health")
        def health_check():
            """Health check endpoint for deployment platforms."""
            import json

            from flask import Response

            health_status = {
                "status": "healthy",
                "version": "2.0.0",
                "service": "mood-music-recommender",
                "timestamp": str(datetime.now()),
                "checks": {
                    "database": "ok",
                    "search_engine": (
                        "ok" if hasattr(self, "search_engine") else "not_initialized"
                    ),
                    "recommender": (
                        "ok"
                        if hasattr(self, "music_recommender")
                        else "not_initialized"
                    ),
                },
            }

            return Response(
                json.dumps(health_status, indent=2),
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"},
                status=200,
            )

    def run_server(self, debug=False, port=8040, host="127.0.0.1"):
        """Run the Dash server.

        Args:
            debug: Whether to run in debug mode
            port: The port to run on
            host: The host to run on
        """
        # Use the newer app.run() method instead of app.run_server()
        self.app.run(debug=debug, port=port, host=host)


if __name__ == "__main__":
    import doctest

    doctest.testmod()

    python_ta.check_all(
        config={
            "extra-imports": [
                "dash",
                "dash.dependencies",
                "plotly.graph_objects",
                "plotly.express",
                "pandas",
                "networkx",
                "html",
            ],
            "allowed-io": [
                "update_similarity_graph",
                "update_track_dropdown_and_info",
                "update_recommendations",
                "update_features_bubble_chart",
                "track_selection_callback",
                "auto_search_on_track_selection",
            ],
            "max-line-length": 120,
            "disable": ["E1136"],
        }
    )
