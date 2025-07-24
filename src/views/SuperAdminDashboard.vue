<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import {
  getAllUsers,
  createAdmin as apiCreateAdmin,
  deleteAdmin as apiDeleteAdmin,
} from '@/services/api'

const users = ref<any[]>([])
const usersLoading = ref(false)
const usersError = ref('')

async function fetchUsers() {
  usersLoading.value = true
  usersError.value = ''
  try {
    const { data } = await getAllUsers()
    users.value = data
  } catch (e: any) {
    usersError.value = e?.response?.data?.detail || 'Failed to load users.'
  } finally {
    usersLoading.value = false
  }
}
onMounted(() => {
  fetchUsers()
})

const activeSection = ref('admin-management')
const profileMenuOpen = ref(false)
function setSection(section: string) {
  activeSection.value = section
}
function toggleProfileMenu() {
  profileMenuOpen.value = !profileMenuOpen.value
}
function closeProfileMenu() {
  profileMenuOpen.value = false
}

// Admin Management Tabs
const userTab = ref<'admins' | 'instructors' | 'students'>('admins')
function setUserTab(tab: 'admins' | 'instructors' | 'students') {
  userTab.value = tab
}

// Filtered users by role
const filteredUsers = computed(() => {
  if (userTab.value === 'admins') return users.value.filter((u) => u.role === 'admin')
  if (userTab.value === 'instructors') return users.value.filter((u) => u.role === 'instructor')
  if (userTab.value === 'students') return users.value.filter((u) => u.role === 'student')
  return []
})

// Pagination
const page = ref(1)
const itemsPerPage = 10
const pagedUsers = computed(() => {
  const list = filteredUsers.value
  const start = (page.value - 1) * itemsPerPage
  return list.slice(start, start + itemsPerPage)
})
const totalPages = computed(() => {
  const list = filteredUsers.value
  return Math.ceil(list.length / itemsPerPage) || 1
})
function goToPage(p: number) {
  if (p >= 1 && p <= totalPages.value) page.value = p
}

// Admin creation form
const newAdmin = ref({ name: '', email: '', password: '' })
const showAdminModal = ref(false)
const adminFormLoading = ref(false)
const adminFormError = ref('')
function openAdminModal() {
  showAdminModal.value = true
}
function closeAdminModal() {
  showAdminModal.value = false
  newAdmin.value = { name: '', email: '', password: '' }
  adminFormError.value = ''
}
async function createAdmin() {
  adminFormLoading.value = true
  adminFormError.value = ''
  try {
    const payload = {
      name: newAdmin.value.name,
      email: newAdmin.value.email,
      password: newAdmin.value.password,
      role: 'admin',
      dob: '',
      address: '',
    }
    await apiCreateAdmin(payload)
    closeAdminModal()
    fetchUsers()
  } catch (e: any) {
    adminFormError.value = e?.response?.data?.detail || 'Failed to create admin.'
  } finally {
    adminFormLoading.value = false
  }
}
async function handleDeleteAdmin(id: number) {
  if (!confirm('Are you sure you want to delete this admin?')) return
  await apiDeleteAdmin(id)
  fetchUsers()
}
type User = { id: number; name: string; email: string; is_active: boolean; role: string }
function toggleActive(user: User) {
  user.is_active = !user.is_active
}
function resetAccount(user: User) {
  alert(`Reset account for ${user.name}`)
}

const userStore = useUserStore()
const router = useRouter()

// Get current super admin info (from userStore or users array)
const superAdmin = computed(() => {
  // If userStore has the current user info:
  if (userStore.user && userStore.user.role === 'superadmin') {
    return userStore.user
  }
  // Fallback: find the first superadmin in users array
  return users.value.find((u: any) => u.role === 'superadmin') || {}
})

