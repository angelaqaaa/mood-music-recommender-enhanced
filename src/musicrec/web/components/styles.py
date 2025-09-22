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

/* Dark mode specific component fixes */
[data-theme="dark"] .dash-tabs {
    background: var(--bg-secondary) !important;
    border-bottom: 1px solid var(--gray-200) !important;
}

[data-theme="dark"] .dash-tabs .tab {
    background: var(--bg-secondary) !important;
    color: var(--text-secondary) !important;
}

[data-theme="dark"] .dash-tabs .tab--selected {
    background: var(--bg-primary) !important;
    color: var(--primary-purple) !important;
}

[data-theme="dark"] .description-box {
    background: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
    border-color: var(--gray-200) !important;
}

[data-theme="dark"] .section-container {
    background: var(--bg-secondary) !important;
}

[data-theme="dark"] .user-features-section,
[data-theme="dark"] .discovery-section,
[data-theme="dark"] .playlists-section,
[data-theme="dark"] .favorites-section {
    background: var(--bg-secondary) !important;
    border-color: var(--gray-200) !important;
}

/* Let Plotly handle its own graph backgrounds - no CSS override */

/* Fix method description in dark mode */
[data-theme="dark"] .method-description {
    background: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
    border-color: var(--gray-200) !important;
}

/* Fix dropdown and input backgrounds */
[data-theme="dark"] .Select-control {
    background: var(--bg-secondary) !important;
    border-color: var(--gray-200) !important;
    color: var(--text-primary) !important;
}

[data-theme="dark"] .Select-menu-outer {
    background: var(--bg-secondary) !important;
    border-color: var(--gray-200) !important;
}

/* Fix specific white background elements */
[data-theme="dark"] .tab-content {
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

[data-theme="dark"] .dash-tabs .tab-selected {
    background: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
}

[data-theme="dark"] .dash-tabs .tab {
    background: var(--bg-tertiary) !important;
    color: var(--text-secondary) !important;
    border-color: var(--gray-200) !important;
}

[data-theme="dark"] .dash-table-container {
    background: var(--bg-secondary) !important;
}

/* Keep plotly plot containers transparent - let Plotly manage backgrounds */

[data-theme="dark"] .plotly text {
    fill: var(--text-primary) !important;
}

[data-theme="dark"] .plotly .xtick text,
[data-theme="dark"] .plotly .ytick text,
[data-theme="dark"] .plotly .legend text,
[data-theme="dark"] .plotly .axis text {
    fill: var(--text-primary) !important;
}

[data-theme="dark"] .plotly .xgrid,
[data-theme="dark"] .plotly .ygrid {
    stroke: var(--gray-200) !important;
}

/* Fix favorites and playlists visibility */
[data-theme="dark"] .favorites-container,
[data-theme="dark"] .playlist-container {
    background: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--gray-200) !important;
}

[data-theme="dark"] .playlist-item {
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    border-bottom: 1px solid var(--gray-200) !important;
}

[data-theme="dark"] .favorite-item {
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--gray-200) !important;
}

/* Fix mood journey section */
[data-theme="dark"] .mood-journey-container {
    background: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
}

/* Light mode mood journey background */
.mood-journey-container {
    background: rgba(240, 245, 250, 0.95) !important;
    border: 1px solid #e3f2fd !important;
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    margin: 1rem 0;
}

/* Enhanced light mode professional backgrounds */
body[data-theme="light"] .controls-container,
body[data-theme="light"] .results-container,
html[data-theme="light"] .controls-container,
html[data-theme="light"] .results-container {
    background: #FFFFFF !important;
    border: 1px solid rgba(148, 163, 184, 0.3) !important;
}

[data-theme="light"] .search-container,
[data-theme="light"] .visualization-section {
    background: rgba(248, 250, 252, 0.95) !important;
    border: 1px solid rgba(148, 163, 184, 0.3) !important;
}

[data-theme="light"] .mood-journey-container {
    background: rgba(240, 245, 250, 0.95) !important;
    color: var(--text-primary) !important;
    border: 1px solid #e3f2fd !important;
}

/* Enhanced light mode backgrounds */
:root {
    --mood-journey-bg-light: rgba(240, 245, 250, 0.95);
    --mood-journey-border-light: #e3f2fd;
}

[data-theme="light"] .visualization-section {
    background: rgba(248, 250, 252, 0.9) !important;
    border: 1px solid rgba(226, 232, 240, 0.8) !important;
    border-radius: var(--radius-lg);
}

[data-theme="dark"] .mood-journey-container h3,
[data-theme="dark"] .mood-journey-container h4,
[data-theme="dark"] .mood-journey-container p {
    color: var(--text-primary) !important;
}

