"""CSS styles for responsive Dash UI components.

This module contains CSS styles for making the music recommender UI responsive
across mobile, tablet, and desktop devices.
"""

# Enhanced responsive styles with modern design system
RESPONSIVE_STYLES = """
/* Modern CSS Variables for Design System */
:root {
    /* Primary Colors - Music Theme */
    --primary-purple: #8B5CF6;
    --primary-purple-light: #A78BFA;
    --primary-purple-dark: #7C3AED;
    --secondary-blue: #3B82F6;
    --secondary-blue-light: #60A5FA;

    /* Accent Colors */
    --accent-pink: #EC4899;
    --accent-orange: #F97316;
    --accent-green: #10B981;

    /* Neutral Colors */
    --gray-50: #F9FAFB;
    --gray-100: #F3F4F6;
    --gray-200: #E5E7EB;
    --gray-300: #D1D5DB;
    --gray-400: #9CA3AF;
    --gray-500: #6B7280;
    --gray-600: #4B5563;
    --gray-700: #374151;
    --gray-800: #1F2937;
    --gray-900: #111827;

    /* Background Colors */
    --bg-primary: #FFFFFF;
    --bg-secondary: #F8FAFC;
    --bg-accent: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

    /* Text Colors */
    --text-primary: #1F2937;
    --text-secondary: #6B7280;
    --text-inverse: #FFFFFF;

    /* Shadows */
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);

    /* Border Radius */
    --radius-sm: 0.375rem;
    --radius-md: 0.5rem;
    --radius-lg: 0.75rem;
    --radius-xl: 1rem;

    /* Typography */
    --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    --font-display: 'Inter', sans-serif;
}

/* Dark Mode Variables */
[data-theme="dark"] {
    /* Dark Mode Colors */
    --gray-50: #111827;
    --gray-100: #1F2937;
    --gray-200: #374151;
    --gray-300: #4B5563;
    --gray-400: #6B7280;
    --gray-500: #9CA3AF;
    --gray-600: #D1D5DB;
    --gray-700: #E5E7EB;
    --gray-800: #F3F4F6;
    --gray-900: #F9FAFB;

    /* Dark Background Colors */
    --bg-primary: #111827;
    --bg-secondary: #0F172A;
    --bg-accent: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

    /* Dark Text Colors */
    --text-primary: #F9FAFB;
    --text-secondary: #D1D5DB;
    --text-inverse: #111827;
}

/* Base styles for all devices */
* {
    box-sizing: border-box;
}

body {
    font-family: var(--font-sans);
    line-height: 1.6;
    color: var(--text-primary);
    background: var(--bg-secondary);
    margin: 0;
    padding: 0;
}

.main-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem;
    min-height: 100vh;
}

/* Modern Header Styles */
.app-header {
    background: var(--bg-accent);
    color: var(--text-inverse);
    padding: 3rem 2rem;
    text-align: center;
    margin: -2rem -2rem 2rem -2rem;
    border-radius: 0 0 var(--radius-xl) var(--radius-xl);
    box-shadow: var(--shadow-lg);
    position: relative;
    overflow: hidden;
}

.app-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="music-pattern" patternUnits="userSpaceOnUse" width="20" height="20"><circle cx="10" cy="10" r="1" fill="rgba(255,255,255,0.1)"/></pattern></defs><rect width="100" height="100" fill="url(%23music-pattern)"/></svg>');
    opacity: 0.3;
}

.app-title {
    font-family: var(--font-display);
    font-size: 2.5rem;
    font-weight: 700;
    margin: 0;
    position: relative;
    z-index: 1;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.app-subtitle {
    font-size: 1.1rem;
    opacity: 0.9;
    margin: 0.5rem 0 0 0;
    position: relative;
    z-index: 1;
}

/* Modern Card-based Layout */
.controls-container {
    background: var(--bg-primary);
    border-radius: var(--radius-lg);
    padding: 2rem;
    box-shadow: var(--shadow-md);
    border: 1px solid var(--gray-200);
    margin-bottom: 2rem;
    transition: box-shadow 0.3s ease;
}

.controls-container:hover {
    box-shadow: var(--shadow-lg);
}

.results-container {
    background: var(--bg-primary);
    border-radius: var(--radius-lg);
    padding: 2rem;
    box-shadow: var(--shadow-md);
    border: 1px solid var(--gray-200);
    min-height: 400px;
}

/* Enhanced Recommendation Cards */
.recommendation-item {
    background: var(--bg-primary);
    border: 2px solid var(--gray-200);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: all 0.3s ease;
    box-shadow: var(--shadow-sm);
    position: relative;
    overflow: hidden;
}

.recommendation-item::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: linear-gradient(45deg, var(--primary-purple), var(--accent-pink));
    opacity: 0;
    transition: opacity 0.3s ease;
}

.recommendation-item:hover {
    border-color: var(--primary-purple-light);
    box-shadow: var(--shadow-lg);
    transform: translateY(-2px);
}

.recommendation-item:hover::before {
    opacity: 1;
}

.recommendation-item:focus-within {
    outline: 2px solid var(--primary-purple);
    outline-offset: 2px;
    border-color: var(--primary-purple);
}

.recommendation-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1rem;
}

.recommendation-icon {
    width: 40px;
    height: 40px;
    background: linear-gradient(45deg, var(--primary-purple), var(--secondary-blue));
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-inverse);
    font-weight: bold;
    font-size: 1.2rem;
    flex-shrink: 0;
}

.recommendation-title {
    font-family: var(--font-display);
    font-weight: 600;
    font-size: 1.25rem;
    color: var(--text-primary);
    margin: 0;
    line-height: 1.3;
}

.recommendation-artist {
    color: var(--text-secondary);
    font-size: 1rem;
    margin: 0.25rem 0;
    font-weight: 500;
}

.recommendation-details {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin: 1rem 0;
}

.recommendation-tag {
    background: var(--gray-100);
    color: var(--text-secondary);
    padding: 0.25rem 0.75rem;
    border-radius: var(--radius-sm);
    font-size: 0.875rem;
    font-weight: 500;
}

.recommendation-tag.genre {
    background: linear-gradient(45deg, var(--primary-purple-light), var(--secondary-blue-light));
    color: var(--text-inverse);
}

.recommendation-tag.mood {
    background: linear-gradient(45deg, var(--accent-pink), var(--accent-orange));
    color: var(--text-inverse);
}

.recommendation-explanation {
    background: linear-gradient(45deg, var(--gray-50), var(--gray-100));
    border-left: 4px solid var(--primary-purple);
    border-radius: var(--radius-md);
    padding: 1rem;
    margin-top: 1rem;
    font-style: italic;
    color: var(--text-secondary);
    font-size: 0.95rem;
    line-height: 1.5;
}

.recommendation-actions {
    display: flex;
    gap: 0.5rem;
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid var(--gray-200);
}

.recommendation-button {
    background: var(--primary-purple);
    color: var(--text-inverse);
    border: none;
    border-radius: var(--radius-md);
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
}

.recommendation-button:hover {
    background: var(--primary-purple-dark);
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
}

.recommendation-button.secondary {
    background: var(--gray-600);
}

.recommendation-button.secondary:hover {
    background: var(--gray-700);
}

/* Enhanced Form Controls */
.form-section {
    margin-bottom: 2rem;
}

.form-section h3 {
    font-family: var(--font-display);
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 1rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.form-section h3::before {
    content: '';
    width: 4px;
    height: 1.25rem;
    background: linear-gradient(45deg, var(--primary-purple), var(--accent-pink));
    border-radius: 2px;
}

.form-group {
    margin-bottom: 1.5rem;
}

.form-label {
    display: block;
    font-weight: 500;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
    font-size: 0.95rem;
}

/* Enhanced Dropdown Styles */
.dash-dropdown .Select-control {
    border: 2px solid var(--gray-300) !important;
    border-radius: var(--radius-md) !important;
    background: var(--bg-primary) !important;
    box-shadow: var(--shadow-sm) !important;
    transition: all 0.2s ease !important;
    min-height: 42px !important;
}

.dash-dropdown .Select-control:hover {
    border-color: var(--primary-purple-light) !important;
    box-shadow: var(--shadow-md) !important;
}

.dash-dropdown .Select-control.is-focused {
    border-color: var(--primary-purple) !important;
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1) !important;
}

.dash-dropdown .Select-value-label {
    color: var(--text-primary) !important;
    font-weight: 500 !important;
}

.dash-dropdown .Select-placeholder {
    color: var(--text-secondary) !important;
}

/* Enhanced Tab Styles */
.dash-tabs {
    border-bottom: 2px solid var(--gray-200) !important;
    margin-bottom: 2rem !important;
}

.dash-tabs .tab {
    background: transparent !important;
    border: none !important;
    border-bottom: 3px solid transparent !important;
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    padding: 1rem 1.5rem !important;
    transition: all 0.2s ease !important;
    border-radius: var(--radius-md) var(--radius-md) 0 0 !important;
}

.dash-tabs .tab:hover {
    color: var(--primary-purple) !important;
    background: var(--gray-50) !important;
}

.dash-tabs .tab.tab--selected {
    color: var(--primary-purple) !important;
    border-bottom-color: var(--primary-purple) !important;
    background: var(--bg-primary) !important;
    font-weight: 600 !important;
}

/* Enhanced Radio Button Styles */
.dash-radio-item {
    display: flex !important;
    align-items: center !important;
    gap: 0.75rem !important;
    padding: 0.75rem 1rem !important;
    border: 2px solid var(--gray-200) !important;
    border-radius: var(--radius-md) !important;
    margin-bottom: 0.5rem !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
}

.dash-radio-item:hover {
    border-color: var(--primary-purple-light) !important;
    background: var(--gray-50) !important;
}

.dash-radio-item input:checked + label {
    border-color: var(--primary-purple) !important;
    background: linear-gradient(45deg, var(--primary-purple-light), var(--secondary-blue-light)) !important;
    color: var(--text-inverse) !important;
}

/* Enhanced Loading Indicator */
.loading-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    background: var(--bg-primary);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
    margin: 1rem 0;
    color: var(--text-secondary);
}

.loading-spinner {
    width: 24px;
    height: 24px;
    border: 3px solid var(--gray-200);
    border-top: 3px solid var(--primary-purple);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-right: 12px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.loading-text {
    font-weight: 500;
    font-size: 1rem;
}

.metrics-panel {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 20px;
}

.metrics-panel h4 {
    margin-top: 0;
    color: #495057;
}

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 10px;
}

.metric-item {
    text-align: center;
    padding: 10px;
    background-color: white;
    border-radius: 4px;
    border: 1px solid #e9ecef;
}

.metric-value {
    font-size: 1.2em;
    font-weight: bold;
    color: #0078d4;
}

.metric-label {
    font-size: 0.85em;
    color: #6c757d;
    margin-top: 5px;
}

/* Enhanced Mobile Styles */
@media (max-width: 767px) {
    .main-container {
        padding: 1rem;
    }

    .app-header {
        margin: -1rem -1rem 1rem -1rem;
        padding: 2rem 1rem;
    }

    .app-title {
        font-size: 2rem;
    }

    .controls-container,
    .results-container {
        padding: 1.5rem;
        margin-bottom: 1rem;
    }

    .recommendation-item {
        padding: 1rem;
    }

    .recommendation-icon {
        width: 32px;
        height: 32px;
        font-size: 1rem;
    }

    .recommendation-title {
        font-size: 1.1rem;
    }

    .recommendation-actions {
        flex-direction: column;
    }

    .recommendation-button {
        width: 100%;
        justify-content: center;
        margin-bottom: 0.5rem;
    }

    .form-group {
        margin-bottom: 1rem;
    }

    .dash-tabs .tab {
        padding: 0.75rem 1rem !important;
        font-size: 0.9rem !important;
    }
}

/* Enhanced Tablet Styles */
@media (min-width: 768px) and (max-width: 1023px) {
    .main-layout {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2rem;
        align-items: start;
    }

    .controls-container {
        margin-bottom: 0;
    }

    .recommendation-item {
        padding: 1.25rem;
    }

    .app-title {
        font-size: 2.25rem;
    }

    .metrics-panel {
        position: sticky;
        top: 2rem;
    }
}

/* Enhanced Desktop Styles */
@media (min-width: 1024px) {
    .main-layout {
        display: grid;
        grid-template-columns: 1fr 2fr;
        gap: 3rem;
        align-items: start;
    }

    .controls-container {
        position: sticky;
        top: 2rem;
        margin-bottom: 0;
    }

    .main-container {
        padding: 3rem;
    }

    .app-header {
        margin: -3rem -3rem 3rem -3rem;
    }

    .recommendation-item {
        padding: 2rem;
    }

    .metrics-grid {
        grid-template-columns: repeat(4, 1fr);
    }

    .app-title {
        font-size: 3rem;
    }

    .recommendation-actions {
        flex-direction: row;
    }

    .recommendation-button {
        width: auto;
    }
}

/* Large Desktop Styles */
@media (min-width: 1440px) {
    .main-container {
        padding: 4rem;
    }

    .app-header {
        margin: -4rem -4rem 4rem -4rem;
        padding: 4rem 2rem;
    }

    .main-layout {
        gap: 4rem;
    }
}

/* Mobile-first accessibility improvements */
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}

/* Focus styles for keyboard navigation */
.dash-dropdown .Select-control:focus,
.dash-dropdown .Select-control.is-focused {
    outline: 2px solid #0078d4;
    outline-offset: 2px;
}

button:focus,
.dash-radio-item input:focus + label,
.dash-slider .rc-slider-handle:focus {
    outline: 2px solid #0078d4;
    outline-offset: 2px;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
    .recommendation-item {
        border-color: #000;
        background-color: #fff;
    }
    
    .recommendation-explanation {
        background-color: #fff;
        border-color: #000;
    }
}

/* Dark Mode Toggle */
.theme-toggle {
    position: fixed;
    top: 2rem;
    right: 2rem;
    z-index: 1000;
    background: var(--bg-primary);
    border: 2px solid var(--gray-300);
    border-radius: 50%;
    width: 50px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: var(--shadow-lg);
    font-size: 1.25rem;
}

.theme-toggle:hover {
    transform: scale(1.1);
    box-shadow: var(--shadow-xl);
    border-color: var(--primary-purple);
}

.theme-toggle:active {
    transform: scale(0.95);
}

/* Smooth Theme Transitions */
* {
    transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease !important;
}

/* Auto Dark Mode Support */
@media (prefers-color-scheme: dark) {
    :root {
        /* Auto-apply dark mode colors if user prefers dark */
        --gray-50: #111827;
        --gray-100: #1F2937;
        --gray-200: #374151;
        --gray-300: #4B5563;
        --gray-400: #6B7280;
        --gray-500: #9CA3AF;
        --gray-600: #D1D5DB;
        --gray-700: #E5E7EB;
        --gray-800: #F3F4F6;
        --gray-900: #F9FAFB;

        --bg-primary: #111827;
        --bg-secondary: #0F172A;
        --text-primary: #F9FAFB;
        --text-secondary: #D1D5DB;
        --text-inverse: #111827;
    }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
    .loading-spinner {
        animation: none;
    }

    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* Enhanced Scrollbar Styling */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: var(--gray-100);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb {
    background: var(--primary-purple);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--primary-purple-dark);
}

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
    flex: 1;
}

.favorite-artist-name {
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin-left: 10px;
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

.track-card-actions {
    display: flex;
    gap: 8px;
    align-items: center;
    margin-top: 12px;
}

.favorite-btn {
    background: none;
    border: none;
    font-size: 1.2rem;
    cursor: pointer;
    padding: 5px 10px;
    border-radius: 6px;
    transition: all 0.2s ease;
}

.favorite-btn:hover {
    background: var(--bg-hover);
}

.favorite-btn.active {
    color: #ff4757;
}

.add-to-playlist-btn {
    background: var(--secondary-blue);
    color: white;
    border: none;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 0.8rem;
    cursor: pointer;
    transition: all 0.2s ease;
}

.add-to-playlist-btn:hover {
    background: var(--secondary-blue-dark);
}

/* Mobile Responsiveness for User Features */
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

    .track-card-actions {
        flex-direction: column;
        gap: 5px;
    }
}

@media (max-width: 480px) {
    .stats-container {
        grid-template-columns: 1fr;
    }

    .playlist-creator {
        flex-direction: column;
    }
}
"""

# Component-specific styles
BUTTON_STYLES = {
    "primary": {
        "backgroundColor": "#0078d4",
        "color": "white",
        "border": "none",
        "borderRadius": "4px",
        "padding": "12px 24px",
        "fontSize": "16px",
        "fontWeight": "bold",
        "cursor": "pointer",
        "transition": "background-color 0.2s ease",
    },
    "secondary": {
        "backgroundColor": "#6c757d",
        "color": "white",
        "border": "none",
        "borderRadius": "4px",
        "padding": "10px 20px",
        "fontSize": "14px",
        "cursor": "pointer",
    },
}

CONTAINER_STYLES = {
    "main_layout": {
        "maxWidth": "1200px",
        "margin": "0 auto",
        "padding": "20px",
        "fontFamily": '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    },
    "controls_mobile": {
        "width": "100%",
        "padding": "15px",
        "marginBottom": "20px",
        "backgroundColor": "#f8f9fa",
        "borderRadius": "8px",
        "boxSizing": "border-box",
    },
    "results_mobile": {"width": "100%", "padding": "15px", "boxSizing": "border-box"},
}
