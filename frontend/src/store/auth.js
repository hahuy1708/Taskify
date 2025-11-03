import { defineStore } from 'pinia';
import { jwtDecode } from 'jwt-decode';
import { getProfile, refreshToken } from '@/api/authApi';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,  // { full_name, role, ... }
    token: null, // access token
  }),
  actions: {
    async initialize() {
      // Restore tokens from localStorage and fetch profile. Attempt refresh if needed.
      const access = localStorage.getItem('access_token');
      const refresh = localStorage.getItem('refresh_token');
      this.token = access;

      if (!access && !refresh) {
        // No tokens, ensure clean state
        this.user = null;
        return;
      }

      try {
        // Try to fetch profile with current access token
        const me = await getProfile();
        this.user = me;
        return;
      } catch (e) {
        // If access likely expired, try refresh if we have a refresh token
        if (!refresh) {
          this.logout();
          return;
        }
        try {
          const { access: newAccess } = await refreshToken();
          this.token = newAccess;
          const me = await getProfile();
          this.user = me;
        } catch (refreshErr) {
          this.logout();
        }
      }
    },
    setUser(data) {
      this.user = data;
      this.token = localStorage.getItem('access_token');
    },
    getRole() {
      if (this.token) {
        const decoded = jwtDecode(this.token);
        return decoded.role || this.user?.role;  // Nếu backend include role trong token payload
      }
      return null;
    },
    logout() {
      this.user = null;
      this.token = null;
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    },
  },
});