import { createRouter, createWebHistory } from 'vue-router';
import LoginPage from '@/components/LoginPage.vue';
import AdminDashboard from '@/views/AdminDashboard.vue';
import UserDashboard from '@/views/UserDashboard.vue';
import { useAuthStore } from '@/store/auth';

const routes = [
  { path: '/login', component: LoginPage },
  { path: '/admin-dashboard', component: AdminDashboard, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/user-dashboard', component: UserDashboard, meta: { requiresAuth: true, role: 'user' } },
  { path: '/', redirect: '/login' },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const store = useAuthStore();
  const isAuthenticated = !!store.token;
  const userRole = store.user?.role;

  if (to.meta.requiresAuth) {
    if (!isAuthenticated) {
      next('/login');
    } else if (to.meta.role && to.meta.role !== userRole) {
      next(userRole === 'admin' ? '/admin-dashboard' : '/user-dashboard');
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;