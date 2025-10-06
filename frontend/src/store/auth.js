import { defineStore } from 'pinia';
import { jwtDecode } from 'jwt-decode';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,  // { full_name, role, ... }
    token: null, // access token
  }),
  actions: {
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