/* Additional fixes for dark mode contrast */
[data-theme="dark"] {
    --bg-tertiary: #1a2332;
}

[data-theme="dark"] .user-features-section {
    color: var(--text-primary) !important;
}

[data-theme="dark"] .discovery-dashboard {
    color: var(--text-primary) !important;
}

/* Fix search and visualization row backgrounds */
[data-theme="dark"] .row {
    background: var(--bg-primary) !important;
}

[data-theme="dark"] .controls-container {
    background: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
}

[data-theme="dark"] .results-container {
    background: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
}

/* Fix specific section backgrounds */
[data-theme="dark"] .search-section,
[data-theme="dark"] .visualization-section {
    background: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
}

/* Fix form sections */
[data-theme="dark"] .form-section {
    background: transparent !important;
    color: var(--text-primary) !important;
}

[data-theme="dark"] .form-section h3 {
    color: var(--text-primary) !important;
}

/* Fix visualization and mood journey text specifically */
[data-theme="dark"] .visualization-content,
[data-theme="dark"] .mood-journey-content,
[data-theme="dark"] .visualization-section h3,
[data-theme="dark"] .mood-journey-section h3,
[data-theme="dark"] .visualization-section p,
[data-theme="dark"] .mood-journey-section p {
    color: var(--text-primary) !important;
}

