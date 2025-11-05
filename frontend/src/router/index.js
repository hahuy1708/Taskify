// scr/router/index.js

import { createRouter, createWebHistory } from 'vue-router';
import Login from '@/pages/Auth/Login.vue';
import Register from '@/pages/Auth/Register.vue';
import ForgotPassword from '@/pages/Auth/ForgotPassword.vue';
import ResetPasswordConfirm from '@/pages/Auth/ResetPasswordConfirm.vue';
import AuthLayout from '@/layouts/AuthLayout.vue';
import DashboardLayout from '@/layouts/DashboardLayout.vue'
import AdminDashboard from '@/pages/Dashboard/AdminDashboard.vue';
import UserDashboard from '@/pages/Dashboard/UserDashboard.vue';
import { useAuthStore } from '@/store/auth';
import ProjectListPage from '@/pages/ProjectListPage.vue';
import UserListPage from '@/pages/UserListPage.vue';
import UserProfile from '@/components/Users/UserProfile.vue';
import TeamListPage from '@/pages/TeamListPage.vue';
import TaskPage from '@/pages/TaskPage.vue';
import Unauthorized from '@/pages/Unauthorized.vue';


const routes = [
  {
  path: '/',
  redirect: '/auth/login'
  },
  {
    path: '/auth',
    component: AuthLayout,
    children: [
      { path: 'login', component: Login },
      { path: 'register', component: Register }
    ]
  },
  {
    path: '/dashboard',
    component: DashboardLayout,
    meta: { requiresAuth: true },
    children: [
      { path: 'admin', component: AdminDashboard, meta: { role: 'admin' } },
      { path: 'user', component: UserDashboard, meta: { role: 'user' } },
      { path: 'projects', component: ProjectListPage, meta: { requiresAuth: true } },
      { path: 'users', component: UserListPage, meta: { requiresAuth: true, role: 'admin' } },
      { path: 'users/leaders', component: UserListPage, meta: { requiresAuth: true, role: 'admin' } },
      { path: 'users/:id', component: UserProfile, meta: { requiresAuth: true, role: 'admin' } }, // view other user's profile by id for admin
      { path: 'profile', component: UserProfile, meta: { requiresAuth: true } },
      { path: 'teams', component: TeamListPage, meta: { requiresAuth: true } },
      { path: 'tasks', component: TaskPage, meta: { requiresAuth: true } },
    ]
  },
  {
    path: '/forgot-password', component: ForgotPassword
  },
  {
    path: '/reset-password/:uid/:token', component: ResetPasswordConfirm
  },
  {
    path: '/unauthorized', component: Unauthorized
  },
  
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
    return next('/unauthorized')
  }
    
  next()
  
});

export default router;