// Storage Service for consistent data persistence
class StorageService {
    constructor() {
        this.keys = {
            HISTORY: 'foodAnalysisHistory',
            PREFERENCES: 'userPreferences',
            SESSION: 'userSession'
        };
    }

    // History management
    saveHistory(history) {
        try {
            localStorage.setItem(this.keys.HISTORY, JSON.stringify(history));
            return true;
        } catch (error) {
            console.error('Error saving history:', error);
            return false;
        }
    }

    loadHistory() {
        try {
            return JSON.parse(localStorage.getItem(this.keys.HISTORY) || '[]');
        } catch (error) {
            console.error('Error loading history:', error);
            return [];
        }
    }

    clearHistory() {
        try {
            localStorage.removeItem(this.keys.HISTORY);
            return true;
        } catch (error) {
            console.error('Error clearing history:', error);
            return false;
        }
    }

    // Preferences management
    savePreferences(preferences) {
        try {
            localStorage.setItem(this.keys.PREFERENCES, JSON.stringify(preferences));
            return true;
        } catch (error) {
            console.error('Error saving preferences:', error);
            return false;
        }
    }

    loadPreferences() {
        try {
            const defaultPrefs = {
                dailyCalories: 2000,
                dailyProtein: 50,
                dailyCarbs: 300,
                dailyFat: 70,
                enableNotifications: true,
                theme: 'light'
            };
            
            return JSON.parse(localStorage.getItem(this.keys.PREFERENCES) || JSON.stringify(defaultPrefs));
        } catch (error) {
            console.error('Error loading preferences:', error);
            return defaultPrefs;
        }
    }

    // Session management
    saveSession(session) {
        try {
            // Session data expires after 24 hours
            const sessionData = {
                ...session,
                expires: Date.now() + (24 * 60 * 60 * 1000)
            };
            localStorage.setItem(this.keys.SESSION, JSON.stringify(sessionData));
            return true;
        } catch (error) {
            console.error('Error saving session:', error);
            return false;
        }
    }

    loadSession() {
        try {
            const sessionData = JSON.parse(localStorage.getItem(this.keys.SESSION) || 'null');
            
            if (sessionData && sessionData.expires > Date.now()) {
                return sessionData;
            }
            
            // Clear expired session
            this.clearSession();
            return null;
        } catch (error) {
            console.error('Error loading session:', error);
            return null;
        }
    }

    clearSession() {
        localStorage.removeItem(this.keys.SESSION);
    }

    // Utility methods
    getStorageSize() {
        let total = 0;
        for (let key in localStorage) {
            if (localStorage.hasOwnProperty(key)) {
                total += localStorage[key].length;
            }
        }
        return total;
    }

    clearAll() {
        try {
            localStorage.clear();
            return true;
        } catch (error) {
            console.error('Error clearing all storage:', error);
            return false;
        }
    }
}

// Export for global use
window.StorageService = StorageService;