/* Fix any remaining white backgrounds */
[data-theme="dark"] .main-container {
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

[data-theme="dark"] .app-container {
    background: var(--bg-primary) !important;
}

/* Fix column backgrounds */
[data-theme="dark"] .col,
[data-theme="dark"] .col-12,
[data-theme="dark"] .col-md-6,
[data-theme="dark"] .col-lg-4 {
    background: transparent !important;
}

/* Fix input and dropdown backgrounds */
[data-theme="dark"] .dash-dropdown,
[data-theme="dark"] input,
[data-theme="dark"] .form-control {
    background: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
    border-color: var(--gray-200) !important;
}

/* Force dark theme on all major containers */
[data-theme="dark"] div,
[data-theme="dark"] .container,
[data-theme="dark"] .container-fluid {
    background-color: transparent !important;
}

/* Force dark theme on body and html */
[data-theme="dark"] body,
[data-theme="dark"] html {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

/* Enhanced Professional Dark Mode */
[data-theme="dark"] {
    color-scheme: dark;
    --bg-primary: #0f172a;
    --bg-secondary: #1e293b;
    --bg-hover: #334155;
    --text-primary: #f1f5f9;
    --text-secondary: #cbd5e1;
    --border-color: #475569;
    --border-light: #64748b;
}

/* Improved background consistency */
[data-theme="dark"] body,
[data-theme="dark"] html,
[data-theme="dark"] #app-container {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

/* Remove problematic Plotly background overrides that cause uniform colors */
/* Let Plotly handle its own chart backgrounds and colors */

/* Fix plotly text colors in dark mode */
[data-theme="dark"] .plotly .xtitle,
[data-theme="dark"] .plotly .ytitle,
[data-theme="dark"] .plotly .g-xtitle,
[data-theme="dark"] .plotly .g-ytitle {
    fill: var(--text-primary) !important;
}

[data-theme="dark"] .plotly .tick text {
    fill: var(--text-secondary) !important;
}

[data-theme="dark"] .plotly .modebar {
    background-color: rgba(15, 23, 42, 0.9) !important;
    border: 1px solid rgba(71, 85, 105, 0.3) !important;
    border-radius: 6px !important;
}

[data-theme="dark"] .plotly .modebar-btn {
    color: var(--text-secondary) !important;
}

[data-theme="dark"] .plotly .modebar-btn:hover {
    background-color: rgba(51, 65, 85, 0.7) !important;
}

[data-theme="dark"] .plotly .modebar-btn svg {
    fill: var(--text-secondary) !important;
}

/* Enhanced container and component backgrounds */
[data-theme="dark"] .controls-container,
[data-theme="dark"] .section-container,
[data-theme="dark"] .recommendations-container,
[data-theme="dark"] .search-container {
    background-color: var(--bg-secondary) !important;
    border-color: var(--border-color) !important;
    color: var(--text-primary) !important;
}

[data-theme="dark"] .recommendation-card,
[data-theme="dark"] .search-result-item {
    background-color: var(--bg-hover) !important;
    border-color: var(--border-light) !important;
    color: var(--text-primary) !important;
}

/* Tab styling improvements */
[data-theme="dark"] .tab-container,
[data-theme="dark"] .tab-content {
    background-color: var(--bg-secondary) !important;
    border-color: var(--border-color) !important;
}

[data-theme="dark"] .tab {
    background-color: var(--bg-primary) !important;
    color: var(--text-secondary) !important;
    border-color: var(--border-color) !important;
}

[data-theme="dark"] .tab.tab--selected {
    background-color: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
    border-bottom-color: var(--primary-purple) !important;
}

/* Enhanced text visibility */
[data-theme="dark"] h1,
[data-theme="dark"] h2,
[data-theme="dark"] h3,
[data-theme="dark"] h4,
[data-theme="dark"] h5,
[data-theme="dark"] h6 {
    color: var(--text-primary) !important;
}

[data-theme="dark"] p,
[data-theme="dark"] span:not(.plotly *),
[data-theme="dark"] div:not(.js-plotly-plot):not(.plotly):not([class*="plotly"]) {
    color: var(--text-secondary) !important;
}

[data-theme="dark"] .section-title,
[data-theme="dark"] .subsection-title {
    color: var(--primary-purple) !important;
}

/* Dropdown and form improvements */
[data-theme="dark"] .dash-dropdown,
[data-theme="dark"] .Select-control,
[data-theme="dark"] .Select--single .Select-control {
    background-color: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
    border-color: var(--border-color) !important;
}

[data-theme="dark"] .Select-menu-outer,
[data-theme="dark"] .VirtualizedSelectFocusedOption,
[data-theme="dark"] .VirtualizedSelectOption {
    background-color: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
}

[data-theme="dark"] .VirtualizedSelectOption:hover,
[data-theme="dark"] .VirtualizedSelectFocusedOption {
    background-color: var(--bg-hover) !important;
}

[data-theme="dark"] .Select-placeholder,
[data-theme="dark"] .Select--single > .Select-control .Select-value {
    color: var(--text-secondary) !important;
}

/* Input field enhancements */
[data-theme="dark"] input,
[data-theme="dark"] textarea {
    background-color: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
    border-color: var(--border-color) !important;
}

[data-theme="dark"] input:focus,
[data-theme="dark"] textarea:focus {
    border-color: var(--primary-purple) !important;
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1) !important;
}

/* Button contrast improvements */
[data-theme="dark"] button:not(.play-playlist-btn):not(.delete-playlist-btn):not(.remove-track-btn) {
    background-color: var(--bg-hover) !important;
    color: var(--text-primary) !important;
    border-color: var(--border-color) !important;
}

[data-theme="dark"] button:hover:not(.play-playlist-btn):not(.delete-playlist-btn):not(.remove-track-btn) {
    background-color: var(--border-light) !important;
}

/* Better visibility for visualization text */
[data-theme="dark"] .visualization-container text {
    fill: var(--text-secondary) !important;
}

[data-theme="dark"] .visualization-title {
    color: var(--text-primary) !important;
}

/* Loading and empty state improvements */
[data-theme="dark"] .loading-spinner,
[data-theme="dark"] .empty-state {
    color: var(--text-secondary) !important;
}

/* Enhanced playlist dropdown specific styling */
[data-theme="dark"] .playlist-dropdown {
    background-color: var(--bg-secondary) !important;
    border-color: var(--border-color) !important;
}

/* Table improvements */
[data-theme="dark"] .dash-table-container table {
    background-color: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
}

[data-theme="dark"] .dash-table-container .dash-cell {
    background-color: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
    border-color: var(--border-color) !important;
}

/* Dark mode input and number input styling - exclude ALL dropdown-related inputs */
[data-theme="dark"] .numeric-input input {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 6px;
    padding: 8px 12px;
}

[data-theme="dark"] .numeric-input input:focus {
    outline: none !important;
    border-color: var(--primary-purple) !important;
    box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2) !important;
}

/* Completely remove visible styling from inputs inside dropdowns/selects */
[data-theme="dark"] .Select input,
[data-theme="dark"] .dash-dropdown input,
[data-theme="dark"] .Select-input input,
[data-theme="dark"] .Select-control input {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
    padding: 0 !important;
    margin: 0 !important;
    opacity: 0 !important;
    position: absolute !important;
    z-index: -1 !important;
}

