// API Service for consistent API calls
class ApiService {
    constructor() {
        this.baseURL = '';
        this.timeout = 30000;
    }

    async analyzeImage(imageFile, apiChoice) {
        const formData = new FormData();
        formData.append('image', imageFile);
        formData.append('api', apiChoice);

        return this._request('/analyze', {
            method: 'POST',
            body: formData,
            timeout: this.timeout
        });
    }

    async getHistory(limit = 10) {
        return this._request(`/history?limit=${limit}`);
    }

    async getAnalytics(hours = 24, days = 7) {
        return this._request(`/api/analytics?hours=${hours}&days=${days}`);
    }

    async getTrends() {
        return this._request('/api/trends');
    }

    async getStatus() {
        return this._request('/api/status');
    }

    async _request(endpoint, options = {}) {
        const config = {
            method: 'GET',
            headers: {},
            timeout: this.timeout,
            ...options
        };

        try {
            const response = await fetch(endpoint, config);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API request failed: ${endpoint}`, error);
            throw error;
        }
    }
}

// Export for global use
window.ApiService = ApiService;