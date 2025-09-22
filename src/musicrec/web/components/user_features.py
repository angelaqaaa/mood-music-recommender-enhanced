"""User-facing interactive features for the music recommender.

This module provides practical features that users can interact with:
- Favorites/bookmarking system
- Playlist generator
- Music discovery dashboard
- User preferences management
"""

import dash
import plotly.graph_objects as go
from dash import ALL, Input, Output, State, callback_context, dcc, html
from dash.exceptions import PreventUpdate


class UserFeaturesManager:
    """Manages user-facing interactive features."""

    def __init__(self, app, recommender):
        """Initialize user features manager.

        Args:
            app: Dash app instance
            recommender: Music recommender engine
        """
        self.app = app
        self.recommender = recommender
        self.register_callbacks()

    def create_favorites_section(self):
        """Create the favorites/bookmarking section."""
        return html.Div(
            [
                html.H3("❤️ Your Music Library", className="section-title"),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H4("⭐ Favorites", className="subsection-title"),
                                html.Div(
                                    id="favorites-list", className="favorites-container"
                                ),
                                html.P(
                                    "Click the ❤️ button on any track to add it to favorites!",
                                    className="help-text",
                                ),
                            ],
                            className="favorites-section",
                        ),
                    ],
                    className="user-library-grid",
                ),
                # Hidden stores for user data
                dcc.Store(id="user-favorites", data=[]),
                dcc.Store(id="user-playlists", data={}),
            ],
            className="user-features-section",
        )

    def create_discovery_dashboard(self):
        """Create music discovery dashboard with user statistics."""
        return html.Div(
            [
                html.H3("🎯 Discovery Dashboard", className="section-title"),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H4("📊 Your Music Stats", className="stats-title"),
                                html.Div(id="user-stats", className="stats-container"),
                            ],
                            className="stats-section",
                        ),
                        html.Div(
                            [
                                html.H4(
                                    "🔍 Genre Explorer", className="explorer-title"
                                ),
                                html.P(
                                    "Discover new genres based on your preferences:",
                                    className="explorer-description",
                                ),
                                html.Button(
                                    "🎲 Explore Random Genre",
                                    id="explore-genre-btn",
                                    className="explore-btn",
                                ),
                                html.Div(
                                    id="genre-exploration",
                                    className="exploration-results",
                                ),
                            ],
                            className="explorer-section",
                        ),
                        html.Div(
                            [
                                html.H4("🎵 Mood Journey", className="mood-title"),
                                html.P(
                                    "Track your musical mood journey:",
                                    className="mood-description",
                                ),
                                dcc.Graph(
                                    id="mood-journey-chart", className="mood-chart"
                                ),
                            ],
                            className="mood-section",
                        ),
                    ],
                    className="dashboard-grid",
                ),
            ],
            className="discovery-dashboard",
        )

    def register_callbacks(self):
        """Register all callbacks for user features."""

        # Favorites management callback
        @self.app.callback(
            [Output("user-favorites", "data"), Output("favorites-list", "children")],
            [Input({"type": "favorite-btn", "index": dash.ALL}, "n_clicks")],
            [
                State("user-favorites", "data"),
                State("current-recommendations-store", "data"),
            ],
            prevent_initial_call=True,
        )
        def manage_favorites(favorite_clicks, current_favorites, recommendations):
            """Add/remove tracks from favorites."""
            if not any(favorite_clicks) or not recommendations:
                raise PreventUpdate

            ctx = callback_context
            if not ctx.triggered:
                raise PreventUpdate

            # Get which favorite button was clicked
            button_id = ctx.triggered[0]["prop_id"]
            track_index = int(button_id.split('"index":')[1].split(",")[0])

            if track_index < len(recommendations):
                track = recommendations[track_index]
                track_id = track.get("track_id", "")

                # Toggle favorite status
                if track_id in current_favorites:
                    current_favorites.remove(track_id)
                else:
                    current_favorites.append(track_id)

            # Generate favorites list display
            favorites_display = self._generate_favorites_display(current_favorites)

            return current_favorites, favorites_display

        # Playlist creation callback
        @self.app.callback(
            [
                Output("user-playlists", "data"),
                Output("playlists-list", "children"),
                Output("new-playlist-name", "value"),
            ],
            [Input("create-playlist-btn", "n_clicks")],
            [State("new-playlist-name", "value"), State("user-playlists", "data")],
            prevent_initial_call=True,
        )
        def create_playlist(n_clicks, playlist_name, current_playlists):
            """Create a new playlist."""
            if not n_clicks or not playlist_name:
                raise PreventUpdate

            # Initialize playlists if not exists
            if not current_playlists:
                current_playlists = {}

            # Add new playlist
            current_playlists[playlist_name] = []

            # Create simple playlist display
            playlist_items = []
            for playlist_name_key, tracks in current_playlists.items():
                playlist_items.append(
                    html.Div(
                        [
                            html.H4(playlist_name_key, className="playlist-name"),
                            html.P(f"{len(tracks)} tracks", className="playlist-count"),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.P(
                                                f"{track['track_name']} - {track['artist_name']}",
                                                className="track-item",
                                                style={"flex": "1"},
                                            ),
                                            html.Button(
                                                "🗑️",
                                                id={
                                                    "type": "remove-track-btn",
                                                    "index": f"{playlist_name}:{track.get('track_id', i)}",
                                                },
                                                className="remove-track-btn",
                                                title="Remove from playlist",
                                                style={
                                                    "background": "#ff4757",
                                                    "color": "white",
                                                    "border": "none",
                                                    "borderRadius": "4px",
                                                    "padding": "4px 8px",
                                                    "cursor": "pointer",
                                                },
                                            ),
                                        ],
                                        style={
                                            "display": "flex",
                                            "alignItems": "center",
                                            "gap": "8px",
                                            "marginBottom": "4px",
                                        },
                                    )
                                    for i, track in enumerate(tracks)
                                ]
                            ),
                        ],
                        className="playlist-item",
                    )
                )

            return current_playlists, playlist_items, ""

        # User statistics callback
        @self.app.callback(
            Output("user-stats", "children"),
            [Input("user-favorites", "data"), Input("user-playlists", "data")],
            prevent_initial_call=True,
        )
        def update_user_stats(favorites, playlists):
            """Update user statistics display."""
            total_favorites = len(favorites)
            total_playlist_tracks = sum(
                len(p) if isinstance(p, list) else len(p.get("tracks", []))
                for p in playlists.values()
            )

            # Calculate favorite genres
            favorite_genres = {}
            for track_id in favorites:
                track_info = self.recommender.get_track_info(track_id)
                if track_info:
                    genre = track_info.get("primary_genre", "Unknown")
                    favorite_genres[genre] = favorite_genres.get(genre, 0) + 1

            top_genre = (
                max(favorite_genres.keys(), key=favorite_genres.get)
                if favorite_genres
                else "None"
            )

            return html.Div(
                [
                    html.Div(
                        [
                            html.H3(str(total_favorites), className="stat-number"),
                            html.P("Favorite Tracks", className="stat-label"),
                        ],
                        className="stat-card",
                    ),
                    html.Div(
                        [
                            html.H3(
                                str(total_playlist_tracks), className="stat-number"
                            ),
                            html.P("Playlist Tracks", className="stat-label"),
                        ],
                        className="stat-card",
                    ),
                    html.Div(
                        [
                            html.H3(top_genre, className="stat-number genre-stat"),
                            html.P("Top Genre", className="stat-label"),
                        ],
                        className="stat-card",
                    ),
                ]
            )

        # Genre exploration callback
        @self.app.callback(
            Output("genre-exploration", "children"),
            [Input("explore-genre-btn", "n_clicks")],
            prevent_initial_call=True,
        )
        def explore_random_genre(n_clicks):
            """Explore a random genre and show recommendations."""
            if not n_clicks:
                raise PreventUpdate

            import random

            genres = self.recommender.get_available_genres()
            random_genre = random.choice(genres) if genres else "pop"

            # Get recommendations for the random genre
            recommendations = self.recommender.recommend_by_genre(random_genre, limit=5)

            if not recommendations:
                return html.Div(
                    "No tracks found for this genre.", className="no-results"
                )

            return html.Div(
                [
                    html.H5(
                        f"🎵 Exploring: {random_genre.title()}",
                        className="exploration-title",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.P(
                                        f"🎵 {track.get('track_name', track.get('track_id', 'Unknown Track'))}",
                                        className="track-name",
                                    ),
                                    html.P(
                                        f"👤 {track.get('artist_name', 'Unknown Artist')}",
                                        className="artist-name",
                                    ),
                                    html.Button("▶️", className="mini-play-btn"),
                                ],
                                className="mini-track-card",
                            )
                            for track in recommendations
                        ]
                    ),
                ]
            )

        # Mood journey chart callback
        @self.app.callback(
            Output("mood-journey-chart", "figure"),
            [Input("user-favorites", "data"), Input("app-theme", "data-theme")],
            prevent_initial_call=True,
        )
        def update_mood_journey(favorites, theme):
            """Create a mood journey chart based on user's favorites."""

            # Get theme colors
            def get_theme_colors(theme):
                """Get color scheme based on theme."""
                if theme == "dark":
                    return {
                        "plot_bgcolor": "rgba(107, 114, 128, 0.6)",
                        "paper_bgcolor": "rgba(55, 65, 81, 0.8)",
                        "font_color": "#F9FAFB",
                        "grid_color": "rgba(156, 163, 175, 0.3)",
                        "line_color": "rgba(156, 163, 175, 0.5)",
                        "annotation_color": "#F9FAFB",
                        "title_color": "#F9FAFB",
                        "axis_color": "#F9FAFB",
                        "tick_color": "#F9FAFB",
                    }
                else:
                    return {
                        "plot_bgcolor": "rgba(219, 234, 254, 0.8)",
                        "paper_bgcolor": "#FFFFFF",
                        "font_color": "#1F2937",
                        "grid_color": "rgba(55, 65, 81, 0.3)",
                        "line_color": "rgba(55, 65, 81, 0.5)",
                        "annotation_color": "#1F2937",
                        "title_color": "#1F2937",
                        "axis_color": "#1F2937",
                        "tick_color": "#1F2937",
                    }

            colors = get_theme_colors(theme)

            if not favorites:
                fig = go.Figure()
                fig.add_annotation(
                    text="Add some favorite tracks to see your mood journey!",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(color=colors["font_color"]),
                )
                fig.update_layout(
                    plot_bgcolor=colors["plot_bgcolor"],
                    paper_bgcolor=colors["paper_bgcolor"],
                    font=dict(color=colors["font_color"]),
                    height=300,
                )
                return fig

            # Analyze mood distribution of favorites
            moods_data = {"happy": 0, "sad": 0, "energetic": 0, "calm": 0, "angry": 0}

            for track_id in favorites:
                track_info = self.recommender.get_track_info(track_id)
                if track_info:
                    # Use valence and energy to determine mood
                    valence = track_info.get("valence", 0.5)
                    energy = track_info.get("energy", 0.5)

                    if valence > 0.6 and energy > 0.6:
                        moods_data["happy"] += 1
                    elif valence < 0.4 and energy < 0.4:
                        moods_data["sad"] += 1
                    elif energy > 0.7:
                        moods_data["energetic"] += 1
                    elif energy < 0.3:
                        moods_data["calm"] += 1
                    else:
                        moods_data["happy"] += 1  # Default

            # Create polar chart with theme-appropriate colors
            if theme == "dark":
                line_color = "#FF6B6B"  # Bright red for dark mode
                fill_color = "rgba(255, 107, 107, 0.3)"  # Semi-transparent red
            else:
                line_color = "#8B5CF6"  # Purple for light mode
                fill_color = "rgba(139, 92, 246, 0.3)"  # Semi-transparent purple

            fig = go.Figure(
                go.Scatterpolar(
                    r=list(moods_data.values()),
                    theta=list(moods_data.keys()),
                    fill="toself",
                    name="Your Music Mood",
                    line=dict(color=line_color, width=3),
                    fillcolor=fill_color,
                    mode="lines+markers",
                    marker=dict(size=8, color=line_color),
                )
            )

            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, max(moods_data.values()) + 1],
                        gridcolor=colors["grid_color"],
                        linecolor=colors["line_color"],
                        tickfont=dict(color=colors["tick_color"]),
                    ),
                    angularaxis=dict(
                        gridcolor=colors["grid_color"],
                        linecolor=colors["line_color"],
                        tickfont=dict(color=colors["tick_color"]),
                    ),
                    bgcolor=colors["plot_bgcolor"],
                ),
                title=dict(
                    text="Your Music Mood Profile",
                    font=dict(color=colors["title_color"], size=16),
                ),
                showlegend=False,
                height=300,
                paper_bgcolor=colors["paper_bgcolor"],
                plot_bgcolor=colors["plot_bgcolor"],
                font=dict(color=colors["font_color"]),
            )

            return fig

        # Setup playlist callback
        self._setup_playlist_callback()

    def _generate_favorites_display(self, favorites):
        """Generate display for favorites list."""
        if not favorites:
            return html.P(
                "No favorites yet! Click ❤️ on tracks to add them.",
                className="empty-favorites",
            )

        favorites_items = []
        for track_id in favorites[-10:]:  # Show last 10 favorites
            track_info = self.recommender.get_track_info(track_id)
            if track_info:
                favorites_items.append(
                    html.Div(
                        [
                            html.Span(
                                f"🎵 {track_info.get('track_name', track_id)}",
                                className="favorite-track-name",
                            ),
                            html.Span(
                                f"👤 {track_info.get('artist_name', 'Unknown')}",
                                className="favorite-artist-name",
                            ),
                            html.Button(
                                "❌",
                                className="remove-favorite-btn",
                                **{"data-track-id": track_id},
                            ),
                        ],
                        className="favorite-item",
                    )
                )

        return favorites_items

    def _generate_playlists_display(self, playlists):
        """Generate display for playlists."""
        if not playlists:
            return html.P(
                "No playlists yet! Create your first playlist above.",
                className="empty-playlists",
            )

        playlist_items = []
        for playlist_id, playlist_data in playlists.items():
            playlist_items.append(
                html.Div(
                    [
                        html.H5(
                            f"📋 {playlist_data['name']}", className="playlist-name"
                        ),
                        html.P(
                            f"{len(playlist_data['tracks'])} tracks",
                            className="playlist-count",
                        ),
                        html.Button("▶️ Play", className="play-playlist-btn"),
                        html.Button("📤 Export", className="export-playlist-btn"),
                    ],
                    className="playlist-item",
                )
            )

        return playlist_items

    # Add to playlist callback (moved to correct indentation level)
    def _setup_playlist_callback(self):
        """Setup the playlist callback."""

        @self.app.callback(
            [
                Output("user-playlists", "data", allow_duplicate=True),
                Output("playlists-list", "children", allow_duplicate=True),
                Output("playlist-confirmation", "children", allow_duplicate=True),
            ],
            [Input({"type": "add-to-playlist-btn", "index": ALL}, "n_clicks")],
            [
                State("user-playlists", "data"),
                State({"type": "playlist-selector", "index": ALL}, "value"),
            ],
            prevent_initial_call=True,
        )
        def add_track_to_playlist(
            n_clicks_list, current_playlists, playlist_selections
        ):
            """Add track to the selected playlist."""
            if not n_clicks_list or not any(n_clicks_list):
                raise PreventUpdate

            # Find which button was clicked using callback context
            ctx = dash.callback_context
            if not ctx.triggered:
                raise PreventUpdate

            # Parse the triggered button to get track ID
            triggered_prop_id = ctx.triggered[0]["prop_id"]
            button_id = triggered_prop_id.split(".")[0]
            track_id = eval(button_id)["index"]

            # Initialize playlists if not exists
            if not current_playlists:
                current_playlists = {"My Music": []}

            # Find the correct dropdown value for this specific track
            # The key insight: we need to find the dropdown with the same track_id index
            selected_playlist = "My Music"  # default
            if playlist_selections:
                # Find which button index corresponds to our track_id
                button_index = -1
                for i, clicks in enumerate(n_clicks_list):
                    if clicks and clicks > 0:
                        button_index = i
                        break

                # Use the corresponding dropdown selection
                if button_index >= 0 and button_index < len(playlist_selections):
                    dropdown_value = playlist_selections[button_index]
                    if dropdown_value:
                        selected_playlist = dropdown_value

            # Create playlist if it doesn't exist
            if selected_playlist not in current_playlists:
                current_playlists[selected_playlist] = []

            # Get actual track info
            track_info = self.recommender.get_track_info(track_id)
            if track_info:
                track_data = {
                    "track_id": track_id,
                    "track_name": track_info.get("track_name", f"Track {track_id}"),
                    "artist_name": track_info.get("artist_name", "Unknown Artist"),
                }
            else:
                track_data = {
                    "track_id": track_id,
                    "track_name": f"Track {track_id}",
                    "artist_name": "Unknown Artist",
                }

            # Check for duplicates and add track
            track_exists = any(
                t.get("track_id") == track_id
                for t in current_playlists[selected_playlist]
            )
            if not track_exists:
                current_playlists[selected_playlist].append(track_data)
                confirmation_msg = (
                    f"✅ '{track_data['track_name']}' added to '{selected_playlist}'!"
                )
            else:
                confirmation_msg = (
                    f"ℹ️ '{track_data['track_name']}' already in '{selected_playlist}'."
                )

            # Create enhanced playlist display with delete and play buttons
            playlist_items = []
            for playlist_name, tracks in current_playlists.items():
                playlist_items.append(
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H4(playlist_name, className="playlist-name"),
                                    html.Div(
                                        [
                                            html.Button(
                                                "▶️ Play",
                                                id={
                                                    "type": "play-playlist-btn",
                                                    "index": playlist_name,
                                                },
                                                className="play-playlist-btn",
                                                title="Play all tracks in playlist",
                                            ),
                                            (
                                                html.Button(
                                                    "🗑️ Delete",
                                                    id={
                                                        "type": "delete-playlist-btn",
                                                        "index": playlist_name,
                                                    },
                                                    className="delete-playlist-btn",
                                                    title="Delete this playlist",
                                                )
                                                if playlist_name != "My Music"
                                                else None
                                            ),
                                        ],
                                        className="playlist-controls",
                                        style={"display": "flex", "gap": "8px"},
                                    ),
                                ],
                                style={
                                    "display": "flex",
                                    "justifyContent": "space-between",
                                    "alignItems": "center",
                                    "marginBottom": "10px",
                                },
                            ),
                            html.P(f"{len(tracks)} tracks", className="playlist-count"),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.P(
                                                f"{track['track_name']} - {track['artist_name']}",
                                                className="track-item",
                                                style={"flex": "1"},
                                            ),
                                            html.Button(
                                                "🗑️",
                                                id={
                                                    "type": "remove-track-btn",
                                                    "index": f"{playlist_name}:{track.get('track_id', i)}",
                                                },
                                                className="remove-track-btn",
                                                title="Remove from playlist",
                                                style={
                                                    "background": "#ff4757",
                                                    "color": "white",
                                                    "border": "none",
                                                    "borderRadius": "4px",
                                                    "padding": "4px 8px",
                                                    "cursor": "pointer",
                                                },
                                            ),
                                        ],
                                        style={
                                            "display": "flex",
                                            "alignItems": "center",
                                            "gap": "8px",
                                            "marginBottom": "4px",
                                        },
                                    )
                                    for i, track in enumerate(tracks)
                                ]
                            ),
                        ],
                        className="playlist-item",
                    )
                )

            return current_playlists, playlist_items, confirmation_msg

        # Update dropdown options when playlists change
        @self.app.callback(
            Output({"type": "playlist-selector", "index": ALL}, "options"),
            [Input("user-playlists", "data")],
            prevent_initial_call=False,
        )
        def update_playlist_dropdowns(current_playlists):
            """Update playlist dropdown options when playlists change."""
            if not current_playlists:
                current_playlists = {"My Music": []}

            # Always ensure My Music is included in options
            options = [
                {"label": name, "value": name} for name in current_playlists.keys()
            ]
            if "My Music" not in [opt["value"] for opt in options]:
                options.insert(0, {"label": "My Music", "value": "My Music"})
            if not options:
                options = [{"label": "My Music", "value": "My Music"}]

            # Return the same options for all dropdowns
            # Handle case where there might be no existing dropdowns yet
            try:
                ctx = dash.callback_context
                if ctx.outputs_list:
                    num_outputs = len(ctx.outputs_list)
                    return [options] * num_outputs
                else:
                    return []
            except (AttributeError, TypeError):
                # If no dropdowns exist yet, return empty list
                return []

        # Delete playlist callback
        @self.app.callback(
            [
                Output("user-playlists", "data", allow_duplicate=True),
                Output("playlists-list", "children", allow_duplicate=True),
            ],
            [Input({"type": "delete-playlist-btn", "index": ALL}, "n_clicks")],
            [State("user-playlists", "data")],
            prevent_initial_call=True,
        )
        def delete_playlist(n_clicks_list, current_playlists):
            """Delete a playlist."""
            if not n_clicks_list or not any(n_clicks_list):
                raise PreventUpdate

            ctx = dash.callback_context
            if not ctx.triggered:
                raise PreventUpdate

            button_id = ctx.triggered[0]["prop_id"].split(".")[0]
            playlist_name = eval(button_id)["index"]

            if not current_playlists:
                current_playlists = {"My Music": []}

            # Don't delete "My Music" playlist
            if playlist_name != "My Music" and playlist_name in current_playlists:
                del current_playlists[playlist_name]

            # Regenerate playlist display
            playlist_items = []
            for playlist_name, tracks in current_playlists.items():
                playlist_items.append(
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H4(playlist_name, className="playlist-name"),
                                    html.Div(
                                        [
                                            html.Button(
                                                "▶️ Play",
                                                id={
                                                    "type": "play-playlist-btn",
                                                    "index": playlist_name,
                                                },
                                                className="play-playlist-btn",
                                                title="Play all tracks in playlist",
                                            ),
                                            (
                                                html.Button(
                                                    "🗑️ Delete",
                                                    id={
                                                        "type": "delete-playlist-btn",
                                                        "index": playlist_name,
                                                    },
                                                    className="delete-playlist-btn",
                                                    title="Delete this playlist",
                                                )
                                                if playlist_name != "My Music"
                                                else None
                                            ),
                                        ],
                                        className="playlist-controls",
                                        style={"display": "flex", "gap": "8px"},
                                    ),
                                ],
                                style={
                                    "display": "flex",
                                    "justifyContent": "space-between",
                                    "alignItems": "center",
                                    "marginBottom": "10px",
                                },
                            ),
                            html.P(f"{len(tracks)} tracks", className="playlist-count"),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.P(
                                                f"{track['track_name']} - {track['artist_name']}",
                                                className="track-item",
                                                style={"flex": "1"},
                                            ),
                                            html.Button(
                                                "🗑️",
                                                id={
                                                    "type": "remove-track-btn",
                                                    "index": f"{playlist_name}:{track.get('track_id', i)}",
                                                },
                                                className="remove-track-btn",
                                                title="Remove from playlist",
                                                style={
                                                    "background": "#ff4757",
                                                    "color": "white",
                                                    "border": "none",
                                                    "borderRadius": "4px",
                                                    "padding": "4px 8px",
                                                    "cursor": "pointer",
                                                },
                                            ),
                                        ],
                                        style={
                                            "display": "flex",
                                            "alignItems": "center",
                                            "gap": "8px",
                                            "marginBottom": "4px",
                                        },
                                    )
                                    for i, track in enumerate(tracks)
                                ]
                            ),
                        ],
                        className="playlist-item",
                    )
                )

            return current_playlists, playlist_items

        # Play playlist callback
        @self.app.callback(
            Output("playlist-confirmation", "children", allow_duplicate=True),
            [Input({"type": "play-playlist-btn", "index": ALL}, "n_clicks")],
            [State("user-playlists", "data")],
            prevent_initial_call=True,
        )
        def play_playlist(n_clicks_list, current_playlists):
            """Play all tracks in a playlist."""
            if not n_clicks_list or not any(n_clicks_list):
                raise PreventUpdate

            ctx = dash.callback_context
            if not ctx.triggered:
                raise PreventUpdate

            button_id = ctx.triggered[0]["prop_id"].split(".")[0]
            playlist_name = eval(button_id)["index"]

            if not current_playlists or playlist_name not in current_playlists:
                raise PreventUpdate

            tracks = current_playlists[playlist_name]
            if not tracks:
                return html.Div(
                    [
                        html.P(
                            f"⚠️ Playlist '{playlist_name}' is empty!",
                            style={
                                "color": "#f59e0b",
                                "margin": "10px 0",
                                "fontWeight": "bold",
                            },
                        )
                    ]
                )

            # Simulate playing playlist (in a real app, this would integrate with music player)
            confirmation = html.Div(
                [
                    html.P(
                        f"🎵 Playing playlist '{playlist_name}' ({len(tracks)} tracks)!",
                        style={
                            "color": "#10b981",
                            "margin": "10px 0",
                            "fontWeight": "bold",
                        },
                    ),
                    html.P(
                        f"♪ Starting with: {tracks[0]['track_name']} - {tracks[0]['artist_name']}",
                        style={
                            "color": "#6b7280",
                            "margin": "5px 0",
                            "fontSize": "0.9em",
                        },
                    ),
                ]
            )

            return confirmation

        # Remove track from playlist callback
        @self.app.callback(
            [
                Output("user-playlists", "data", allow_duplicate=True),
                Output("playlists-list", "children", allow_duplicate=True),
                Output("playlist-confirmation", "children", allow_duplicate=True),
            ],
            [Input({"type": "remove-track-btn", "index": ALL}, "n_clicks")],
            [State("user-playlists", "data")],
            prevent_initial_call=True,
        )
        def remove_track_from_playlist(n_clicks_list, current_playlists):
            """Remove a track from a playlist."""
            if not n_clicks_list or not any(n_clicks_list):
                raise PreventUpdate

            ctx = dash.callback_context
            if not ctx.triggered:
                raise PreventUpdate

            button_id = ctx.triggered[0]["prop_id"].split(".")[0]
            playlist_track_id = eval(button_id)["index"]

            # Parse playlist name and track id from the combined index
            playlist_name, track_id = playlist_track_id.split(":", 1)

            if not current_playlists:
                current_playlists = {"My Music": []}

            # Remove track from playlist
            if playlist_name in current_playlists:
                tracks = current_playlists[playlist_name]
                # Find and remove the track
                for i, track in enumerate(tracks):
                    if track.get("track_id", str(i)) == track_id:
                        track_name = track.get("track_name", "Unknown Track")
                        tracks.pop(i)
                        break
                else:
                    track_name = "Unknown Track"

            # Regenerate playlist display
            playlist_items = []
            for pname, tracks in current_playlists.items():
                delete_btn = (
                    html.Button(
                        "🗑️ Delete",
                        id={"type": "delete-playlist-btn", "index": pname},
                        className="delete-playlist-btn",
                        style={
                            "background": "#ef4444",
                            "color": "white",
                            "border": "none",
                            "borderRadius": "4px",
                            "padding": "4px 8px",
                            "cursor": "pointer",
                        },
                        title="Delete this playlist",
                    )
                    if pname != "My Music"
                    else None
                )

                playlist_items.append(
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H4(pname, className="playlist-name"),
                                    html.Div(
                                        [
                                            html.Button(
                                                "▶️ Play",
                                                id={
                                                    "type": "play-playlist-btn",
                                                    "index": pname,
                                                },
                                                className="play-playlist-btn",
                                                style={
                                                    "background": "#10b981",
                                                    "color": "white",
                                                    "border": "none",
                                                    "borderRadius": "4px",
                                                    "padding": "4px 8px",
                                                    "cursor": "pointer",
                                                },
                                            ),
                                            delete_btn,
                                        ],
                                        className="playlist-controls",
                                        style={"display": "flex", "gap": "8px"},
                                    ),
                                ],
                                style={
                                    "display": "flex",
                                    "justifyContent": "space-between",
                                    "alignItems": "center",
                                    "marginBottom": "10px",
                                },
                            ),
                            html.P(f"{len(tracks)} tracks", className="playlist-count"),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.P(
                                                f"{track['track_name']} - {track['artist_name']}",
                                                className="track-item",
                                                style={"flex": "1"},
                                            ),
                                            html.Button(
                                                "🗑️",
                                                id={
                                                    "type": "remove-track-btn",
                                                    "index": f"{pname}:{track.get('track_id', i)}",
                                                },
                                                className="remove-track-btn",
                                                title="Remove from playlist",
                                                style={
                                                    "background": "#ff4757",
                                                    "color": "white",
                                                    "border": "none",
                                                    "borderRadius": "4px",
                                                    "padding": "4px 8px",
                                                    "cursor": "pointer",
                                                },
                                            ),
                                        ],
                                        style={
                                            "display": "flex",
                                            "alignItems": "center",
                                            "gap": "8px",
                                            "marginBottom": "4px",
                                        },
                                    )
                                    for i, track in enumerate(tracks)
                                ]
                            ),
                        ],
                        className="playlist-item",
                    )
                )

            confirmation_msg = html.Div(
                [
                    html.P(
                        f"🗑️ Removed '{track_name}' from '{playlist_name}'!",
                        style={
                            "color": "#f59e0b",
                            "margin": "10px 0",
                            "fontWeight": "bold",
                        },
                    )
                ]
            )

            return current_playlists, playlist_items, confirmation_msg


