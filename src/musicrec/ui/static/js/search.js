/**
 * CSC111 Winter 2025: A Mood-Driven Music Recommender with Genre Hierarchies
 * 
 * Real-time search functionality with debounced input, keyboard navigation,
 * and accessible dropdown interface.
 * 
 * Copyright and Usage Information
 * ===============================
 * This file is Copyright (c) 2025 Qian (Angela) Su.
 */

class DebouncedSearch {
    /**
     * Initialize the debounced search functionality.
     *
     * @param {Object} options - Configuration options
     * @param {string} options.inputSelector - CSS selector for search input
     * @param {string} options.suggestionsSelector - CSS selector for suggestions container
     * @param {number} options.debounceDelay - Debounce delay in milliseconds (default: 300)
     * @param {number} options.minQueryLength - Minimum query length to trigger search (default: 3)
     * @param {Function} options.searchCallback - Function to call when performing search
     * @param {Function} options.selectionCallback - Function to call when item is selected
     */
    constructor(options = {}) {
        this.inputElement = document.querySelector(options.inputSelector);
        this.suggestionsElement = document.querySelector(options.suggestionsSelector);
        this.debounceDelay = options.debounceDelay || 300;
        this.minQueryLength = options.minQueryLength || 3;
        this.searchCallback = options.searchCallback || this.defaultSearchCallback.bind(this);
        this.selectionCallback = options.selectionCallback || this.defaultSelectionCallback.bind(this);

        this.debounceTimer = null;
        this.currentQuery = '';
        this.suggestions = [];
        this.selectedIndex = -1;
        this.isLoading = false;
        this.isVisible = false;

        this.init();
    }

    /**
     * Initialize event listeners and ARIA attributes.
     */
    init() {
        if (!this.inputElement) {
            console.warn('DebouncedSearch: Input element not found');
            return;
        }

        this.setupAccessibility();
        this.bindEvents();
    }

    /**
     * Setup ARIA attributes for accessibility.
     */
    setupAccessibility() {
        // Set up combobox role and attributes
        this.inputElement.setAttribute('role', 'combobox');
        this.inputElement.setAttribute('aria-autocomplete', 'list');
        this.inputElement.setAttribute('aria-expanded', 'false');

        if (this.suggestionsElement) {
            this.suggestionsElement.setAttribute('role', 'listbox');
            this.inputElement.setAttribute('aria-controls', this.suggestionsElement.id || 'search-suggestions');
        }
    }

    /**
     * Bind event listeners for input and keyboard navigation.
     */
    bindEvents() {
        // Input event for search
        this.inputElement.addEventListener('input', (e) => {
            this.handleInput(e.target.value);
        });

        // Keyboard navigation
        this.inputElement.addEventListener('keydown', (e) => {
            this.handleKeydown(e);
        });

        // Click outside to close suggestions
        document.addEventListener('click', (e) => {
            if (!this.inputElement.contains(e.target) &&
                !this.suggestionsElement?.contains(e.target)) {
                this.hideSuggestions();
            }
        });

        // Focus events
        this.inputElement.addEventListener('focus', () => {
            if (this.suggestions.length > 0) {
                this.showSuggestions();
            }
        });

        this.inputElement.addEventListener('blur', (e) => {
            // Delay hiding to allow for suggestion clicks
            setTimeout(() => {
                if (!this.suggestionsElement?.contains(document.activeElement)) {
                    this.hideSuggestions();
                }
            }, 150);
        });
    }

    /**
     * Handle input changes with debouncing.
     *
     * @param {string} value - Input value
     */
    handleInput(value) {
        this.currentQuery = value.trim();

        // Clear previous timer
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }

        // Reset selection
        this.selectedIndex = -1;

        // Handle empty input
        if (this.currentQuery.length === 0) {
            this.hideSuggestions();
            return;
        }

        // Handle short queries
        if (this.currentQuery.length < this.minQueryLength) {
            this.showMessage(`Type at least ${this.minQueryLength} characters to search`);
            return;
        }

