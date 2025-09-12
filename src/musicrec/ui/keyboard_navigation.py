"""Client-side JavaScript for keyboard navigation and focus management."""

# JavaScript code for keyboard navigation
KEYBOARD_NAVIGATION_JS = """
window.dash_clientside = Object.assign({}, window.dash_clientside, {
    keyboard: {
        // Handle keyboard navigation for recommendation cards
        handleKeyboardNavigation: function(n_clicks, current_recommendations) {
            if (!current_recommendations || current_recommendations.length === 0) {
                return window.dash_clientside.no_update;
            }
            
            // Initialize keyboard navigation on first load
            if (!window.keyboard_nav_initialized) {
                initializeKeyboardNavigation();
                window.keyboard_nav_initialized = true;
            }
            
            return window.dash_clientside.no_update;
        },
        
        // Focus the first recommendation card
        focusFirstRecommendation: function(recommendations_data) {
            if (!recommendations_data || recommendations_data.length === 0) {
                return window.dash_clientside.no_update;
            }
            
            // Small delay to ensure DOM is updated
            setTimeout(() => {
                const firstCard = document.querySelector('.recommendation-item[tabindex="0"]');
                if (firstCard) {
                    firstCard.focus();
                    firstCard.setAttribute('aria-selected', 'true');
                }
            }, 100);
            
            return window.dash_clientside.no_update;
        }
    }
});

// Initialize keyboard navigation system
function initializeKeyboardNavigation() {
    let currentFocusIndex = 0;
    let cards = [];
    
    function updateCards() {
        cards = Array.from(document.querySelectorAll('.recommendation-item'));
        cards.forEach((card, index) => {
            card.setAttribute('data-index', index);
            card.setAttribute('role', 'option');
            card.setAttribute('aria-selected', 'false');
        });
    }
    
    function focusCard(index) {
        if (cards.length === 0) return;
        
        // Clear previous selection
        cards.forEach(card => {
            card.setAttribute('aria-selected', 'false');
            card.classList.remove('focused');
        });
        
        // Set new selection
        const targetIndex = ((index % cards.length) + cards.length) % cards.length;
        currentFocusIndex = targetIndex;
        
        const targetCard = cards[targetIndex];
        if (targetCard) {
            targetCard.focus();
            targetCard.setAttribute('aria-selected', 'true');
            targetCard.classList.add('focused');
            
            // Ensure card is visible
            targetCard.scrollIntoView({
                behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
                block: 'nearest'
            });
        }
    }
    
    function activateCard(card) {
        // Find and click the "Find Similar" button
        const button = card.querySelector('button[id*="track-button"]');
        if (button) {
            button.click();
            return true;
        }
        return false;
    }
    
    // Global keyboard event listener
    document.addEventListener('keydown', (event) => {
        // Only handle keyboard navigation when focus is on recommendations
        const activeElement = document.activeElement;
        if (!activeElement || !activeElement.closest('.recommendation-item')) {
            return;
        }
        
        updateCards();
        if (cards.length === 0) return;
        
        let handled = false;
        
        switch (event.key) {
            case 'ArrowDown':
            case 'ArrowRight':
                event.preventDefault();
                focusCard(currentFocusIndex + 1);
                handled = true;
                break;
                
            case 'ArrowUp':
            case 'ArrowLeft':
                event.preventDefault();
                focusCard(currentFocusIndex - 1);
                handled = true;
                break;
                
            case 'Home':
                event.preventDefault();
                focusCard(0);
                handled = true;
                break;
                
            case 'End':
                event.preventDefault();
                focusCard(cards.length - 1);
                handled = true;
                break;
                
            case 'Enter':
            case ' ':
                event.preventDefault();
                const currentCard = cards[currentFocusIndex];
                if (currentCard && activateCard(currentCard)) {
                    // Announce activation to screen readers
                    const announcement = document.createElement('div');
                    announcement.setAttribute('aria-live', 'polite');
                    announcement.setAttribute('aria-atomic', 'true');
                    announcement.style.position = 'absolute';
                    announcement.style.left = '-10000px';
                    announcement.textContent = 'Finding similar tracks...';
                    document.body.appendChild(announcement);
                    setTimeout(() => document.body.removeChild(announcement), 1000);
                }
                handled = true;
                break;
                
            case 'Escape':
                event.preventDefault();
                // Remove focus from recommendations
                const firstFocusable = document.querySelector('#search-button, .dash-dropdown input');
                if (firstFocusable) {
                    firstFocusable.focus();
                }
                handled = true;
                break;
        }
        
        if (handled) {
            event.stopPropagation();
        }
    });
    
    // Focus management when new recommendations load
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList' && 
                mutation.target.classList?.contains('recommendations-container')) {
                updateCards();
                if (cards.length > 0) {
                    setTimeout(() => focusCard(0), 150);
                }
            }
        });
    });
    
    // Start observing
    const container = document.querySelector('#recommendations-table');
    if (container) {
        observer.observe(container, {
            childList: true,
            subtree: true
        });
    }
}

// Additional CSS for focus indicators (to be injected)
const FOCUS_STYLES = `
.recommendation-item.focused {
    outline: 3px solid #0078d4 !important;
    outline-offset: 2px !important;
    box-shadow: 0 0 8px rgba(0, 120, 212, 0.3) !important;
}

.recommendation-item:focus {
    outline: 2px solid #0078d4 !important;
    outline-offset: 2px !important;
}

@media (prefers-contrast: high) {
    .recommendation-item.focused,
    .recommendation-item:focus {
        outline: 3px solid #fff !important;
        box-shadow: 0 0 0 1px #000, 0 0 0 4px #fff !important;
    }
}

@media (prefers-reduced-motion: reduce) {
    .recommendation-item {
        transition: none !important;
    }
}
`;

// Add focus styles to the page
if (typeof document !== 'undefined') {
    const styleElement = document.createElement('style');
    styleElement.textContent = FOCUS_STYLES;
    document.head.appendChild(styleElement);
}
"""


# Python utility functions for extracting testable logic
def get_keyboard_navigation_config():
    """Get configuration for keyboard navigation behavior."""
    return {
        "wrap_around": True,
        "focus_first_on_load": True,
        "respect_reduced_motion": True,
        "announce_actions": True,
        "escape_unfocus": True,
    }


def get_navigation_keys():
    """Get the keys used for navigation."""
    return {
        "next": ["ArrowDown", "ArrowRight"],
        "previous": ["ArrowUp", "ArrowLeft"],
        "first": ["Home"],
        "last": ["End"],
        "activate": ["Enter", " "],
        "escape": ["Escape"],
    }