const showLogoutConfirm = ref(false)
function openLogoutConfirm() {
  showLogoutConfirm.value = true
}
function closeLogoutConfirm() {
  showLogoutConfirm.value = false
}
function confirmLogout() {
  userStore.logout()
  closeProfileMenu()
  closeLogoutConfirm()
  router.push('/login')
}
function handleLogout() {
  openLogoutConfirm()
}
</script>

<template>
  <!-- Header Bar -->
  <div class="w-full header-bar flex items-center justify-between px-8 py-4 z-50 sticky top-0">
    <span class="header-title font-extrabold text-2xl tracking-tight">AFP Super Admin</span>
    <div class="relative">
      <button
        @click="toggleProfileMenu"
        class="profile-btn flex items-center justify-center w-12 h-12 rounded-full bg-transparent hover:bg-emerald-50 transition focus:outline-none focus:ring-2 focus:ring-emerald-300"
      >
        <span class="material-symbols-outlined text-white" style="font-size: 2.75rem"
          >account_circle</span
        >
      </button>
      <transition name="fade-slide-x-inline">
        <div
          v-if="profileMenuOpen"
          class="absolute right-0 mt-2 w-40 bg-white rounded-xl shadow-lg border border-emerald-100 z-50"
        >
          <button
            @click="openLogoutConfirm"
            class="block w-full text-left px-4 py-3 bg-dark-green text-white font-semibold hover:bg-emerald-700 rounded-xl flex items-center gap-2 transition"
            aria-label="Logout"
          >
            <span class="material-symbols-outlined text-white">logout</span>Logout
          </button>
        </div>
      </transition>
    </div>
  </div>

  <!-- Navbar -->
  <div class="w-full flex justify-center mt-4 mb-6">
    <div class="navbar-modern flex flex-wrap items-center gap-2 md:gap-6">
      <button
        @click="setSection('admin-management')"
        :class="[
          'nav-link flex items-center gap-2',
          { active: activeSection === 'admin-management' },
        ]"
      >
        <span class="material-symbols-outlined text-emerald-500">admin_panel_settings</span>Admin
        Management
      </button>
      <button
        @click="setSection('profile')"
        :class="['nav-link flex items-center gap-2', { active: activeSection === 'profile' }]"
      >
        <span class="material-symbols-outlined text-emerald-500">person</span>Update Profile
      </button>
    </div>
  </div>

  <!-- Main Content Container -->
  <div class="flex justify-center items-start min-h-[60vh] pt-2 pb-16 overflow-y-auto max-h-screen">
    <div class="w-full max-w-4xl card-section mt-0 mx-auto px-4 md:px-8">
      <!-- Admin Management -->
      <section v-if="activeSection === 'admin-management'">
        <h2 class="section-title flex items-center gap-2">
          <span class="material-symbols-outlined text-emerald-500">admin_panel_settings</span>Admin
          Management
        </h2>
        <!-- Tab Navigation + Add Admin Button -->
        <div class="flex flex-wrap items-center gap-2 mb-6 justify-between">
          <div class="flex gap-2 flex-1">
            <button
              @click="
                () => {
                  setUserTab('admins')
                  page = 1
                }
              "
              :class="['tab-btn', { active: userTab === 'admins' }]"
            >
              Admins
            </button>
            <button
              @click="
                () => {
                  setUserTab('instructors')
                  page = 1
                }
              "
              :class="['tab-btn', { active: userTab === 'instructors' }]"
            >
              Instructors
            </button>
            <button
              @click="
                () => {
                  setUserTab('students')
                  page = 1
                }
              "
              :class="['tab-btn', { active: userTab === 'students' }]"
            >
              Students
            </button>
          </div>
          <button
            v-if="userTab === 'admins'"
            @click="openAdminModal"
            class="ml-auto bg-emerald-700 hover:bg-emerald-800 text-white rounded-full shadow-lg p-3 flex items-center justify-center transition"
          >
            <span class="material-symbols-outlined text-2xl">add</span>
            <span class="hidden md:inline ml-2 font-bold">Add Admin</span>
          </button>
        </div>
        <!-- User List -->
        <div class="space-y-4">
          <div v-if="usersLoading" class="text-center text-emerald-700 py-8">Loading admins...</div>
          <div v-if="usersError" class="text-center text-red-500 py-4">{{ usersError }}</div>
          <div
            v-for="user in pagedUsers"
            :key="user.id"
            class="user-card flex flex-col sm:flex-row sm:items-center justify-between bg-white rounded-xl shadow p-4 border border-emerald-100"
          >
            <div class="flex-1 min-w-0">
              <div class="font-bold text-emerald-800 truncate">{{ user.name }}</div>
              <div class="text-sm text-gray-600 truncate">{{ user.email }}</div>
            </div>
            <div class="flex items-center gap-4 mt-2 sm:mt-0">
              <span
                :class="user.is_active ? 'text-emerald-600' : 'text-red-500'"
                class="font-semibold"
                >{{ user.is_active ? 'Active' : 'Inactive' }}</span
              >
              <button
                @click="toggleActive(user)"
                class="action-btn px-3 py-1"
                :class="
                  user.is_active
                    ? 'bg-red-500 hover:bg-red-600'
                    : 'bg-emerald-700 hover:bg-emerald-800'
                "
              >
                {{ user.is_active ? 'Deactivate' : 'Activate' }}
              </button>
              <button
                @click="resetAccount(user)"
                class="action-btn bg-emerald-500 hover:bg-emerald-600 px-3 py-1"
              >
                Reset
              </button>
              <button
                v-if="userTab === 'admins'"
                @click="handleDeleteAdmin(user.id)"
                class="action-btn bg-red-600 hover:bg-red-700 px-3 py-1"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
        <!-- Pagination -->
        <div class="flex justify-center items-center gap-2 mt-6">
          <button
            @click="goToPage(page - 1)"
            :disabled="page === 1"
            class="px-3 py-1 rounded bg-emerald-100 text-emerald-700 font-bold disabled:opacity-50"
          >
            Prev
          </button>
          <span class="font-semibold">Page {{ page }} of {{ totalPages }}</span>
          <button
            @click="goToPage(page + 1)"
            :disabled="page === totalPages"
            class="px-3 py-1 rounded bg-emerald-100 text-emerald-700 font-bold disabled:opacity-50"
          >
            Next
          </button>
        </div>
        <!-- Modal for Creating Admin -->
        <div
          v-if="showAdminModal"
          class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40"
        >
          <div class="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md relative">
            <button
              @click="closeAdminModal"
              class="absolute top-3 right-3 text-gray-400 hover:text-red-500 text-2xl font-bold"
            >
              &times;
            </button>
            <h3 class="font-bold text-xl mb-4 text-emerald-800">Create Admin Account</h3>
            <form @submit.prevent="createAdmin" class="flex flex-col gap-4">
              <input
                v-model="newAdmin.name"
                type="text"
                placeholder="Name"
                class="input"
                required
              />
              <input
                v-model="newAdmin.email"
                type="email"
                placeholder="Email"
                class="input"
                required
              />
              <input
                v-model="newAdmin.password"
                type="password"
                placeholder="Password"
                class="input"
                required
              />
              <div v-if="adminFormError" class="text-red-500 text-sm">{{ adminFormError }}</div>
              <button
                type="submit"
                class="action-btn bg-emerald-700 hover:bg-emerald-800 w-full"
                :disabled="adminFormLoading"
              >
                <span v-if="adminFormLoading">Creating...</span>
                <span v-else>Create</span>
              </button>
            </form>
          </div>
        </div>
      </section>
      <!-- Update Profile (Super Admin Info) -->
      <section v-if="activeSection === 'profile'">
        <h2 class="section-title flex items-center gap-2">
          <span class="material-symbols-outlined text-emerald-500">person</span>Update Profile
        </h2>
        <div class="bg-emerald-50 rounded-xl p-6 max-w-lg mx-auto shadow space-y-4">
          <div>
            <label class="block text-emerald-700 font-semibold mb-1">Name</label>
            <div class="bg-white rounded px-4 py-2 border border-emerald-200">
              {{ superAdmin.name }}
            </div>
          </div>
          <div>
            <label class="block text-emerald-700 font-semibold mb-1">Email</label>
            <div class="bg-white rounded px-4 py-2 border border-emerald-200">
              {{ superAdmin.email }}
            </div>
          </div>
          <div>
            <label class="block text-emerald-700 font-semibold mb-1">Date of Birth</label>
            <div class="bg-white rounded px-4 py-2 border border-emerald-200">
              {{ superAdmin.dob || '-' }}
            </div>
          </div>
          <div>
            <label class="block text-emerald-700 font-semibold mb-1">Address</label>
            <div class="bg-white rounded px-4 py-2 border border-emerald-200">
              {{ superAdmin.address || '-' }}
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>

  <!-- Logout Confirmation Modal -->
  <div
    v-if="showLogoutConfirm"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40"
  >
    <div class="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-sm relative">
      <h3 class="font-bold text-xl mb-4 text-emerald-800">Confirm Logout</h3>
      <p class="mb-6 text-gray-700">Are you sure you want to log out?</p>
      <div class="flex justify-end gap-3">
        <button
          @click="closeLogoutConfirm"
          class="px-4 py-2 rounded font-semibold bg-gray-100 text-gray-700 hover:bg-gray-200"
        >
          Cancel
        </button>
        <button
          @click="confirmLogout"
          class="px-4 py-2 rounded font-semibold bg-red-600 text-white hover:bg-red-700"
        >
          Logout
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined');

