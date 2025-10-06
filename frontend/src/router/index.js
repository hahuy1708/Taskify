// scr/router/index.js

import { createRouter, createWebHistory } from 'vue-router';
import Login from '@/pages/Auth/Login.vue';
import AuthLayout from '@/layouts/AuthLayout.vue';
import DashboardLayout from '@/layouts/DashboardLayout.vue'
import AdminDashboard from '@/pages/Dashboard/AdminDashboard.vue';
import UserDashboard from '@/pages/Dashboard/UserDashboard.vue';
import { useAuthStore } from '@/store/auth';

// const routes = [
//   { path: '/login', component: Login },
//   { path: '/admin-dashboard', component: AdminDashboard, meta: { requiresAuth: true, role: 'admin' } },
//   { path: '/user-dashboard', component: UserDashboard, meta: { requiresAuth: true, role: 'user' } },
//   { path: '/', redirect: '/login' },
// ];

const routes = [
  {
  path: '/',
  redirect: '/auth/login'
  },
  {
    path: '/auth',
    component: AuthLayout,
    children: [
      { path: 'login', component: Login }
    ]
  },
  {
    path: '/dashboard',
    component: DashboardLayout,
    meta: { requiresAuth: true },
    children: [
      { path: 'admin', component: AdminDashboard, meta: { role: 'admin' } },
      { path: 'user', component: UserDashboard, meta: { role: 'user' } }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const store = useAuthStore();
  const isAuthenticated = !!store.token;
  const userRole = store.user?.role;
  if (to.meta.requiresAuth && !isAuthenticated) {
    return next('/auth/login')
  }

  if (to.path === '/dashboard') {
    if (userRole === 'admin') return next('/dashboard/admin')
    if (userRole === 'user') return next('/dashboard/user')
    }

  if (to.meta.role && to.meta.role !== userRole) {
    return next(`/dashboard/${userRole}`)
    }
    
  next()
  
});

export default router;