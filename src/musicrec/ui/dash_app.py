"""CSC111 Winter 2025: A Mood-Driven Music Recommender with Genre Hierarchies

Module for creating the visualization interface of the music recommender system.
This module builds a Dash application for interactive music recommendations.

Copyright and Usage Information
===============================
This file is Copyright (c) 2025 Qian (Angela) Su & Mengxuan (Connie) Guo.
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import networkx as nx
import logging
from ..metrics.collector import metrics_collector

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
        self.app = dash.Dash(__name__, suppress_callback_exceptions=True)

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
                html.H1(
                    "Mood-Driven Music Recommender with Genre Hierarchies",
                    style={"textAlign": "center", "marginBottom": "30px"},
                ),
                # Controls section
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3("Search Options"),
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
                                                        {"label": genre, "value": genre}
                                                        for genre in genres
                                                    ],
                                                    value=genres[0] if genres else None,
                                                    clearable=False,
                                                ),
                                                # Mood selection
                                                html.Label("Select Mood (Optional):"),
                                                dcc.Dropdown(
                                                    id="mood-dropdown",
                                                    options=[
                                                        {"label": mood, "value": mood}
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
                                                    labelStyle={"display": "block"},
                                                ),
                                                # Number of results to show - set default to 50
                                                html.Label("Number of Results:"),
                                                dcc.Slider(
                                                    id="results-count-slider",
                                                    min=5,
                                                    max=100,
                                                    step=5,
                                                    value=50,  # Changed to 50
                                                    marks={
                                                        i: str(i)
                                                        for i in range(5, 101, 10)
                                                    },
                                                ),
                                                # Search options for BFS/DFS
                                                html.Div(
                                                    [
                                                        html.Label("Max Depth (BFS):"),
                                                        dcc.Slider(
                                                            id="max-depth-slider",
                                                            min=1,
                                                            max=5,
                                                            step=1,
                                                            value=2,
                                                            marks={
                                                                i: str(i)
                                                                for i in range(1, 6)
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
                                                                for i in range(1, 11, 2)
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
                                                        )
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
                                                        for i in range(5, 101, 10)
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
                            style={"width": "30%", "float": "left", "padding": "20px"},
                        ),
                        # Results section with maximum height and scrolling
                        html.Div(
                            [
                                html.H3("Recommendations"),
                                # Status indicator
                                html.Div(
                                    id="search-status",
                                    style={"marginBottom": "10px", "color": "#666"},
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
                            style={"width": "65%", "float": "right", "padding": "20px"},
                        ),
                    ],
                    style={"display": "flex", "flexWrap": "wrap"},
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
                                                html.P(
                                                    "Bubble size represents popularity/similarity and color represents genre.",
                                                    style={
                                                        "textAlign": "center",
                                                        "marginBottom": "10px",
                                                    },
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
                                        html.P(
                                            "This visualization shows connections between similar tracks.",
                                            style={
                                                "textAlign": "center",
                                                "marginBottom": "10px",
                                            },
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
            ]
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

                # Search for matching tracks
                matched_tracks = []
                for track_id, node in self.recommender.genre_tree.tracks.items():
                    track_name = node.data.get("track_name", "")
                    artist_name = node.data.get("artist_name", "")

                    # Convert to lowercase for case-insensitive search
                    if (
                        search_value.lower() in track_name.lower()
                        or search_value.lower() in artist_name.lower()
                    ):
                        # Create properly decoded display name
                        display_name = f"{track_name} - {artist_name}"
                        matched_tracks.append(
                            {"label": display_name, "value": track_id}
                        )

                        # Limit to 100 matches for performance
                        if len(matched_tracks) >= 100:
                            break

                # Sort matches alphabetically
                matched_tracks.sort(key=lambda x: x["label"].lower())

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
                return html.Div(), "Select search criteria and click 'Search'", []

            # Determine which tab is active and generate recommendations accordingly
            if active_tab == "track":  # Track selection tab
                # Get the selected track ID (either from dropdown or store)
                selected_track = track_dropdown or track_store

                if not selected_track:
                    return (
                        html.Div("Please select a track first."),
                        "No track selected",
                        [],
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
                    return html.Div("Please select a genre."), "No genre selected", []

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

                return html.Div(no_results_message), status_message, []

            # Create the recommendation table
            table_header = [
                html.Thead(
                    html.Tr(
                        [
                            html.Th("Track Name"),
                            html.Th("Artist"),
                            html.Th("Genre Path"),
                            html.Th("Moods"),
                            html.Th("Energy"),
                            html.Th("Valence"),
                            html.Th("Actions"),
                        ]
                    )
                )
            ]

            table_rows = []
            for rec in recommendations:
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

                # Create clickable track name with link to streaming service
                track_link = html.A(
                    track_display,
                    href=streaming_url,
                    target="_blank",
                    title=f"Listen to {track_display} on YouTube Music",
                    style={"color": "#0066cc", "textDecoration": "none"},
                )

                row = html.Tr(
                    [
                        html.Td(track_link),  # Clickable link instead of plain text
                        html.Td(artist_name),
                        html.Td(genre_path),
                        html.Td(mood_tags),
                        html.Td(
                            f"{rec.get('energy', 'N/A'):.2f}"
                            if "energy" in rec
                            else "N/A"
                        ),
                        html.Td(
                            f"{rec.get('valence', 'N/A'):.2f}"
                            if "valence" in rec
                            else "N/A"
                        ),
                        html.Td(
                            html.Button(
                                "Similar",
                                id={"type": "track-button", "index": rec["track_id"]},
                                title="Find tracks similar to this one",
                                style={
                                    "backgroundColor": "#2196F3",
                                    "color": "white",
                                    "border": "none",
                                    "padding": "5px 10px",
                                    "borderRadius": "4px",
                                    "cursor": "pointer",
                                },
                            )
                        ),
                    ]
                )
                table_rows.append(row)

            table_body = [html.Tbody(table_rows)]

            # Apply styling to the table
            table = html.Table(
                table_header + table_body,
                style={
                    "width": "100%",
                    "borderCollapse": "collapse",
                    "border": "1px solid #ddd",
                },
                className="recommendation-table",
            )

            return table, status_message, recommendations

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
        """Add metrics endpoint to the Flask server."""

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

    def run_server(self, debug=False, port=8040):
        """Run the Dash server.

        Args:
            debug: Whether to run in debug mode
            port: The port to run on
        """
        # Use the newer app.run() method instead of app.run_server()
        self.app.run(debug=debug, port=port)


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
