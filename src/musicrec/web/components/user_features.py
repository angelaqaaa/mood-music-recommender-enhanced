"""User-facing interactive features for the music recommender.

This module provides practical features that users can interact with:
- Favorites/bookmarking system
- Playlist generator
- Music discovery dashboard
- User preferences management
"""

import json
from datetime import datetime
from typing import Dict, List, Any
import dash
from dash import dcc, html, Input, Output, State, callback_context
import plotly.graph_objects as go
import plotly.express as px
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
        return html.Div([
            html.H3("❤️ Your Music Library", className="section-title"),
            html.Div([
                html.Div([
                    html.H4("⭐ Favorites", className="subsection-title"),
                    html.Div(id="favorites-list", className="favorites-container"),
                    html.P("Click the ❤️ button on any track to add it to favorites!",
                          className="help-text")
                ], className="favorites-section"),

                html.Div([
                    html.H4("📋 Custom Playlists", className="subsection-title"),
                    html.Div([
                        dcc.Input(
                            id="new-playlist-name",
                            type="text",
                            placeholder="Enter playlist name...",
                            className="playlist-input"
                        ),
                        html.Button("➕ Create Playlist", id="create-playlist-btn",
                                  className="create-playlist-btn")
                    ], className="playlist-creator"),
                    html.Div(id="playlists-list", className="playlists-container")
                ], className="playlists-section")
            ], className="user-library-grid"),

            # Hidden stores for user data
            dcc.Store(id="user-favorites", data=[]),
            dcc.Store(id="user-playlists", data={}),
        ], className="user-features-section")

    def create_discovery_dashboard(self):
        """Create music discovery dashboard with user statistics."""
        return html.Div([
            html.H3("🎯 Discovery Dashboard", className="section-title"),
            html.Div([
                html.Div([
                    html.H4("📊 Your Music Stats", className="stats-title"),
                    html.Div(id="user-stats", className="stats-container")
                ], className="stats-section"),

                html.Div([
                    html.H4("🔍 Genre Explorer", className="explorer-title"),
                    html.P("Discover new genres based on your preferences:",
                          className="explorer-description"),
                    html.Button("🎲 Explore Random Genre", id="explore-genre-btn",
                              className="explore-btn"),
                    html.Div(id="genre-exploration", className="exploration-results")
                ], className="explorer-section"),

                html.Div([
                    html.H4("🎵 Mood Journey", className="mood-title"),
                    html.P("Track your musical mood journey:",
                          className="mood-description"),
                    dcc.Graph(id="mood-journey-chart", className="mood-chart")
                ], className="mood-section")
            ], className="dashboard-grid")
        ], className="discovery-dashboard")

    def register_callbacks(self):
        """Register all callbacks for user features."""

        # Favorites management callback
        @self.app.callback(
            [Output("user-favorites", "data"),
             Output("favorites-list", "children")],
            [Input({"type": "favorite-btn", "index": dash.ALL}, "n_clicks")],
            [State("user-favorites", "data"),
             State("current-recommendations-store", "data")],
            prevent_initial_call=True
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
            track_index = int(button_id.split('"index":')[1].split(',')[0])

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
            [Output("user-playlists", "data"),
             Output("playlists-list", "children"),
             Output("new-playlist-name", "value")],
            [Input("create-playlist-btn", "n_clicks")],
            [State("new-playlist-name", "value"),
             State("user-playlists", "data")],
            prevent_initial_call=True
        )
        def create_playlist(n_clicks, playlist_name, current_playlists):
            """Create a new playlist."""
            if not n_clicks or not playlist_name:
                raise PreventUpdate

            # Add new playlist
            playlist_id = f"playlist_{len(current_playlists)}"
            current_playlists[playlist_id] = {
                "name": playlist_name,
                "tracks": [],
                "created": datetime.now().isoformat()
            }

            # Generate playlists display
            playlists_display = self._generate_playlists_display(current_playlists)

            return current_playlists, playlists_display, ""

        # User statistics callback
        @self.app.callback(
            Output("user-stats", "children"),
            [Input("user-favorites", "data"),
             Input("user-playlists", "data")],
            prevent_initial_call=True
        )
        def update_user_stats(favorites, playlists):
            """Update user statistics display."""
            total_favorites = len(favorites)
            total_playlists = len(playlists)
            total_playlist_tracks = sum(len(p.get("tracks", [])) for p in playlists.values())

            # Calculate favorite genres
            favorite_genres = {}
            for track_id in favorites:
                track_info = self.recommender.get_track_info(track_id)
                if track_info:
                    genre = track_info.get("primary_genre", "Unknown")
                    favorite_genres[genre] = favorite_genres.get(genre, 0) + 1

            top_genre = max(favorite_genres.keys(), key=favorite_genres.get) if favorite_genres else "None"

            return html.Div([
                html.Div([
                    html.H3(str(total_favorites), className="stat-number"),
                    html.P("Favorite Tracks", className="stat-label")
                ], className="stat-card"),
                html.Div([
                    html.H3(str(total_playlists), className="stat-number"),
                    html.P("Custom Playlists", className="stat-label")
                ], className="stat-card"),
                html.Div([
                    html.H3(str(total_playlist_tracks), className="stat-number"),
                    html.P("Playlist Tracks", className="stat-label")
                ], className="stat-card"),
                html.Div([
                    html.H3(top_genre, className="stat-number genre-stat"),
                    html.P("Top Genre", className="stat-label")
                ], className="stat-card")
            ])

        # Genre exploration callback
        @self.app.callback(
            Output("genre-exploration", "children"),
            [Input("explore-genre-btn", "n_clicks")],
            prevent_initial_call=True
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
                return html.Div("No tracks found for this genre.", className="no-results")

            return html.Div([
                html.H5(f"🎵 Exploring: {random_genre.title()}", className="exploration-title"),
                html.Div([
                    html.Div([
                        html.P(f"🎵 {track.data.get('track_name', track.track_id)}",
                              className="track-name"),
                        html.P(f"👤 {track.data.get('artist_name', 'Unknown')}",
                              className="artist-name"),
                        html.Button("▶️", className="mini-play-btn"),
                    ], className="mini-track-card")
                    for track in recommendations
                ])
            ])

        # Mood journey chart callback
        @self.app.callback(
            Output("mood-journey-chart", "figure"),
            [Input("user-favorites", "data")],
            prevent_initial_call=True
        )
        def update_mood_journey(favorites):
            """Create a mood journey chart based on user's favorites."""
            if not favorites:
                return go.Figure().add_annotation(
                    text="Add some favorite tracks to see your mood journey!",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )

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

            # Create polar chart
            fig = go.Figure(go.Scatterpolar(
                r=list(moods_data.values()),
                theta=list(moods_data.keys()),
                fill='toself',
                name='Your Music Mood',
                line=dict(color='rgb(139, 92, 246)')
            ))

            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, max(moods_data.values()) + 1])
                ),
                title="Your Music Mood Profile",
                showlegend=False,
                height=300
            )

            return fig

    def _generate_favorites_display(self, favorites):
        """Generate display for favorites list."""
        if not favorites:
            return html.P("No favorites yet! Click ❤️ on tracks to add them.",
                         className="empty-favorites")

        favorites_items = []
        for track_id in favorites[-10:]:  # Show last 10 favorites
            track_info = self.recommender.get_track_info(track_id)
            if track_info:
                favorites_items.append(html.Div([
                    html.Span(f"🎵 {track_info.get('track_name', track_id)}",
                             className="favorite-track-name"),
                    html.Span(f"👤 {track_info.get('artist_name', 'Unknown')}",
                             className="favorite-artist-name"),
                    html.Button("❌", className="remove-favorite-btn",
                              **{"data-track-id": track_id})
                ], className="favorite-item"))

        return favorites_items

    def _generate_playlists_display(self, playlists):
        """Generate display for playlists."""
        if not playlists:
            return html.P("No playlists yet! Create your first playlist above.",
                         className="empty-playlists")

        playlist_items = []
        for playlist_id, playlist_data in playlists.items():
            playlist_items.append(html.Div([
                html.H5(f"📋 {playlist_data['name']}", className="playlist-name"),
                html.P(f"{len(playlist_data['tracks'])} tracks", className="playlist-count"),
                html.Button("▶️ Play", className="play-playlist-btn"),
                html.Button("📤 Export", className="export-playlist-btn")
            ], className="playlist-item"))

        return playlist_items


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
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 10px;
    border: 1px solid var(--border-light);
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