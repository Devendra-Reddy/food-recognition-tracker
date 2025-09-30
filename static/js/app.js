// Food Recognition Tracker - Enhanced Client-Side Application
class FoodTrackerApp {
    constructor() {
        this.state = {
            selectedAPI: 'nutrition',
            uploadedFile: null,
            imagePreview: null,
            analysisHistory: this.loadHistory(),
            currentResult: null,
            isLoading: false,
            userPreferences: this.loadPreferences()
        };
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.renderHistory();
        this.renderPreferences();
    }

    bindEvents() {
        // API Selection
        const apiOptions = document.querySelectorAll('.api-option');
        if (apiOptions) {
            apiOptions.forEach(option => {
                option.addEventListener('click', (e) => {
                    this.selectAPI(e.currentTarget.dataset.api);
                });
            });
        }

        // File Upload
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        
        if (uploadArea && fileInput) {
            uploadArea.addEventListener('click', () => fileInput.click());
            uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
            uploadArea.addEventListener('drop', this.handleFileDrop.bind(this));
            fileInput.addEventListener('change', (e) => this.handleFileSelect(e.target.files[0]));
        }

        // Analysis
        const analyzeBtn = document.getElementById('analyzeBtn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.analyzeImage());
        }
        
        // History Management
        const clearHistoryBtn = document.getElementById('clearHistory');
        if (clearHistoryBtn) {
            clearHistoryBtn.addEventListener('click', () => this.clearHistory());
        }
        
        // Preferences
        const savePrefsBtn = document.getElementById('savePreferences');
        if (savePrefsBtn) {
            savePrefsBtn.addEventListener('click', () => this.savePreferences());
        }

        // Go Back button
        const goBackBtn = document.getElementById('goBackButton');
        if (goBackBtn) {
            goBackBtn.addEventListener('click', () => {
                this.showSection('uploadSection');
                this.updateUploadUI(false);
            });
        }

        // Navigation
        const navLinks = document.querySelectorAll('.nav-link');
        if (navLinks) {
            navLinks.forEach(link => {
                link.addEventListener('click', (e) => {
                    const section = e.currentTarget.dataset.section;
                    this.showSection(section);
                });
            });
        }
    }

    selectAPI(api) {
        this.state.selectedAPI = api;
        
        // Update UI
        document.querySelectorAll('.api-option').forEach(opt => {
            opt.classList.remove('active');
        });
        
        const selectedOption = document.querySelector(`[data-api="${api}"]`);
        if (selectedOption) {
            selectedOption.classList.add('active');
        }
        
        // Update hidden input
        const apiInput = document.getElementById('selectedApi');
        if (apiInput) {
            apiInput.value = api;
        }
        
        // Show API-specific instructions
        this.showAPIInstructions(api);
    }

    showAPIInstructions(api) {
        const instructions = {
            nutrition: "Get detailed nutrition facts and health insights",
            roboflow: "Fast food detection with computer vision",
            spoonacular: "Recipe suggestions and cooking information",
            bodyrequirements: "Daily nutritional requirements and goals"
        };
        
        const instructionsElement = document.getElementById('apiInstructions');
        if (instructionsElement) {
            instructionsElement.textContent = instructions[api] || "Select an API for analysis";
        }
    }

    handleDragOver(e) {
        e.preventDefault();
        const uploadArea = document.getElementById('uploadArea');
        if (uploadArea) {
            uploadArea.classList.add('dragover');
        }
    }

    handleFileDrop(e) {
        e.preventDefault();
        const uploadArea = document.getElementById('uploadArea');
        if (uploadArea) {
            uploadArea.classList.remove('dragover');
        }
        
        const files = e.dataTransfer.files;
        if (files && files.length > 0) {
            this.handleFileSelect(files[0]);
        }
    }

    handleFileSelect(file) {
        if (!this.validateFile(file)) return;

        this.state.uploadedFile = file;
        this.showImagePreview(file);
        this.updateUploadUI(true);
    }

    validateFile(file) {
        const validTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
        const maxSize = 5 * 1024 * 1024; // 5MB

        if (!validTypes.includes(file.type)) {
            this.showError('Please select a valid image file (JPEG, PNG, WEBP, GIF)');
            return false;
        }

        if (file.size > maxSize) {
            this.showError('File size must be less than 5MB');
            return false;
        }

        return true;
    }