/* Dark mode dropdown styling */
[data-theme="dark"] .Select,
[data-theme="dark"] .dash-dropdown,
[data-theme="dark"] .Select-control {
    background-color: var(--bg-primary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 6px !important;
    box-shadow: none !important;
}

/* Remove black shadow/container behind dropdowns */
[data-theme="dark"] .dash-dropdown div,
[data-theme="dark"] .Select div,
[data-theme="dark"] .dash-dropdown *,
[data-theme="dark"] .Select * {
    box-shadow: none !important;
    border-radius: 6px !important;
}

/* Specifically target playlist dropdowns in track results */
[data-theme="dark"] .track-item .dash-dropdown,
[data-theme="dark"] .track-item .Select,
[data-theme="dark"] .track-item .dash-dropdown div,
[data-theme="dark"] .track-item .Select div,
[data-theme="dark"] .track-item .dash-dropdown *,
[data-theme="dark"] .track-item .Select * {
    box-shadow: none !important;
    background-color: var(--bg-primary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 6px !important;
}

/* Nuclear option - remove all shadows and force transparent backgrounds */
[data-theme="dark"] * {
    box-shadow: none !important;
}

/* Force transparent/matching backgrounds on ALL dropdown elements */
[data-theme="dark"] .dash-dropdown,
[data-theme="dark"] .Select,
[data-theme="dark"] .dash-dropdown *,
[data-theme="dark"] .Select *,
[data-theme="dark"] .dash-dropdown > div,
[data-theme="dark"] .Select > div,
[data-theme="dark"] .dash-dropdown .Select-control,
[data-theme="dark"] .dash-dropdown .dropdown,
[data-theme="dark"] .dropdown-container,
[data-theme="dark"] .VirtualizedSelect,
[data-theme="dark"] .VirtualizedSelectOption {
    background-color: transparent !important;
    background: transparent !important;
    box-shadow: none !important;
    border: none !important;
}

/* Only apply styling to the outermost dropdown container */
[data-theme="dark"] .dash-dropdown {
    background-color: var(--bg-primary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 6px !important;
    min-height: auto !important;
    height: auto !important;
}

/* Fix dropdown control height and padding */
[data-theme="dark"] .dash-dropdown .Select-control {
    min-height: 32px !important;
    height: 32px !important;
    padding: 4px 8px !important;
    background-color: var(--bg-primary) !important;
    border: none !important;
}

/* Fix dropdown menu background to be visible */
[data-theme="dark"] .dash-dropdown .Select-menu-outer,
[data-theme="dark"] .dash-dropdown .VirtualizedSelectMenu {
    background-color: var(--bg-primary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 6px !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
}

/* Ensure all dropdown containers have consistent rounded borders */
[data-theme="dark"] .dash-dropdown .Select-control,
[data-theme="dark"] .dash-dropdown .VirtualizedSelectFocusedOption,
[data-theme="dark"] .dash-dropdown .VirtualizedSelectOption {
    border-radius: 6px !important;
    box-shadow: none !important;
}

[data-theme="dark"] .Select-input,
[data-theme="dark"] .Select-input input {
    background-color: transparent !important;
    border: none !important;
    outline: none !important;
    color: var(--text-primary) !important;
    box-shadow: none !important;
}

/* Scrollable dropdown menu styling - more aggressive approach */
.playlist-dropdown .Select-menu-outer,
.playlist-dropdown .Select-menu,
.playlist-dropdown .VirtualizedSelectMenu,
.playlist-dropdown .ReactVirtualized__Grid,
.playlist-dropdown .ReactVirtualized__List,
.dash-dropdown .Select-menu-outer,
.dash-dropdown .Select-menu,
.dash-dropdown .VirtualizedSelectMenu,
.dash-dropdown .ReactVirtualized__Grid,
.dash-dropdown .ReactVirtualized__List {
    max-height: 200px !important;
    overflow-y: auto !important;
    z-index: 99999 !important;
    position: relative !important;
}

/* Fix z-index for playlist dropdown containers */
.playlist-dropdown,
.playlist-dropdown .dash-dropdown {
    position: relative !important;
    z-index: 99999 !important;
}

/* Ensure track result containers don't interfere with dropdown layering */
.track-result,
.track-item,
.recommendation-item {
    position: relative !important;
    z-index: 1 !important;
    overflow: visible !important;
}

/* Fix the track box that contains the dropdown */
.track-result:has(.playlist-dropdown),
.track-item:has(.playlist-dropdown),
.recommendation-item:has(.playlist-dropdown) {
    overflow: visible !important;
    z-index: 999998 !important;
}

/* Alternative approach for browsers without :has support */
.track-result,
.track-item,
.recommendation-item {
    overflow: visible !important;
}

/* The actual track container styling */
.track-container,
.rec-item,
.recommendation-box {
    overflow: visible !important;
    position: relative !important;
}

/* When dropdown is open, boost its container z-index */
.playlist-dropdown:focus-within,
.playlist-dropdown .Select--is-open {
    z-index: 999999 !important;
}

/* Fix parent containers that might clip dropdowns */
.recommendations-results,
.track-results,
.results-container,
.recommendations-container {
    overflow: visible !important;
    position: relative !important;
}

/* Specifically target the recommendation items */
.recommendation-item {
    overflow: visible !important;
    position: relative !important;
    z-index: 1 !important;
}

/* When a recommendation item contains an open dropdown */
.recommendation-item:has(.Select--is-open) {
    z-index: 999998 !important;
    overflow: visible !important;
}

/* Force dropdown to break out completely - portal approach */
.playlist-dropdown .Select-menu-outer {
    position: absolute !important;
    top: 100% !important;
    left: 0 !important;
    z-index: 999999 !important;
    background: var(--bg-primary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 4px !important;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2) !important;
    width: 150px !important;
    max-height: 200px !important;
    overflow-y: auto !important;
    /* Force it to render on top layer */
    transform: translateZ(0) !important;
    will-change: transform !important;
}

/* Create a new stacking context */
.playlist-dropdown {
    transform: translateZ(0) !important;
    position: relative !important;
    z-index: 999999 !important;
}

/* When dropdown is open, portal it to body */
.playlist-dropdown .Select--is-open .Select-menu-outer {
    position: fixed !important;
    z-index: 9999999 !important;
    transform: translateZ(999px) !important;
    /* Try to position relative to viewport */
    top: auto !important;
    left: auto !important;
    /* Calculate position using CSS custom properties if possible */
}

/* Alternative approach - make dropdown escape container bounds */
.playlist-dropdown .Select-menu-outer {
    /* Force it out of container flow */
    position: absolute !important;
    top: 100% !important;
    left: 0 !important;
    /* Use contain to create new containing block */
    contain: layout style !important;
}

/* Nuclear option - force ALL parent containers to be visible */
body * {
    /* Only target containers that might clip dropdowns */
}

.recommendation-item * {
    overflow: visible !important;
}

/* Force any element containing a dropdown to not clip */
*:has(.playlist-dropdown) {
    overflow: visible !important;
    clip: none !important;
    clip-path: none !important;
}

/* Fallback for browsers without :has */
.recommendation-item,
.recommendation-item > *,
.recommendation-item > * > * {
    overflow: visible !important;
    clip: none !important;
    clip-path: none !important;
}

/* Nuclear option - force scrolling on ALL dropdown-related containers */
.playlist-dropdown div[style*="overflow: hidden"],
.dash-dropdown div[style*="overflow: hidden"] {
    overflow: auto !important;
    max-height: 200px !important;
}

.playlist-dropdown div[style*="height:"],
.dash-dropdown div[style*="height:"] {
    max-height: 200px !important;
    overflow-y: auto !important;
}

/* Force override inline styles on virtualized components */
.playlist-dropdown .ReactVirtualized__Grid.VirtualSelectGrid,
.dash-dropdown .ReactVirtualized__Grid.VirtualSelectGrid {
    overflow: auto !important;
    height: auto !important;
    max-height: 200px !important;
}

.playlist-dropdown .ReactVirtualized__Grid__innerScrollContainer,
.dash-dropdown .ReactVirtualized__Grid__innerScrollContainer {
    overflow: visible !important;
    max-height: none !important;
}

/* Custom scrollbar for dropdown menus */
.playlist-dropdown .Select-menu-outer::-webkit-scrollbar,
.playlist-dropdown .VirtualizedSelectMenu::-webkit-scrollbar,
.playlist-dropdown .ReactVirtualized__Grid::-webkit-scrollbar,
.dash-dropdown .Select-menu-outer::-webkit-scrollbar,
.dash-dropdown .VirtualizedSelectMenu::-webkit-scrollbar,
.dash-dropdown .ReactVirtualized__Grid::-webkit-scrollbar {
    width: 6px;
}

.playlist-dropdown .Select-menu-outer::-webkit-scrollbar-track,
.playlist-dropdown .VirtualizedSelectMenu::-webkit-scrollbar-track,
.playlist-dropdown .ReactVirtualized__Grid::-webkit-scrollbar-track,
.dash-dropdown .Select-menu-outer::-webkit-scrollbar-track,
.dash-dropdown .VirtualizedSelectMenu::-webkit-scrollbar-track,
.dash-dropdown .ReactVirtualized__Grid::-webkit-scrollbar-track {
    background: var(--bg-secondary);
    border-radius: 3px;
}

.playlist-dropdown .Select-menu-outer::-webkit-scrollbar-thumb,
.playlist-dropdown .VirtualizedSelectMenu::-webkit-scrollbar-thumb,
.playlist-dropdown .ReactVirtualized__Grid::-webkit-scrollbar-thumb,
.dash-dropdown .Select-menu-outer::-webkit-scrollbar-thumb,
.dash-dropdown .VirtualizedSelectMenu::-webkit-scrollbar-thumb,
.dash-dropdown .ReactVirtualized__Grid::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: 3px;
}

.playlist-dropdown .Select-menu-outer::-webkit-scrollbar-thumb:hover,
.playlist-dropdown .VirtualizedSelectMenu::-webkit-scrollbar-thumb:hover,
.playlist-dropdown .ReactVirtualized__Grid::-webkit-scrollbar-thumb:hover,
.dash-dropdown .Select-menu-outer::-webkit-scrollbar-thumb:hover,
.dash-dropdown .VirtualizedSelectMenu::-webkit-scrollbar-thumb:hover,
.dash-dropdown .ReactVirtualized__Grid::-webkit-scrollbar-thumb:hover {
    background: var(--primary-purple);
}

/* Dark theme scrollbar colors */
[data-theme="dark"] .playlist-dropdown .Select-menu-outer::-webkit-scrollbar-track,
[data-theme="dark"] .playlist-dropdown .VirtualizedSelectMenu::-webkit-scrollbar-track,
[data-theme="dark"] .playlist-dropdown .ReactVirtualized__Grid::-webkit-scrollbar-track,
[data-theme="dark"] .dash-dropdown .Select-menu-outer::-webkit-scrollbar-track,
[data-theme="dark"] .dash-dropdown .VirtualizedSelectMenu::-webkit-scrollbar-track,
[data-theme="dark"] .dash-dropdown .ReactVirtualized__Grid::-webkit-scrollbar-track {
    background: rgba(55, 65, 81, 0.5);
}

[data-theme="dark"] .playlist-dropdown .Select-menu-outer::-webkit-scrollbar-thumb,
[data-theme="dark"] .playlist-dropdown .VirtualizedSelectMenu::-webkit-scrollbar-thumb,
[data-theme="dark"] .playlist-dropdown .ReactVirtualized__Grid::-webkit-scrollbar-thumb,
[data-theme="dark"] .dash-dropdown .Select-menu-outer::-webkit-scrollbar-thumb,
[data-theme="dark"] .dash-dropdown .VirtualizedSelectMenu::-webkit-scrollbar-thumb,
[data-theme="dark"] .dash-dropdown .ReactVirtualized__Grid::-webkit-scrollbar-thumb {
    background: rgba(156, 163, 175, 0.6);
}

[data-theme="dark"] .playlist-dropdown .Select-menu-outer::-webkit-scrollbar-thumb:hover,
[data-theme="dark"] .playlist-dropdown .VirtualizedSelectMenu::-webkit-scrollbar-thumb:hover,
[data-theme="dark"] .playlist-dropdown .ReactVirtualized__Grid::-webkit-scrollbar-thumb:hover,
[data-theme="dark"] .dash-dropdown .Select-menu-outer::-webkit-scrollbar-thumb:hover,
[data-theme="dark"] .dash-dropdown .VirtualizedSelectMenu::-webkit-scrollbar-thumb:hover,
[data-theme="dark"] .dash-dropdown .ReactVirtualized__Grid::-webkit-scrollbar-thumb:hover {
    background: var(--primary-purple);
}

[data-theme="dark"] .Select-placeholder,
[data-theme="dark"] .Select-value {
    color: var(--text-primary) !important;
}

[data-theme="dark"] .Select-arrow-zone,
[data-theme="dark"] .Select-arrow {
    color: var(--text-secondary) !important;
    border-color: var(--text-secondary) transparent transparent !important;
}

[data-theme="dark"] .Select-menu-outer {
    background-color: var(--bg-primary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 6px !important;
}

[data-theme="dark"] .Select-option {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

[data-theme="dark"] .Select-option:hover,
[data-theme="dark"] .Select-option.is-focused {
    background-color: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
}

[data-theme="dark"] .Select-option.is-selected {
    background-color: var(--primary-purple) !important;
    color: white !important;
}

[data-theme="dark"] .Select--is-focused .Select-control {
    border-color: var(--primary-purple) !important;
    box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2) !important;
}

/* Dark mode slider styling - refined and elegant */
[data-theme="dark"] .rc-slider {
    background-color: transparent !important;
}

[data-theme="dark"] .rc-slider-rail {
    background-color: var(--gray-500) !important;
    height: 3px !important;
    border-radius: 2px !important;
}

[data-theme="dark"] .rc-slider-track {
    background: linear-gradient(90deg, var(--primary-purple), var(--primary-purple-light)) !important;
    height: 3px !important;
    border-radius: 2px !important;
}

[data-theme="dark"] .rc-slider-handle {
    background-color: white !important;
    border: 2px solid var(--primary-purple) !important;
    box-shadow: 0 2px 6px rgba(139, 92, 246, 0.3) !important;
    width: 16px !important;
    height: 16px !important;
    margin-top: -7px !important;
}

[data-theme="dark"] .rc-slider-handle:hover {
    border-color: var(--primary-purple-light) !important;
    background-color: white !important;
    transform: scale(1.1) !important;
    box-shadow: 0 3px 8px rgba(139, 92, 246, 0.4) !important;
}

[data-theme="dark"] .rc-slider-handle:focus {
    border-color: var(--primary-purple-light) !important;
    background-color: white !important;
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.2), 0 2px 6px rgba(139, 92, 246, 0.3) !important;
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
    min-height: 800px;
    height: fit-content;
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
    min-height: 800px;
    height: fit-content;
    display: flex;
    flex-direction: column;
}

/* Enhanced Recommendation Cards */
.recommendations-container {
    max-height: 700px;
    overflow-y: auto;
    padding-right: 8px;
}

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

/* Final attempt - force dropdown completely out of container */
.playlist-dropdown .Select--is-open .Select-menu-outer {
    position: fixed !important;
    z-index: 999999999 !important;
    max-height: 200px !important;
    overflow-y: auto !important;
    width: 150px !important;
    background: var(--bg-primary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 4px !important;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2) !important;
}

/* Force recommendation item containing open dropdown to not clip */
.recommendation-item:has(.Select--is-open) {
    overflow: visible !important;
    z-index: 999999 !important;
    position: relative !important;
}

/* Nuclear option - any container with open select should not clip */
*:has(.Select--is-open) {
    overflow: visible !important;
}

/* Force all parent containers to be visible when dropdown is open */
body:has(.Select--is-open) * {
    overflow: visible !important;
}

/* Alternative approach - use CSS transform to move dropdown */
.playlist-dropdown .Select--is-open .Select-menu-outer {
    transform: translateZ(1000px) !important;
    isolation: isolate !important;
}

/* Target the exact problematic elements from the HTML structure */
.playlist-dropdown .ReactVirtualized__Grid__innerScrollContainer {
    overflow: visible !important;
    max-height: none !important;
    height: auto !important;
}

.playlist-dropdown .ReactVirtualized__Grid.VirtualSelectGrid {
    overflow: auto !important;
    max-height: 200px !important;
    height: auto !important;
}

.playlist-dropdown .Select-menu {
    overflow: visible !important;
    position: static !important;
}

/* Force override all inline styles that cause overflow hidden */
.playlist-dropdown .Select--is-open [style*="overflow: hidden"] {
    overflow: visible !important;
}

.playlist-dropdown .Select--is-open [style*="height: 210px"] {
    height: auto !important;
    max-height: 200px !important;
}

/* Add a portal target for dropdowns */
#dropdown-portal {
    position: fixed;
    top: 0;
    left: 0;
    z-index: 999999999;
    pointer-events: none;
}

#dropdown-portal > * {
    pointer-events: auto;
}

/* Enhanced support for Dash native menuPortalTarget="body" approach */
.Select__menu-portal {
    z-index: 999999999 !important;
}

.Select__menu-portal .Select__menu {
    background: white !important;
    border: 1px solid #ccc !important;
    border-radius: 4px !important;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15) !important;
    max-height: 200px !important;
    overflow-y: auto !important;
    z-index: 999999999 !important;
}

