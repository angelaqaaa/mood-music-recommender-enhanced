"""CSS styles for responsive Dash UI components.

This module contains CSS styles for making the music recommender UI responsive
across mobile, tablet, and desktop devices.
"""

# Base responsive styles for the main layout
RESPONSIVE_STYLES = """
/* Base styles for all devices */
.main-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.controls-container {
    width: 100%;
    padding: 15px;
    box-sizing: border-box;
}

.results-container {
    width: 100%;
    padding: 15px;
    box-sizing: border-box;
}

.recommendation-item {
    padding: 15px;
    margin-bottom: 10px;
    border: 1px solid #ddd;
    border-radius: 8px;
    background-color: #f9f9f9;
}

.recommendation-item:hover {
    background-color: #f0f0f0;
    border-color: #ccc;
}

.recommendation-item:focus-within {
    outline: 2px solid #0078d4;
    outline-offset: 2px;
}

.recommendation-title {
    font-weight: bold;
    font-size: 1.1em;
    color: #333;
    margin-bottom: 5px;
}

.recommendation-details {
    color: #666;
    font-size: 0.95em;
    margin-bottom: 8px;
}

.recommendation-explanation {
    font-size: 0.9em;
    color: #555;
    font-style: italic;
    margin-top: 8px;
    padding: 8px;
    background-color: #f5f5f5;
    border-radius: 4px;
    border-left: 3px solid #0078d4;
}

.loading-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
    color: #666;
}

.loading-spinner {
    width: 20px;
    height: 20px;
    border: 2px solid #f3f3f3;
    border-top: 2px solid #0078d4;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-right: 10px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
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

/* Tablet styles */
@media (min-width: 768px) {
    .main-layout {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
    }
    
    .controls-container {
        width: 35%;
        min-width: 300px;
    }
    
    .results-container {
        width: 60%;
        flex: 1;
    }
    
    .recommendation-item {
        padding: 20px;
    }
    
    .metrics-panel {
        position: sticky;
        top: 20px;
    }
}

/* Desktop styles */
@media (min-width: 1024px) {
    .controls-container {
        width: 30%;
    }
    
    .results-container {
        width: 65%;
    }
    
    .main-container {
        padding: 30px;
    }
    
    .recommendation-item {
        padding: 25px;
    }
    
    .metrics-grid {
        grid-template-columns: repeat(4, 1fr);
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