# Additional CSS styles for the user features
USER_FEATURES_STYLES = """
/* User Features Styling */
.user-features-section {
    background: var(--bg-secondary);
    border-radius: 15px;
    padding: 30px;
    margin: 20px 0;
    border: 1px solid var(--border-color);
}

.user-library-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 30px;
    margin-top: 20px;
}

.favorites-section, .playlists-section {
    background: var(--bg-primary);
    border-radius: 12px;
    padding: 25px;
    border: 1px solid var(--border-light);
}

.subsection-title {
    color: var(--primary-purple);
    margin-bottom: 15px;
    font-size: 1.2rem;
    font-weight: 600;
}

.favorites-container {
    max-height: 300px;
    overflow-y: auto;
    margin-bottom: 15px;
}

.favorite-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px;
    background: var(--bg-hover);
    border-radius: 8px;
    margin-bottom: 8px;
    border: 1px solid var(--border-light);
}

.favorite-track-name {
    font-weight: 500;
    color: var(--text-primary);
}

.favorite-artist-name {
    color: var(--text-secondary);
    font-size: 0.9rem;
}

.playlist-creator {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

.playlist-input {
    flex: 1;
    padding: 12px;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    background: var(--bg-primary);
    color: var(--text-primary);
    font-size: 14px;
}

.create-playlist-btn {
    padding: 12px 20px;
    background: var(--primary-purple);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
}

.create-playlist-btn:hover {
    background: var(--primary-purple-dark);
    transform: translateY(-1px);
}

.playlist-item {
    background: var(--bg-hover);
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 15px;
    border: 1px solid var(--border-light);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: all 0.2s ease;
}

.playlist-item:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.playlist-controls {
    display: flex;
    gap: 8px;
    align-items: center;
}

.play-playlist-btn,
.delete-playlist-btn {
    padding: 6px 12px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.85rem;
    font-weight: 500;
    transition: all 0.2s ease;
}

.play-playlist-btn {
    background: linear-gradient(135deg, #10b981, #059669);
    color: white;
}

.play-playlist-btn:hover {
    background: linear-gradient(135deg, #059669, #047857);
    transform: translateY(-1px);
}

.delete-playlist-btn {
    background: linear-gradient(135deg, #ef4444, #dc2626);
    color: white;
}

.delete-playlist-btn:hover {
    background: linear-gradient(135deg, #dc2626, #b91c1c);
    transform: translateY(-1px);
}

.playlist-name {
    margin-bottom: 8px;
    color: var(--text-primary);
}

.playlist-count {
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin-bottom: 10px;
}

/* Discovery Dashboard Styles */
.discovery-dashboard {
    background: var(--bg-secondary);
    border-radius: 15px;
    padding: 30px;
    margin: 20px 0;
    border: 1px solid var(--border-color);
}

.dashboard-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 25px;
    margin-top: 20px;
}

.stats-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15px;
}

.stat-card {
    background: var(--bg-primary);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    border: 1px solid var(--border-light);
    transition: transform 0.2s ease;
}

.stat-card:hover {
    transform: translateY(-2px);
}

.stat-number {
    font-size: 2rem;
    font-weight: 700;
    color: var(--primary-purple);
    margin-bottom: 5px;
}

.stat-label {
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin: 0;
}

.genre-stat {
    font-size: 1.2rem !important;
    text-transform: capitalize;
}

.explore-btn {
    background: linear-gradient(135deg, var(--primary-purple), var(--secondary-blue));
    color: white;
    border: none;
    border-radius: 10px;
    padding: 15px 25px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    margin-bottom: 20px;
}

.explore-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(139, 92, 246, 0.3);
}

.mini-track-card {
    background: var(--bg-primary);
    border-radius: 8px;
    padding: 12px;
    margin: 8px 0;
    border: 1px solid var(--border-light);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.mini-play-btn {
    background: var(--primary-purple);
    color: white;
    border: none;
    border-radius: 50%;
    width: 30px;
    height: 30px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Mobile Responsiveness */
@media (max-width: 1024px) {
    .dashboard-grid {
        grid-template-columns: 1fr 1fr;
    }
}

@media (max-width: 768px) {
    .user-library-grid,
    .dashboard-grid {
        grid-template-columns: 1fr;
    }

    .stats-container {
        grid-template-columns: 1fr 1fr;
    }
}

@media (max-width: 480px) {
    .stats-container {
        grid-template-columns: 1fr;
    }
}
"""
