import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes: RouteRecordRaw[] = [
  {
    path: '/student',
    name: 'student',
    component: () => import('../views/StudentDashboard.vue'),
  },
  {
    path: '/instructor',
    name: 'instructor',
    component: () => import('../views/InstructorDashboard.vue'),
  },
  {
    path: '/admin',
    name: 'admin',
    component: () => import('../views/AdminDashboard.vue'),
  },
  {
    path: '/super-admin',
    name: 'super-admin',
    component: () => import('../views/SuperAdminDashboard.vue'),
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue'),
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/RegisterView.vue'),
  },
  {
    path: '/register/role',
    name: 'register-role',
    component: () => import('../views/RegisterRoleSelect.vue')
  },
  {
    path: '/register/student',
    name: 'register-student',
    component: () => import('../views/RegisterStudent.vue')
  },
  {
    path: '/register/instructor',
    name: 'register-instructor',
    component: () => import('../views/RegisterInstructor.vue')
  },
  {
    path: '/register/student/select-school',
    name: 'register-student-select-school',
    component: () => import('../views/SelectSchool.vue')
  },
  {
    path: '/student-info',
    name: 'student-info',
    component: () => import('../views/StudentInfo.vue'),
  },
  {
    path: '/',
    redirect: '/login',
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  // Allow public access to student-info
  const publicRoutes = ['login', 'register', 'register-role', 'register-student', 'register-instructor', 'student-info']
  if (!userStore.isAuthenticated && !publicRoutes.includes(to.name as string)) {
    return next({ name: 'login' })
  }
  // Role-based protection
  if (to.name === 'student' && userStore.user?.role !== 'student') return next(false)
  if (to.name === 'instructor' && userStore.user?.role !== 'instructor') return next(false)
  if (to.name === 'admin' && userStore.user?.role !== 'admin') return next(false)
  if (to.name === 'super-admin' && userStore.user?.role !== 'superadmin') return next(false)
  next()
})

export default router