        // Set up debounced search
        this.debounceTimer = setTimeout(() => {
            this.performSearch(this.currentQuery);
        }, this.debounceDelay);
    }

    /**
     * Handle keyboard navigation.
     *
     * @param {KeyboardEvent} e - Keyboard event
     */
    handleKeydown(e) {
        if (!this.isVisible || this.suggestions.length === 0) {
            return;
        }

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.moveSelection(1);
                break;

            case 'ArrowUp':
                e.preventDefault();
                this.moveSelection(-1);
                break;

            case 'Enter':
                e.preventDefault();
                if (this.selectedIndex >= 0) {
                    this.selectSuggestion(this.selectedIndex);
                }
                break;
            case 'Escape':
                e.preventDefault();
                this.hideSuggestions();
                break;
        }
    }

    /**
     * Move selection up or down in suggestions list.
     *
     * @param {number} direction - Direction to move (1 for down, -1 for up)
     */
    moveSelection(direction) {
        const newIndex = this.selectedIndex + direction;

        if (newIndex >= -1 && newIndex < this.suggestions.length) {
            this.selectedIndex = newIndex;
            this.updateSelection();
        }
    }

    /**
     * Update visual selection and ARIA attributes.
     */
    updateSelection() {
        const suggestionElements = this.suggestionsElement?.querySelectorAll('[role="option"]') || [];

        suggestionElements.forEach((element, index) => {
            const isSelected = index === this.selectedIndex;
            element.classList.toggle('selected', isSelected);
            element.setAttribute('aria-selected', isSelected.toString());
        });

        // Update aria-activedescendant
        if (this.selectedIndex >= 0 && suggestionElements[this.selectedIndex]) {
            const selectedId = suggestionElements[this.selectedIndex].id || `option-${this.selectedIndex}`;
            this.inputElement.setAttribute('aria-activedescendant', selectedId);
        } else {
            this.inputElement.removeAttribute('aria-activedescendant');
        }
    }

    /**
     * Perform search operation.
     *
     * @param {string} query - Search query
     */
    async performSearch(query) {
        try {
            this.setLoading(true);
            const results = await this.searchCallback(query);
            this.handleSearchResults(results);
        } catch (error) {
            console.error('Search error:', error);
            this.showMessage('Search failed. Please try again.');
        } finally {
            this.setLoading(false);
        }
    }

    /**
     * Handle search results.
     *
     * @param {Array} results - Search results
     */
    handleSearchResults(results) {
        this.suggestions = results || [];

        if (this.suggestions.length === 0) {
            this.showMessage('No results found');
        } else {
            this.renderSuggestions();
            this.showSuggestions();
        }
    }

    /**
     * Render suggestions list.
     */
    renderSuggestions() {
        if (!this.suggestionsElement) return;

        const listElement = document.createElement('ul');
        listElement.setAttribute('role', 'listbox');

        this.suggestions.forEach((suggestion, index) => {
            const listItem = document.createElement('li');
            listItem.setAttribute('role', 'option');
            listItem.setAttribute('id', `search-option-${index}`);
            listItem.className = 'search-suggestion';
            listItem.textContent = suggestion.label || suggestion.display_name || suggestion;

            // Click handler
            listItem.addEventListener('click', () => {
                this.selectSuggestion(index);
            });

            // Mouse hover
            listItem.addEventListener('mouseenter', () => {
                this.selectedIndex = index;
                this.updateSelection();
            });

            listElement.appendChild(listItem);
        });

        this.suggestionsElement.innerHTML = '';
        this.suggestionsElement.appendChild(listElement);
        this.updateSelection();
    }

    /**
     * Select a suggestion by index.
     *
     * @param {number} index - Suggestion index
     */
    selectSuggestion(index) {
        if (index >= 0 && index < this.suggestions.length) {
            const suggestion = this.suggestions[index];
            this.inputElement.value = suggestion.label || suggestion.display_name || suggestion;
            this.hideSuggestions();
            this.selectionCallback(suggestion);
        }
    }

    /**
     * Show suggestions dropdown.
     */
    showSuggestions() {
        if (!this.suggestionsElement) return;

        this.isVisible = true;
        this.suggestionsElement.style.display = 'block';
        this.inputElement.setAttribute('aria-expanded', 'true');
    }

    /**
     * Hide suggestions dropdown.
     */
    hideSuggestions() {
        if (!this.suggestionsElement) return;

        this.isVisible = false;
        this.suggestionsElement.style.display = 'none';
        this.inputElement.setAttribute('aria-expanded', 'false');
        this.inputElement.removeAttribute('aria-activedescendant');
        this.selectedIndex = -1;
    }

    /**
     * Show a message in the suggestions area.
     *
     * @param {string} message - Message to display
     */
    showMessage(message) {
        if (!this.suggestionsElement) return;

        this.suggestionsElement.innerHTML = `
            <div class="search-message" role="status" aria-live="polite">
                ${message}
            </div>
        `;
        this.showSuggestions();
    }

    /**
     * Set loading state.
     *
     * @param {boolean} loading - Loading state
     */
    setLoading(loading) {
        this.isLoading = loading;

        if (loading) {
            this.showMessage('Searching...');
        }
    }

    /**
     * Default search callback (to be overridden).
     *
     * @param {string} query - Search query
     * @returns {Promise<Array>} Search results
     */
    async defaultSearchCallback(query) {
        console.log('Default search callback called with query:', query);
        return [];
    }

    /**
     * Default selection callback (to be overridden).
     *
     * @param {Object} suggestion - Selected suggestion
     */
    defaultSelectionCallback(suggestion) {
        console.log('Default selection callback called with:', suggestion);
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DebouncedSearch;
} else if (typeof window !== 'undefined') {
    window.DebouncedSearch = DebouncedSearch;
}