/* Dark theme support for portaled menus */
[data-theme="dark"] .Select__menu-portal .Select__menu {
    background: var(--bg-secondary) !important;
    border-color: var(--border-color) !important;
    color: var(--text-primary) !important;
}

/* Support React-Select v5+ portal classes */
.react-select__menu-portal {
    z-index: 999999999 !important;
}

.react-select__menu {
    z-index: 999999999 !important;
    max-height: 200px !important;
    overflow-y: auto !important;
}

/* Dash component portaling support */
div[id*="menu-portal"] {
    z-index: 999999999 !important;
}

/* Ensure the playlist dropdown control itself is properly styled */
.playlist-dropdown .Select__control {
    border: 1px solid #ccc !important;
    border-radius: 4px !important;
    min-height: 32px !important;
}

[data-theme="dark"] .playlist-dropdown .Select__control {
    background: var(--bg-secondary) !important;
    border-color: var(--border-color) !important;
    color: var(--text-primary) !important;
}

/* Playlist dropdown functionality removed */

/* FINAL OVERRIDE: Fix track list to fill recommendation panel properly */
.recommendations-container {
    min-height: 700px !important;
    max-height: 800px !important;
    overflow-y: auto !important;
    overflow-x: visible !important;
    border-bottom: 2px solid #ddd !important;
}

