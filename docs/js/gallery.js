/**
 * Character and Location Gallery Logic
 */

class CharacterGallery {
    constructor() {
        this.characters = {};
        this.filter = 'all';
        this.mainParty = []; // Will be populated from config
        this.creatures = []; // Will be populated from config
    }

    async init() {
        try {
            const response = await fetch('data/characters.json');
            if (!response.ok) {
                throw new Error('Failed to load characters data');
            }
            this.characters = await response.json();
            this.renderGallery();
            this.setupFilters();
            this.setupModal();
        } catch (error) {
            console.error('Failed to initialize character gallery:', error);
            this.showError('Failed to load character data. Please refresh the page.');
        }
    }

    categorizeCharacters() {
        return Object.entries(this.characters).map(([name, data]) => {
            let category = 'npcs';
            if (this.mainParty.includes(name)) {
                category = 'party';
            } else if (this.creatures.includes(name)) {
                category = 'creatures';
            }

            return {
                name,
                ...data,
                category
            };
        });
    }

    renderGallery() {
        const characters = this.categorizeCharacters();
        const filtered = this.filter === 'all' ? characters :
                        characters.filter(c => c.category === this.filter);

        const container = document.getElementById('character-grid');

        if (filtered.length === 0) {
            container.innerHTML = `
                <div class="no-results">
                    <p>No characters found in this category.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = filtered.map(char => {
            const role = this.extractRole(char);
            const race = this.extractRace(char);
            const thumbnail = this.getThumbnail(char);
            const summary = this.getSummary(char);

            return `
                <div class="character-card" data-category="${char.category}">
                    ${thumbnail ? `<img src="${thumbnail}" alt="${char.name}" class="card-thumbnail" onerror="this.src='images/placeholder.png'">` : ''}
                    <div class="card-content">
                        <h3>${char.name}</h3>
                        ${role ? `<p class="role">${role}</p>` : ''}
                        ${race ? `<p class="race">${race}</p>` : ''}
                        ${summary ? `<p class="summary">${summary}</p>` : ''}
                        <button class="expand-btn" data-character="${char.name}">View Full Description</button>
                    </div>
                </div>
            `;
        }).join('');

        // Add click handlers
        container.querySelectorAll('.expand-btn[data-character]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const charName = btn.dataset.character;
                this.showCharacterModal(charName);
            });
        });
    }

    getThumbnail(char) {
        // Create filename from character name
        const filename = char.name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
        return `images/characters/${filename}-portrait.png`;
    }

    getSummary(char) {
        if (char.full_description) {
            // Return first 150 characters
            return char.full_description.substring(0, 150) + (char.full_description.length > 150 ? '...' : '');
        }
        return '';
    }

    extractRole(char) {
        if (!char.description_components) return '';
        if (char.description_components.class) return char.description_components.class;
        return '';
    }

    extractRace(char) {
        if (!char.description_components) return '';
        if (char.description_components.race) return char.description_components.race;
        return '';
    }

    setupFilters() {
        const filterBtns = document.querySelectorAll('.filter-btn');
        filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.filter = btn.dataset.filter;
                this.renderGallery();
            });
        });
    }

    setupModal() {
        const modal = document.getElementById('character-modal');

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal.classList.contains('active')) {
                modal.classList.remove('active');
            }
        });
    }

    showCharacterModal(name) {
        const char = this.characters[name];
        if (!char) return;

        const modal = document.getElementById('character-modal');

        modal.innerHTML = `
            <div class="modal-content">
                <button class="close-modal" aria-label="Close">&times;</button>
                <h2>${char.name}</h2>
                ${char.full_description ?
                    `<p class="description">${char.full_description}</p>` : ''}
                ${this.renderDescriptionComponents(char.description_components)}
            </div>
        `;

        modal.classList.add('active');

        modal.querySelector('.close-modal').addEventListener('click', () => {
            modal.classList.remove('active');
        });
    }

    renderDescriptionComponents(components) {
        if (!components) return '';

        return Object.entries(components)
            .filter(([key, value]) => value && value.trim())
            .map(([key, value]) => `
                <div class="desc-section">
                    <h4>${this.formatComponentTitle(key)}</h4>
                    <p>${value}</p>
                </div>
            `).join('');
    }

    formatComponentTitle(key) {
        return key
            .replace(/_/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase());
    }

    showError(message) {
        const container = document.getElementById('character-grid');
        container.innerHTML = `
            <div class="error-message">
                <h2>Error</h2>
                <p>${message}</p>
            </div>
        `;
    }
}

class LocationGallery {
    constructor() {
        this.locations = {};
    }

    async init() {
        try {
            const response = await fetch('data/locations.json');
            if (!response.ok) {
                throw new Error('Failed to load locations data');
            }
            this.locations = await response.json();
            this.renderGallery();
            this.setupModal();
        } catch (error) {
            console.error('Failed to initialize location gallery:', error);
            this.showError('Failed to load location data. Please refresh the page.');
        }
    }

    renderGallery() {
        const container = document.getElementById('location-grid');
        const locations = Object.entries(this.locations);

        if (locations.length === 0) {
            container.innerHTML = `
                <div class="no-results">
                    <p>No locations found.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = locations.map(([name, data]) => {
            const thumbnail = this.getThumbnail(name);
            const summary = this.getSummary(data);

            return `
                <div class="character-card location-card">
                    ${thumbnail ? `<img src="${thumbnail}" alt="${data.name || name}" class="card-thumbnail" onerror="this.src='images/placeholder.png'">` : ''}
                    <div class="card-content">
                        <h3>${data.name || name}</h3>
                        ${data.description_components?.type ?
                            `<p class="role">${data.description_components.type}</p>` : ''}
                        ${summary ? `<p class="summary">${summary}</p>` : ''}
                        <button class="expand-btn" data-location="${name}">View Full Description</button>
                    </div>
                </div>
            `;
        }).join('');

        container.querySelectorAll('.expand-btn[data-location]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const locName = btn.dataset.location;
                this.showLocationModal(locName);
            });
        });
    }

    getThumbnail(locationName) {
        const filename = locationName.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '');
        return `images/locations/${filename}.png`;
    }

    getSummary(data) {
        const desc = data.full_description || data.description || '';
        return desc.substring(0, 150) + (desc.length > 150 ? '...' : '');
    }

    setupModal() {
        const modal = document.getElementById('location-modal');

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal.classList.contains('active')) {
                modal.classList.remove('active');
            }
        });
    }

    showLocationModal(name) {
        const loc = this.locations[name];
        if (!loc) return;

        const modal = document.getElementById('location-modal');

        modal.innerHTML = `
            <div class="modal-content">
                <button class="close-modal" aria-label="Close">&times;</button>
                <h2>${loc.name || name}</h2>
                ${loc.full_description ?
                    `<p class="description">${loc.full_description}</p>` : ''}
                ${this.renderDescriptionComponents(loc.description_components)}
            </div>
        `;

        modal.classList.add('active');

        modal.querySelector('.close-modal').addEventListener('click', () => {
            modal.classList.remove('active');
        });
    }

    renderDescriptionComponents(components) {
        if (!components) return '';

        return Object.entries(components)
            .filter(([key, value]) => value && value.trim())
            .map(([key, value]) => `
                <div class="desc-section">
                    <h4>${this.formatComponentTitle(key)}</h4>
                    <p>${value}</p>
                </div>
            `).join('');
    }

    formatComponentTitle(key) {
        return key
            .replace(/_/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase());
    }

    showError(message) {
        const container = document.getElementById('location-grid');
        container.innerHTML = `
            <div class="error-message">
                <h2>Error</h2>
                <p>${message}</p>
            </div>
        `;
    }
}

// Initialize based on page
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('character-grid')) {
        window.characterGallery = new CharacterGallery();
        window.characterGallery.init();
    } else if (document.getElementById('location-grid')) {
        window.locationGallery = new LocationGallery();
        window.locationGallery.init();
    }
});
