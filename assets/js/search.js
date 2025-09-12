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
     * Initialize debounced search component
     * @param {string} inputId - ID of the search input element
     * @param {string} containerId - ID of the search container element
     * @param {Object} options - Configuration options
     */
    constructor(inputId, containerId, options = {}) {
        this.inputId = inputId;
        this.containerId = containerId;
        this.options = {
            debounceDelay: options.debounceDelay || 300,
            minQueryLength: options.minQueryLength || 3,
            maxResults: options.maxResults || 20,
            onSearch: options.onSearch || (() => {}),
            onSelect: options.onSelect || (() => {}),
            onEmpty: options.onEmpty || (() => {}),
            ...options
        };
        
        this.searchTimeout = null;
        this.currentQuery = '';
        this.selectedIndex = -1;
        this.suggestions = [];
        this.isLoading = false;
        this.isOpen = false;
        
        this.init();
    }
    
    /**
     * Initialize the search component
     */
    init() {
        this.inputElement = document.getElementById(this.inputId);
        this.containerElement = document.getElementById(this.containerId);
        
        if (!this.inputElement || !this.containerElement) {
            console.error('Search elements not found:', this.inputId, this.containerId);
            return;
        }
        
        this.setupEventListeners();
        this.setupAccessibility();
    }
    
    /**
     * Set up event listeners for search functionality
     */
    setupEventListeners() {
        // Input events
        this.inputElement.addEventListener('input', (e) => {
            this.handleInput(e.target.value);
        });
        
        this.inputElement.addEventListener('keydown', (e) => {
            this.handleKeyDown(e);
        });
        
        this.inputElement.addEventListener('focus', () => {
            if (this.suggestions.length > 0) {
                this.showSuggestions();
            }
        });
        
        this.inputElement.addEventListener('blur', (e) => {
            // Delay hiding to allow for suggestion clicks
            setTimeout(() => {
                if (!this.containerElement.contains(document.activeElement)) {
                    this.hideSuggestions();
                }
            }, 150);
        });
        
        // Document click to close suggestions
        document.addEventListener('click', (e) => {
            if (!this.containerElement.contains(e.target)) {
                this.hideSuggestions();
            }
        });
        
        // Handle clicks on suggestions
        this.containerElement.addEventListener('click', (e) => {
            const suggestion = e.target.closest('.suggestion-item');
            if (suggestion && !suggestion.classList.contains('empty')) {
                this.selectSuggestion(parseInt(suggestion.dataset.index));
            }
        });
    }
    
    /**
     * Set up accessibility attributes
     */
    setupAccessibility() {
        const suggestionsId = `${this.inputId}-suggestions`;
        
        // Set up ARIA attributes on input
        this.inputElement.setAttribute('role', 'combobox');
        this.inputElement.setAttribute('aria-autocomplete', 'list');
        this.inputElement.setAttribute('aria-expanded', 'false');
        this.inputElement.setAttribute('aria-controls', suggestionsId);
        this.inputElement.setAttribute('aria-haspopup', 'listbox');
    }
    
    /**
     * Handle input changes with debouncing
     * @param {string} value - Current input value
     */
    handleInput(value) {
        this.currentQuery = value.trim();
        
        // Clear existing timeout
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }
        
        // Reset selection
        this.selectedIndex = -1;
        
        if (this.currentQuery.length < this.options.minQueryLength) {
            this.hideSuggestions();
            this.options.onEmpty();
            return;
        }
        
        // Show loading indicator
        this.showLoading();
        
        // Debounce the search
        this.searchTimeout = setTimeout(() => {
            this.performSearch(this.currentQuery);
        }, this.options.debounceDelay);
    }
    
    /**
     * Handle keyboard navigation
     * @param {KeyboardEvent} e - Keyboard event
     */
    handleKeyDown(e) {
        if (!this.isOpen || this.suggestions.length === 0) {
            return;
        }
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.navigateDown();
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.navigateUp();
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
            case 'Tab':
                // Allow tab to move focus naturally
                this.hideSuggestions();
                break;
        }
    }
    
    /**
     * Navigate down in suggestions list
     */
    navigateDown() {
        const maxIndex = this.suggestions.length - 1;
        this.selectedIndex = this.selectedIndex < maxIndex ? this.selectedIndex + 1 : 0;
        this.updateSelection();
    }
    
    /**
     * Navigate up in suggestions list
     */
    navigateUp() {
        const maxIndex = this.suggestions.length - 1;
        this.selectedIndex = this.selectedIndex > 0 ? this.selectedIndex - 1 : maxIndex;
        this.updateSelection();
    }
    
    /**
     * Update visual selection in suggestions list
     */
    updateSelection() {
        const suggestionItems = this.containerElement.querySelectorAll('.suggestion-item:not(.empty)');
        
        suggestionItems.forEach((item, index) => {
            const isSelected = index === this.selectedIndex;
            item.setAttribute('aria-selected', isSelected.toString());
            
            if (isSelected) {
                item.scrollIntoView({ block: 'nearest' });
                this.inputElement.setAttribute('aria-activedescendant', item.id || `suggestion-${index}`);
            }
        });
    }
    
    /**
     * Perform the actual search
     * @param {string} query - Search query
     */
    async performSearch(query) {
        this.isLoading = true;
        
        try {
            // Call the search function provided in options
            const results = await this.options.onSearch(query);
            this.suggestions = results || [];
            this.displaySuggestions();
        } catch (error) {
            console.error('Search error:', error);
            this.suggestions = [];
            this.displaySuggestions();
        } finally {
            this.hideLoading();
            this.isLoading = false;
        }
    }
    
    /**
     * Display search suggestions
     */
    displaySuggestions() {
        let suggestionsContainer = this.containerElement.querySelector('.search-suggestions');
        
        if (!suggestionsContainer) {
            suggestionsContainer = document.createElement('div');
            suggestionsContainer.className = 'search-suggestions';
            suggestionsContainer.id = `${this.inputId}-suggestions`;
            suggestionsContainer.setAttribute('role', 'listbox');
            this.containerElement.appendChild(suggestionsContainer);
        }
        
        if (this.suggestions.length === 0) {
            suggestionsContainer.innerHTML = `
                <div class="suggestion-item empty" role="option">
                    No tracks found
                </div>
            `;
            suggestionsContainer.classList.add('empty');
            suggestionsContainer.setAttribute('aria-label', 'No search results');
        } else {
            suggestionsContainer.innerHTML = this.suggestions.map((suggestion, index) => `
                <div class="suggestion-item" 
                     role="option" 
                     tabindex="-1"
                     data-track-id="${suggestion.track_id}"
                     data-index="${index}"
                     id="suggestion-${index}"
                     aria-selected="false">
                    <div class="suggestion-main">
                        <span class="track-name">${this.escapeHtml(suggestion.track_name)}</span>
                        <span class="artist-name">by ${this.escapeHtml(suggestion.artist_name)}</span>
                    </div>
                    <div class="suggestion-details">
                        <span class="genre">${this.escapeHtml(suggestion.genre_path?.slice(0, 2).join(' › ') || '')}</span>
                        ${suggestion.mood_tags?.length ? `<span class="moods">${this.escapeHtml(suggestion.mood_tags.slice(0, 3).join(', '))}</span>` : ''}
                    </div>
                </div>
            `).join('');
            suggestionsContainer.classList.remove('empty');
            suggestionsContainer.setAttribute('aria-label', `${this.suggestions.length} search results`);
        }
        
        this.showSuggestions();
    }
    
    /**
     * Select a suggestion by index
     * @param {number} index - Index of suggestion to select
     */
    selectSuggestion(index) {
        if (index >= 0 && index < this.suggestions.length) {
            const suggestion = this.suggestions[index];
            this.inputElement.value = suggestion.display_name;
            this.hideSuggestions();
            this.options.onSelect(suggestion);
        }
    }
    
    /**
     * Show suggestions dropdown
     */
    showSuggestions() {
        const suggestionsContainer = this.containerElement.querySelector('.search-suggestions');
        if (suggestionsContainer) {
            suggestionsContainer.style.display = 'block';
            this.isOpen = true;
            this.inputElement.setAttribute('aria-expanded', 'true');
        }
    }
    
    /**
     * Hide suggestions dropdown
     */
    hideSuggestions() {
        const suggestionsContainer = this.containerElement.querySelector('.search-suggestions');
        if (suggestionsContainer) {
            suggestionsContainer.style.display = 'none';
            this.isOpen = false;
            this.selectedIndex = -1;
            this.inputElement.setAttribute('aria-expanded', 'false');
            this.inputElement.removeAttribute('aria-activedescendant');
        }
    }
    
    /**
     * Show loading indicator
     */
    showLoading() {
        if (!this.isLoading) {
            const loadingIndicator = document.createElement('span');
            loadingIndicator.className = 'search-loading';
            loadingIndicator.id = `${this.inputId}-loading`;
            loadingIndicator.setAttribute('aria-label', 'Searching...');
            loadingIndicator.setAttribute('role', 'status');
            
            this.containerElement.appendChild(loadingIndicator);
        }
    }
    
    /**
     * Hide loading indicator
     */
    hideLoading() {
        const loadingIndicator = this.containerElement.querySelector('.search-loading');
        if (loadingIndicator) {
            loadingIndicator.remove();
        }
    }
    
    /**
     * Escape HTML to prevent XSS
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    /**
     * Clear current search and suggestions
     */
    clear() {
        this.inputElement.value = '';
        this.currentQuery = '';
        this.suggestions = [];
        this.selectedIndex = -1;
        this.hideSuggestions();
        this.hideLoading();
    }
    
    /**
     * Update configuration options
     * @param {Object} newOptions - New options to merge
     */
    updateOptions(newOptions) {
        this.options = { ...this.options, ...newOptions };
    }
    
    /**
     * Focus the search input
     */
    focus() {
        this.inputElement.focus();
    }
    
    /**
     * Get current search value
     * @returns {string} Current search query
     */
    getValue() {
        return this.inputElement.value;
    }
    
    /**
     * Set search value
     * @param {string} value - Value to set
     */
    setValue(value) {
        this.inputElement.value = value;
        this.currentQuery = value.trim();
    }
}

// Export for use in other modules
window.DebouncedSearch = DebouncedSearch;