    showImagePreview(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            this.state.imagePreview = e.target.result;
            const previewContainer = document.getElementById('imagePreview');
            if (previewContainer) {
                previewContainer.innerHTML = `
                    <img src="${e.target.result}" alt="Preview" class="preview-image">
                    <div class="file-info">
                        <strong>${file.name}</strong>
                        <span>${(file.size / 1024).toFixed(1)} KB</span>
                    </div>
                `;
            }
        };
        reader.readAsDataURL(file);
    }

    updateUploadUI(isReady) {
        const uploadArea = document.getElementById('uploadArea');
        const analyzeBtn = document.getElementById('analyzeBtn');

        if (uploadArea) {
            if (isReady) {
                uploadArea.innerHTML = `
                    <div class="upload-success">
                        <div class="upload-icon">✅</div>
                        <p>Ready to analyze!</p>
                        <small>Click to change image</small>
                    </div>
                `;
            } else {
                uploadArea.innerHTML = `
                    <div class="upload-prompt">
                        <div class="upload-icon">📁</div>
                        <p><strong>Drop your food image here</strong></p>
                        <p>or click to browse files</p>
                        <small>Supports: JPG, PNG, WEBP, GIF (max 5MB)</small>
                    </div>
                `;
            }
        }

        if (analyzeBtn) {
            analyzeBtn.disabled = !isReady;
        }
    }

    async analyzeImage() {
        if (!this.state.uploadedFile) {
            this.showError('Please select an image first');
            return;
        }

        this.setLoading(true);

        try {
            const formData = new FormData();
            formData.append('image', this.state.uploadedFile);
            formData.append('api', this.state.selectedAPI);

            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Analysis failed: ${response.statusText}`);
            }

            const result = await response.json();
            this.handleAnalysisResult(result);

        } catch (error) {
            this.showError(error.message);
        } finally {
            this.setLoading(false);
        }
    }

    handleAnalysisResult(result) {
        this.state.currentResult = result;
        this.state.analysisHistory.unshift(result);
        this.saveHistory();

        this.renderResults(result);
        this.renderHistory();
        this.showSection('resultsSection');
    }

    renderResults(result) {
        // Update basic info
        const foodNameElement = document.getElementById('resultFoodName');
        const healthRatingElement = document.getElementById('resultHealthRating');
        
        if (foodNameElement) {
            foodNameElement.textContent = result.food_name || 'Unknown Food';
        }
        
        if (healthRatingElement) {
            healthRatingElement.textContent = result.health_rating || 'Unknown';
            healthRatingElement.className = `health-rating ${this.getRatingClass(result.health_rating)}`;
        }
        
        // Update nutrition data
        this.renderNutritionData(result.nutrition);
        
        // Update demographic information
        this.renderDemographicInfo(result.demographic_info);
        
        // Update recommendations
        const recommendationElement = document.getElementById('recommendationText');
        const portionElement = document.getElementById('portionSuggestion');
        
        if (recommendationElement) {
            recommendationElement.textContent = result.recommendation || 'No recommendation available.';
        }
        
        if (portionElement) {
            portionElement.textContent = result.portion_suggestion || 'Standard portion recommended.';
        }
    }

    renderNutritionData(nutrition) {
        const container = document.getElementById('nutritionData');
        if (!container) return;

        const nutrients = [
            { key: 'calories', label: 'Calories', unit: '', icon: '🔥' },
            { key: 'protein', label: 'Protein', unit: 'g', icon: '💪' },
            { key: 'carbs', label: 'Carbs', unit: 'g', icon: '🌾' },
            { key: 'fat', label: 'Fat', unit: 'g', icon: '⛽' },
            { key: 'fiber', label: 'Fiber', unit: 'g', icon: '🌿' },
            { key: 'sugar', label: 'Sugar', unit: 'g', icon: '🍬' },
            { key: 'sodium', label: 'Sodium', unit: 'mg', icon: '🧂' }
        ];

        let html = '';
        nutrients.forEach(nutrient => {
            const value = nutrition ? nutrition[nutrient.key] : null;
            if (value !== undefined && value !== null) {
                html += `
                    <div class="nutrition-item">
                        <div class="nutrient-icon">${nutrient.icon}</div>
                        <div class="nutrient-info">
                            <div class="nutrient-value">${value}${nutrient.unit}</div>
                            <div class="nutrient-label">${nutrient.label}</div>
                        </div>
                    </div>
                `;
            }
        });

        container.innerHTML = html || '<p>No nutrition data available.</p>';
    }

    renderDemographicInfo(demographic) {
        const container = document.getElementById('demographicInfo');
        if (!container) return;
        
        if (!demographic) {
            container.innerHTML = '<p>No demographic information available for this food.</p>';
            return;
        }
        
        container.innerHTML = `
            <div class="demographic-item">
                <h4>🌎 Origin & History</h4>
                <p><strong>Origin:</strong> ${demographic.origin || 'Unknown'}</p>
                <p><strong>Cultural Significance:</strong> ${demographic.cultural_significance || 'Not specified'}</p>
            </div>
            
            <div class="demographic-item">
                <h4>📊 Global Popularity</h4>
                <p><strong>Popularity:</strong> ${demographic.global_popularity || 'Unknown'}</p>
                <p><strong>Common Consumption:</strong> ${demographic.common_consumption || 'Global'}</p>
            </div>
            
            <div class="demographic-item">
                <h4>📅 Seasonal Patterns</h4>
                <p><strong>Seasonal Availability:</strong> ${demographic.seasonal_pattern || 'Year-round'}</p>
            </div>
        `;
    }

    renderHistory() {
        const container = document.getElementById('historyList');
        if (!container) return;
        
        const history = this.state.analysisHistory.slice(0, 10);
        
        if (history.length === 0) {
            container.innerHTML = '<p class="empty-history">No analysis history yet</p>';
            return;
        }

        container.innerHTML = history.map((item, index) => `
            <div class="history-item" onclick="app.viewHistoryItem(${index})">
                <div class="history-food">${item.food_name || 'Unknown Food'}</div>
                <div class="history-details">
                    <span class="health-rating ${this.getRatingClass(item.health_rating)}">${item.health_rating || 'Unknown'}</span>
                    <span class="calories">${item.nutrition?.calories || 0} cal</span>
                    <span class="timestamp">${new Date(item.timestamp).toLocaleDateString()}</span>
                </div>
            </div>
        `).join('');
    }

    viewHistoryItem(index) {
        const item = this.state.analysisHistory[index];
        this.state.currentResult = item;
        this.renderResults(item);
        this.showSection('resultsSection');
    }

    clearHistory() {
        if (confirm('Are you sure you want to clear your analysis history?')) {
            this.state.analysisHistory = [];
            this.saveHistory();
            this.renderHistory();
        }
    }

    renderPreferences() {
        const prefs = this.state.userPreferences;
        const calorieGoal = document.getElementById('calorieGoal');
        const proteinGoal = document.getElementById('proteinGoal');
        const carbsGoal = document.getElementById('carbsGoal');
        const fatGoal = document.getElementById('fatGoal');
        
        if (calorieGoal) calorieGoal.value = prefs.dailyCalories;
        if (proteinGoal) proteinGoal.value = prefs.dailyProtein;
        if (carbsGoal) carbsGoal.value = prefs.dailyCarbs;
        if (fatGoal) fatGoal.value = prefs.dailyFat;
    }

    savePreferences() {
        this.state.userPreferences = {
            dailyCalories: parseInt(document.getElementById('calorieGoal').value) || 2000,
            dailyProtein: parseInt(document.getElementById('proteinGoal').value) || 50,
            dailyCarbs: parseInt(document.getElementById('carbsGoal').value) || 300,
            dailyFat: parseInt(document.getElementById('fatGoal').value) || 70
        };
        this.savePreferencesToStorage();
        this.showNotification('Preferences saved successfully!');
    }

    // Storage methods
    loadHistory() {
        try {
            return JSON.parse(localStorage.getItem('foodAnalysisHistory') || '[]');
        } catch (e) {
            return [];
        }
    }

    saveHistory() {
        try {
            localStorage.setItem('foodAnalysisHistory', JSON.stringify(this.state.analysisHistory));
        } catch (e) {
            console.error('Error saving history:', e);
        }
    }

    loadPreferences() {
        try {
            const defaultPrefs = {
                dailyCalories: 2000,
                dailyProtein: 50,
                dailyCarbs: 300,
                dailyFat: 70
            };
            return JSON.parse(localStorage.getItem('userPreferences') || JSON.stringify(defaultPrefs));
        } catch (e) {
            return {
                dailyCalories: 2000,
                dailyProtein: 50,
                dailyCarbs: 300,
                dailyFat: 70
            };
        }
    }

    savePreferencesToStorage() {
        try {
            localStorage.setItem('userPreferences', JSON.stringify(this.state.userPreferences));
        } catch (e) {
            console.error('Error saving preferences:', e);
        }
    }

    // UI Utilities
    setLoading(loading) {
        this.state.isLoading = loading;
        const loadingSection = document.getElementById('loadingSection');
        const analyzeBtn = document.getElementById('analyzeBtn');
        
        if (loadingSection) {
            loadingSection.style.display = loading ? 'block' : 'none';
        }
        
        if (analyzeBtn) {
            analyzeBtn.disabled = loading;
        }
        
        if (loading) {
            this.showSection('loadingSection');
        }
    }

    showSection(sectionId) {
        const sections = ['uploadSection', 'loadingSection', 'resultsSection', 'historySection', 'preferencesSection'];
        
        sections.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.style.display = 'none';
            }
        });
        
        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.style.display = 'block';
        }
        
        this.updateNavigation(sectionId);
    }

    updateNavigation(activeSection) {
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.classList.remove('active');
        });
        
        const activeLink = document.querySelector(`[data-section="${activeSection}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type = 'success') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <span class="notification-icon">${type === 'error' ? '❌' : '✅'}</span>
            <span class="notification-message">${message}</span>
            <button class="notification-close">×</button>
        `;
        
        // Add close functionality
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.remove();
        });
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    getRatingClass(rating) {
        if (!rating) return 'rating-unknown';
        if (rating.includes('Excellent')) return 'rating-excellent';
        if (rating.includes('Good')) return 'rating-good';
        if (rating.includes('Moderate')) return 'rating-moderate';
        if (rating.includes('Limit')) return 'rating-limit';
        return 'rating-unknown';
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new FoodTrackerApp();
});