.header-bar {
  background: #065f46;
  color: #fff;
  box-shadow: 0 4px 24px 0 rgba(16, 185, 129, 0.1);
}
.header-title {
  color: #fff !important;
}
.profile-btn {
  background: transparent !important;
}
.bg-dark-green {
  background-color: #065f46 !important;
}
.nav-link {
  @apply text-emerald-800 font-semibold px-4 py-2 rounded-full hover:bg-emerald-50 transition cursor-pointer shadow-sm;
  margin: 0 0.25rem;
  display: flex;
  align-items: center;
}
.nav-link.active {
  @apply bg-emerald-100 text-emerald-700;
}
.group:hover .group-hover\:opacity-100 {
  opacity: 1 !important;
}
.group:hover .group-hover\:pointer-events-auto {
  pointer-events: auto !important;
}
.card-section {
  @apply bg-white rounded-3xl shadow-2xl border border-emerald-100 p-8 md:p-10 mb-8;
  transition: box-shadow 0.2s;
}
.section-title {
  @apply text-xl md:text-2xl font-bold text-emerald-700 mb-4;
  transition: box-shadow 0.2s;
}
.input {
  @apply border border-emerald-200 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-400;
}
.action-btn {
  @apply px-6 py-2 rounded-full text-white font-bold flex items-center gap-2 shadow hover:shadow-lg transition;
}
.fade-slide-x-inline-enter-active,
.fade-slide-x-inline-leave-active {
  transition:
    opacity 0.2s,
    transform 0.2s;
  display: inline-block;
}
.fade-slide-x-inline-enter-from,
.fade-slide-x-inline-leave-to {
  opacity: 0;
  transform: translateX(-16px);
}
.fade-slide-x-inline-enter-to,
.fade-slide-x-inline-leave-from {
  opacity: 1;
  transform: translateX(0);
}
.tab-btn {
  @apply px-4 py-2 rounded-full font-semibold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 transition;
}
.tab-btn.active {
  @apply bg-emerald-700 text-white shadow;
}
.user-card {
  @apply flex flex-col sm:flex-row sm:items-center justify-between bg-white rounded-xl shadow p-4 border border-emerald-100;
}
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-to,
.modal-leave-from {
  opacity: 1;
}
</style>