#recommendations-table,
#recommendations-list {
    min-height: 700px !important;
    max-height: 800px !important;
    overflow-y: auto !important;
    overflow-x: visible !important;
}

/* Fix recommendation items sizing and spacing */
.recommendation-item {
    box-sizing: border-box !important;
    max-width: 100% !important;
    margin-bottom: 20px !important;
    padding: 20px !important;
    font-size: 16px !important;
    word-wrap: break-word !important;
}

/* Fix overall application zoom/sizing - comprehensive fix */
html {
    zoom: 1.0 !important;
    font-size: 16px !important;
    -webkit-text-size-adjust: 100% !important;
    -moz-text-size-adjust: 100% !important;
    -ms-text-size-adjust: 100% !important;
}

body {
    zoom: 1.0 !important;
    transform: scale(1.0) !important;
    font-size: 16px !important;
    min-width: 100% !important;
    width: 100% !important;
}

.main-container {
    zoom: 1.0 !important;
    transform: scale(1.0) !important;
    font-size: 16px !important;
    width: 100% !important;
    max-width: none !important;
    min-width: 100% !important;
}

/* Force all text elements to normal size */
h1, h2, h3, h4, h5, h6, p, span, div {
    zoom: 1.0 !important;
    font-size: inherit !important;
}

/* Fix buttons and controls */
button, input, select, textarea {
    zoom: 1.0 !important;
    font-size: 14px !important;
}
"""


# Add JavaScript function to create dropdown portal
def add_dropdown_portal_script():
    return """
    <script>
    (function() {
        let portalContainer = null;

        function createPortalContainer() {
            if (!portalContainer) {
                portalContainer = document.createElement('div');
                portalContainer.id = 'dropdown-portal';
                portalContainer.style.cssText = 'position: fixed; top: 0; left: 0; z-index: 999999999; pointer-events: none;';
                document.body.appendChild(portalContainer);
            }
            return portalContainer;
        }

        function moveDropdownToPortal(dropdown) {
            const menuOuter = dropdown.querySelector('.Select-menu-outer');
            if (menuOuter && !menuOuter.dataset.portaled) {
                const rect = dropdown.getBoundingClientRect();
                const portal = createPortalContainer();

                // Clone the menu and position it
                const clone = menuOuter.cloneNode(true);
                clone.style.cssText = `
                    position: fixed !important;
                    top: ${rect.bottom + 2}px !important;
                    left: ${rect.left}px !important;
                    width: 150px !important;
                    max-height: 200px !important;
                    overflow-y: auto !important;
                    z-index: 999999999 !important;
                    background: var(--bg-primary) !important;
                    border: 1px solid var(--border-color) !important;
                    border-radius: 4px !important;
                    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2) !important;
                    pointer-events: auto !important;
                `;

                // Hide original and show clone
                menuOuter.style.display = 'none';
                menuOuter.dataset.portaled = 'true';
                portal.appendChild(clone);

                // Handle clicks on clone
                clone.addEventListener('click', function(e) {
                    const target = e.target.closest('.VirtualizedSelectOption');
                    if (target) {
                        const originalOption = menuOuter.querySelector('.VirtualizedSelectOption[style*="top: ' + target.style.top + '"]');
                        if (originalOption) {
                            originalOption.click();
                        }
                    }
                });

                // Store reference for cleanup
                dropdown.dataset.cloneId = clone.id = 'dropdown-clone-' + Date.now();
            }
        }

        function cleanupDropdowns() {
            const closedDropdowns = document.querySelectorAll('.playlist-dropdown:not(.Select--is-open) [data-portaled]');
            closedDropdowns.forEach(menu => {
                const dropdown = menu.closest('.playlist-dropdown');
                const cloneId = dropdown.dataset.cloneId;
                if (cloneId) {
                    const clone = document.getElementById(cloneId);
                    if (clone) clone.remove();
                    delete dropdown.dataset.cloneId;
                    menu.style.display = '';
                    delete menu.dataset.portaled;
                }
            });
        }

        function handleDropdowns() {
            // Move open dropdowns to portal
            const openDropdowns = document.querySelectorAll('.playlist-dropdown.Select--is-open');
            openDropdowns.forEach(moveDropdownToPortal);

            // Clean up closed dropdowns
            cleanupDropdowns();
        }

        // Set up observer
        const observer = new MutationObserver(handleDropdowns);
        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['class']
        });

        // Initial check
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', handleDropdowns);
        } else {
            handleDropdowns();
        }
    })();
    </script>
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
