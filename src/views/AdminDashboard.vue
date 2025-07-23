<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import { onMounted, onBeforeUnmount } from 'vue'
import {
  getSchools,
  createSchool,
  updateSchool as updateSchoolApi,
  archiveSchool as apiArchiveSchool,
  getInstructors,
  approveInstructor as apiApproveInstructor,
  updateInstructor as apiUpdateInstructor,
  unarchiveSchool as apiUnarchiveSchool,
} from '@/services/api'
<<<<<<< HEAD
import api from '@/services/api'
=======
import axios from 'axios'
>>>>>>> d200206 (Initial commit)
import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'
import { useSnackbarStore } from '@/stores/snackbar'
import Snackbar from '@/components/common/Snackbar.vue'

// Type definitions
interface Instructor {
  id: number
  name: string
  email: string
  is_active: boolean
  school: string[]
}

interface Student {
  id: number
  name: string
  email: string
  school: string
  is_active: boolean
  studentId: string // studentId from backend, not id
}

interface School {
  id: number
  name: string
  archived: boolean
}

interface EditSchool {
  id: number | null
  name: string
}

// Reactive data
const instructors = ref<Instructor[]>([])
const students = ref<Student[]>([])
const schools = ref<School[]>([])

const activeSection = ref('approve-instructors')
const filterSchool = ref('All')
const filterAttendance = ref('All')
const newSchool = ref('')
const editSchool = ref<EditSchool>({ id: null, name: '' })

// Modal for Add School
const showSchoolModal = ref(false)
function openSchoolModal() {
  showSchoolModal.value = true
}
function closeSchoolModal() {
  showSchoolModal.value = false
  newSchool.value = ''
}

// Modal for assigning school to instructor
const showAssignSchoolModal = ref(false)
const assignSchoolSearch = ref('')
const assignSchoolInstructor = ref<Instructor | null>(null)
const assignSchoolSelections = ref<string[]>([])
const filteredAssignSchools = computed(() => {
  const search = assignSchoolSearch.value.trim().toLowerCase()
  return schools.value.filter(
    (s) => !s.archived && (!search || s.name.toLowerCase().includes(search)),
  )
})
function openAssignSchoolModal(instructor: Instructor) {
  assignSchoolInstructor.value = instructor
  assignSchoolSearch.value = ''
  assignSchoolSelections.value = instructor.school ? [...instructor.school] : []
  showAssignSchoolModal.value = true
}
function closeAssignSchoolModal() {
  showAssignSchoolModal.value = false
  assignSchoolInstructor.value = null
  assignSchoolSearch.value = ''
  assignSchoolSelections.value = []
}

// Profile menu and logout modal logic (like SuperAdminDashboard)
const profileMenuOpen = ref(false)
function toggleProfileMenu() {
  profileMenuOpen.value = !profileMenuOpen.value
}
function closeProfileMenu() {
  profileMenuOpen.value = false
}
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

// Snackbar for notifications
// REMOVE the local snackbar ref and showSnackbar function

// User store and router
const userStore = useUserStore()
const router = useRouter()
const snackbarStore = useSnackbarStore()

function setSection(section: string) {
  activeSection.value = section
}
function resetAccount(user: Instructor | Student) {
  snackbarStore.trigger(`Reset account for ${user.name}`, 'warning')
}

async function fetchSchools() {
  try {
    const { data } = await getSchools()
    schools.value = data
  } catch (e) {
    snackbarStore.trigger('Failed to load schools', 'error')
  }
}

async function addSchool() {
  if (newSchool.value) {
    try {
      const { data } = await createSchool({ name: newSchool.value })
      schools.value.push(data)
      newSchool.value = ''
      closeSchoolModal()
      snackbarStore.trigger('School added!', 'success')
    } catch (e) {
      snackbarStore.trigger('Failed to add school', 'error')
    }
  }
}

function startEditSchool(school: School) {
  editSchool.value = { ...school }
}

async function updateSchool() {
  const s = schools.value.find((s) => s.id === editSchool.value.id)
  if (s && editSchool.value.name) {
    try {
      const { data } = await updateSchoolApi(s.id, {
        name: editSchool.value.name,
        archived: s.archived,
      })
      s.name = data.name
      editSchool.value = { id: null, name: '' }
      snackbarStore.trigger('School updated!', 'success')
    } catch (e) {
      snackbarStore.trigger('Failed to update school', 'error')
    }
  }
}

async function archiveSchool(school: School) {
  try {
    await apiArchiveSchool(school.id)
    school.archived = true
    snackbarStore.trigger('School archived!', 'success')
  } catch (e) {
    snackbarStore.trigger('Failed to archive school', 'error')
  }
}

async function unarchiveSchool(school: School) {
  try {
    await apiUnarchiveSchool(school.id)
    school.archived = false
    snackbarStore.trigger('School unarchived!', 'success')
  } catch (e) {
    snackbarStore.trigger('Failed to unarchive school', 'error')
  }
}

async function fetchInstructors() {
  try {
    const { data } = await getInstructors()
    instructors.value = data.map((inst: any) => ({
      id: inst.id,
      name: inst.name,
      email: inst.email,
      is_active: inst.is_active,
      school: inst.school
        ? Array.isArray(inst.school)
          ? inst.school
          : inst.school.split(',').filter(Boolean)
        : [],
    }))
  } catch (e) {
    snackbarStore.trigger('Failed to load instructors', 'error')
  }
}

async function approveInstructor(inst: Instructor) {
  try {
    await apiApproveInstructor(inst.id)
    inst.is_active = true
    snackbarStore.trigger('Instructor approved!', 'success')
    fetchInstructors()
  } catch (e) {
    snackbarStore.trigger('Failed to approve instructor', 'error')
  }
}

async function assignSchoolsToInstructor() {
  if (assignSchoolInstructor.value) {
    try {
      await apiUpdateInstructor(assignSchoolInstructor.value.id, {
        school: assignSchoolSelections.value.join(','),
      })
      assignSchoolInstructor.value.school = [...assignSchoolSelections.value]
      snackbarStore.trigger(`Assigned school(s) to ${assignSchoolInstructor.value.name}`, 'success')
      closeAssignSchoolModal()
      fetchInstructors()
    } catch (e) {
      snackbarStore.trigger('Failed to assign school(s)', 'error')
    }
  }
}

async function fetchStudents() {
  try {
<<<<<<< HEAD
    const { data } = await api.get('/api/users')
=======
    const { data } = await axios.get('/api/users')
>>>>>>> d200206 (Initial commit)
    students.value = data
      .filter((u: any) => u.role === 'student')
      .map((u: any) => ({
        id: u.id,
        name: u.name,
        email: u.email,
        school: u.school || '',
        is_active: u.is_active,
        studentId: u.studentId || '', // Use studentId from backend
      }))
  } catch (e) {
    snackbarStore.trigger('Failed to load students', 'error')
  }
}

const filteredStudents = computed(() => {
  let list = students.value
  if (filterSchool.value !== 'All') list = list.filter((s) => s.school === filterSchool.value)
  return list
})
const filteredAttendance = computed(() => {
  // Placeholder: filter by present/absent
  return filteredStudents.value
})
const page = ref(1)
const itemsPerPage = 10
const paginatedAttendance = computed(() => {
  const start = (page.value - 1) * itemsPerPage
  return filteredAttendance.value.slice(start, start + itemsPerPage)
})
const totalPages = computed(() => {
  return Math.ceil(filteredAttendance.value.length / itemsPerPage) || 1
})
function goToPage(p: number) {
  if (p >= 1 && p <= totalPages.value) page.value = p
}

// Pagination for View Students
const studentPage = ref(1)
const studentsPerPage = 10
const paginatedStudents = computed(() => {
  const start = (studentPage.value - 1) * studentsPerPage
  return filteredStudents.value.slice(start, start + studentsPerPage)
})
const studentTotalPages = computed(() => {
  return Math.ceil(filteredStudents.value.length / studentsPerPage) || 1
})
function goToStudentPage(p: number) {
  if (p >= 1 && p <= studentTotalPages.value) studentPage.value = p
}

// Pagination for Approve Instructors
const instructorPage = ref(1)
const instructorsPerPage = 10
const paginatedInstructors = computed(() => {
  const start = (instructorPage.value - 1) * instructorsPerPage
  return instructors.value.slice(start, start + instructorsPerPage)
})
const instructorTotalPages = computed(() => {
  return Math.ceil(instructors.value.length / instructorsPerPage) || 1
})
function goToInstructorPage(p: number) {
  if (p >= 1 && p <= instructorTotalPages.value) instructorPage.value = p
}
// Pagination for Manage Schools
const schoolPage = ref(1)
const schoolsPerPage = 10
const schoolStatusFilter = ref('All')
const schoolSearch = ref('')

// Filtered and searched schools
const filteredSchools = computed(() => {
  let list = schools.value
  if (schoolStatusFilter.value === 'Active') list = list.filter((s) => !s.archived)
  else if (schoolStatusFilter.value === 'Archived') list = list.filter((s) => s.archived)
  if (schoolSearch.value.trim()) {
    const search = schoolSearch.value.trim().toLowerCase()
    list = list.filter((s) => s.name.toLowerCase().includes(search))
  }
  return list
})
const paginatedSchools = computed(() => {
  const start = (schoolPage.value - 1) * schoolsPerPage
  return filteredSchools.value.slice(start, start + schoolsPerPage)
})
const schoolTotalPages = computed(() => {
  return Math.ceil(filteredSchools.value.length / schoolsPerPage) || 1
})
function goToSchoolPage(p: number) {
  if (p >= 1 && p <= schoolTotalPages.value) schoolPage.value = p
}

// Report menu dropdown logic with delay on close
const reportMenuOpen = ref(false)
let reportMenuTimeout: ReturnType<typeof setTimeout> | null = null
function openReportMenu() {
  if (reportMenuTimeout) clearTimeout(reportMenuTimeout)
  reportMenuOpen.value = true
}
function closeReportMenu() {
  reportMenuTimeout = setTimeout(() => {
    reportMenuOpen.value = false
  }, 180)
}

const showActionsMenu = ref<number | null>(null)
const actionsMenuRef = ref<HTMLElement | null>(null)
function openActionsMenu(id: number) {
  showActionsMenu.value = showActionsMenu.value === id ? null : id
}
function closeActionsMenu() {
  showActionsMenu.value = null
}

function handleClickOutsideActionsMenu(event: MouseEvent) {
  if (!actionsMenuRef.value) return
  if (showActionsMenu.value !== null && !actionsMenuRef.value.contains(event.target as Node)) {
    closeActionsMenu()
  }
}
onMounted(() => {
  fetchSchools()
  fetchInstructors()
  fetchStudents()
  document.addEventListener('click', handleClickOutsideActionsMenu)
})
onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutsideActionsMenu)
})

const assignSchoolModalRef = ref<HTMLElement | null>(null)
function handleClickOutsideAssignSchoolModal(event: MouseEvent) {
  if (
    showAssignSchoolModal.value &&
    assignSchoolModalRef.value &&
    !assignSchoolModalRef.value.contains(event.target as Node)
  ) {
    closeAssignSchoolModal()
  }
}
watch(showAssignSchoolModal, (val) => {
  if (val) {
    document.addEventListener('mousedown', handleClickOutsideAssignSchoolModal)
  } else {
    document.removeEventListener('mousedown', handleClickOutsideAssignSchoolModal)
  }
})

// Add attendanceRecords and modal state for details
const attendanceRecords = ref<Record<string, any[]>>({})
const attendanceModal = ref({ show: false, student: null as Student | null, records: [] as any[] })
const attendanceFilterDate = ref('')
const filteredAttendanceRecords = computed(() => {
  return attendanceModal.value.records.filter((record) => {
    if (attendanceFilterDate.value) {
      const recordDate = formatDate(record.date)
      const filterDate = formatDate(attendanceFilterDate.value)
      return recordDate === filterDate
    }
    return true
  })
})

// Helper to count presents/absences for a student
function countAttendance(studentId: string, status: 'present' | 'absent'): number {
  const records = attendanceRecords.value[studentId] || []
  return records.filter((r) => r.status === status).length
}

// Fetch attendance records for all students on mount
async function fetchAttendanceRecords(studentId: string) {
<<<<<<< HEAD
  const { data } = await api.get(`/api/attendance/by-student/${studentId}`)
=======
  const { data } = await axios.get(`/api/attendance/by-student/${studentId}`)
>>>>>>> d200206 (Initial commit)
  attendanceRecords.value[studentId] = data
  return data
}

async function openAttendanceModal(student: Student) {
  attendanceModal.value.show = true
  attendanceModal.value.student = student
  attendanceModal.value.records = await fetchAttendanceRecords(student.studentId)
}
function closeAttendanceModal() {
  attendanceModal.value.show = false
  attendanceModal.value.student = null
  attendanceModal.value.records = []
}

function formatDate(date: unknown): string {
  const d = (date ?? '').toString()
  if (d && !isNaN(Date.parse(d))) {
    try {
      return new Date(d).toLocaleDateString()
    } catch {
      return '-'
    }
  }
  return '-'
}
function formatTime(date: unknown): string {
  const d = (date ?? '').toString()
  if (d && !isNaN(Date.parse(d))) {
    try {
      return new Date(d).toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      })
    } catch {
      return '-'
    }
  }
  return '-'
}

// Add for List of Schools report (Instructor style)
const schoolsReport = computed(() => schools.value)
function downloadSchoolsReport() {
  const doc = new jsPDF()
  doc.setFontSize(14)
  doc.text('List of Schools', 14, 18)
  const headers = [['#', 'School', 'Status']]
  const rows = schoolsReport.value.map((s, idx) => [
    idx + 1,
    s.name,
    s.archived ? 'Archived' : 'Active',
  ])
  autoTable(doc, {
    head: headers,
    body: rows,
    startY: 24,
    styles: { fontSize: 11 },
    headStyles: { fillColor: [22, 163, 74] },
    margin: { left: 14, right: 14 },
  })
  const pdfBlob = doc.output('blob')
  const url = URL.createObjectURL(pdfBlob)
  window.open(url, '_blank')
}
// Add for List of Students report (Instructor style)
const reportSchoolFilter = ref('')
const filteredReportStudents = computed(() => {
  if (!reportSchoolFilter.value) return students.value
  return students.value.filter((s) => s.school === reportSchoolFilter.value)
})
function downloadReport() {
  const doc = new jsPDF()
  doc.setFontSize(14)
  doc.text('Student Report', 14, 18)
  const headers = [['#', 'Name', 'Email', 'Student ID', 'School', 'Status']]
  const rows = filteredReportStudents.value.map((s, idx) => [
    idx + 1,
    s.name,
    s.email,
    s.studentId,
    s.school || '',
    s.is_active ? 'Active' : 'Pending Approval',
  ])
  autoTable(doc, {
    head: headers,
    body: rows,
    startY: 24,
    styles: { fontSize: 11 },
    headStyles: { fillColor: [22, 163, 74] },
    margin: { left: 14, right: 14 },
  })
  const pdfBlob = doc.output('blob')
  const url = URL.createObjectURL(pdfBlob)
  window.open(url, '_blank')
}
// Students per School report
const studentsPerSchoolFilter = ref('')
const filteredStudentsPerSchool = computed(() => {
  if (!studentsPerSchoolFilter.value) return students.value
  return students.value.filter((s) => s.school === studentsPerSchoolFilter.value)
})
const selectedStudentsPerSchool = ref<number[]>([])
const allStudentsPerSchoolSelected = computed(
  () =>
    filteredStudentsPerSchool.value.length > 0 &&
    filteredStudentsPerSchool.value.every((s) => selectedStudentsPerSchool.value.includes(s.id)),
)
function toggleSelectAllStudentsPerSchool() {
  if (allStudentsPerSchoolSelected.value) {
    selectedStudentsPerSchool.value = []
  } else {
    selectedStudentsPerSchool.value = filteredStudentsPerSchool.value.map((s) => s.id)
  }
}
function toggleStudentPerSchool(id: number) {
  if (selectedStudentsPerSchool.value.includes(id)) {
    selectedStudentsPerSchool.value = selectedStudentsPerSchool.value.filter((sid) => sid !== id)
  } else {
    selectedStudentsPerSchool.value.push(id)
  }
}
function downloadStudentsPerSchool() {
  if (selectedStudentsPerSchool.value.length === 0) {
    snackbarStore.trigger('Please select at least one student to generate the report.', 'warning')
    return
  }
  const selected = filteredStudentsPerSchool.value.filter((s) =>
    selectedStudentsPerSchool.value.includes(s.id),
  )
  const doc = new jsPDF()
  doc.setFontSize(14)
  doc.text('Students per School', 14, 18)
  const headers = [['#', 'Name', 'Email', 'Student ID', 'School', 'Status']]
  const rows = selected.map((s, idx) => [
    idx + 1,
    s.name,
    s.email,
    s.studentId,
    s.school || '',
    s.is_active ? 'Active' : 'Pending Approval',
  ])
  autoTable(doc, {
    head: headers,
    body: rows,
    startY: 24,
    styles: { fontSize: 11 },
    headStyles: { fillColor: [22, 163, 74] },
    margin: { left: 14, right: 14 },
  })
  const pdfBlob = doc.output('blob')
  const url = URL.createObjectURL(pdfBlob)
  window.open(url, '_blank')
}
// Students with Attendance Summary per School report
const summarySchoolFilter = ref('')
const filteredSummaryStudents = computed(() => {
  if (!summarySchoolFilter.value) return students.value
  return students.value.filter((s) => s.school === summarySchoolFilter.value)
})
function downloadSummaryStudents() {
  const doc = new jsPDF()
  doc.setFontSize(14)
  doc.text('Students w/ Attendance Summary', 14, 18)
  const headers = [
    ['#', 'Name', 'Email', 'Student ID', 'School', 'Total Presents', 'Total Absences'],
  ]
  const rows = filteredSummaryStudents.value.map((s, idx) => [
    idx + 1,
    s.name,
    s.email,
    s.studentId,
    s.school || '',
    countAttendance(s.studentId, 'present'),
    countAttendance(s.studentId, 'absent'),
  ])
  autoTable(doc, {
    head: headers,
    body: rows,
    startY: 24,
    styles: { fontSize: 11 },
    headStyles: { fillColor: [22, 163, 74] },
    margin: { left: 14, right: 14 },
  })
  const pdfBlob = doc.output('blob')
  const url = URL.createObjectURL(pdfBlob)
  window.open(url, '_blank')
}
// Summary per Student report
const summaryPerStudentSchoolFilter = ref('')
const filteredSummaryPerStudent = computed(() => {
  if (!summaryPerStudentSchoolFilter.value) return students.value
  return students.value.filter((s) => s.school === summaryPerStudentSchoolFilter.value)
})
const selectedSummaryPerStudent = ref<number[]>([])
const allSummaryPerStudentSelected = computed(
  () =>
    filteredSummaryPerStudent.value.length > 0 &&
    filteredSummaryPerStudent.value.every((s) => selectedSummaryPerStudent.value.includes(s.id)),
)
function toggleSelectAllSummaryPerStudent() {
  if (allSummaryPerStudentSelected.value) {
    selectedSummaryPerStudent.value = []
  } else {
    selectedSummaryPerStudent.value = filteredSummaryPerStudent.value.map((s) => s.id)
  }
}
function toggleSummaryPerStudent(id: number) {
  if (selectedSummaryPerStudent.value.includes(id)) {
    selectedSummaryPerStudent.value = selectedSummaryPerStudent.value.filter((sid) => sid !== id)
  } else {
    selectedSummaryPerStudent.value.push(id)
  }
}
function downloadSummaryPerStudent() {
  if (selectedSummaryPerStudent.value.length === 0) {
    snackbarStore.trigger('Please select at least one student to generate the report.', 'warning')
    return
  }
  const selected = filteredSummaryPerStudent.value.filter((s) =>
    selectedSummaryPerStudent.value.includes(s.id),
  )
  const doc = new jsPDF()
  doc.setFontSize(14)
  doc.text('Summary per Student', 14, 18)
  const headers = [
    ['#', 'Name', 'Email', 'Student ID', 'School', 'Total Presents', 'Total Absences'],
  ]
  const rows = selected.map((s, idx) => [
    idx + 1,
    s.name,
    s.email,
    s.studentId,
    s.school || '',
    countAttendance(s.studentId, 'present'),
    countAttendance(s.studentId, 'absent'),
  ])
  autoTable(doc, {
    head: headers,
    body: rows,
    startY: 24,
    styles: { fontSize: 11 },
    headStyles: { fillColor: [22, 163, 74] },
    margin: { left: 14, right: 14 },
  })
  const pdfBlob = doc.output('blob')
  const url = URL.createObjectURL(pdfBlob)
  window.open(url, '_blank')
}
</script>

<template>
  <div class="w-full header-bar flex items-center justify-between px-8 py-4 z-50 sticky top-0">
    <span class="header-title font-extrabold text-2xl tracking-tight">AFP Admin</span>
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
  <div class="w-full flex justify-center mt-4 mb-6">
    <div class="navbar-modern flex flex-wrap items-center gap-2 md:gap-6">
      <button
        @click="setSection('approve-instructors')"
        :class="[
          'nav-link flex items-center gap-2',
          { active: activeSection === 'approve-instructors' },
        ]"
      >
        <span class="material-symbols-outlined text-emerald-500">verified_user</span>Approve
        Instructors
      </button>
      <button
        @click="setSection('manage-schools')"
        :class="[
          'nav-link flex items-center gap-2',
          { active: activeSection === 'manage-schools' },
        ]"
      >
        <span class="material-symbols-outlined text-emerald-500">school</span>Manage Schools
      </button>
      <button
        @click="setSection('students')"
        :class="['nav-link flex items-center gap-2', { active: activeSection === 'students' }]"
      >
        <span class="material-symbols-outlined text-emerald-500">groups</span>View Students
      </button>
      <button
        @click="setSection('attendance-summary')"
        :class="[
          'nav-link flex items-center gap-2',
          { active: activeSection === 'attendance-summary' },
        ]"
      >
        <span class="material-symbols-outlined text-emerald-500">summarize</span>Attendance Summary
      </button>
      <div
        class="relative group"
        @mouseenter="openReportMenu"
        @mouseleave="closeReportMenu"
        @focusin="openReportMenu"
        @focusout="closeReportMenu"
      >
        <button class="nav-link flex items-center gap-2" type="button">
          <span class="material-symbols-outlined text-emerald-500">description</span>Generate Report
          <svg class="w-4 h-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M19 9l-7 7-7-7"
            />
          </svg>
        </button>
        <div
          v-if="reportMenuOpen"
          class="absolute right-0 mt-2 w-56 bg-white border border-emerald-100 rounded-xl shadow-lg z-50"
        >
          <button
            @click="setSection('report-schools')"
            class="block w-full text-left px-4 py-2 hover:bg-emerald-50 flex items-center gap-2"
          >
            <span class="material-symbols-outlined text-emerald-500">school</span>List of Schools
          </button>
          <button
            @click="setSection('report-students-per-school')"
            class="block w-full text-left px-4 py-2 hover:bg-emerald-50 flex items-center gap-2"
          >
            <span class="material-symbols-outlined text-emerald-500">groups</span>Students per
            School
          </button>
          <button
            @click="setSection('report-students-summary')"
            class="block w-full text-left px-4 py-2 hover:bg-emerald-50 flex items-center gap-2"
          >
            <span class="material-symbols-outlined text-emerald-500">bar_chart</span>Students w/
            Attendance Summary
          </button>
          <button
            @click="setSection('report-summary-each-student')"
            class="block w-full text-left px-4 py-2 hover:bg-emerald-50 flex items-center gap-2"
          >
            <span class="material-symbols-outlined text-emerald-500">person_search</span>Summary per
            Student
          </button>
          <button
            @click="setSection('report-students')"
            class="block w-full text-left px-4 py-2 hover:bg-emerald-50 flex items-center gap-2"
          >
            <span class="material-symbols-outlined text-emerald-500">list</span>List of Students
          </button>
        </div>
      </div>
    </div>
  </div>
  <div class="flex justify-center items-start min-h-[60vh] pt-2 pb-16 overflow-y-auto max-h-screen">
    <div class="w-full max-w-6xl card-section mt-0 mx-auto px-4 md:px-8">
      <!-- Approve Instructors -->
      <section v-if="activeSection === 'approve-instructors'">
        <h2 class="section-title flex items-center gap-2">
          <span class="material-symbols-outlined text-emerald-500">verified_user</span>Approve
          Instructor Accounts
        </h2>
        <table class="w-full mb-4">
          <thead>
            <tr class="text-left text-emerald-700">
              <th>#</th>
              <th>Name</th>
              <th>Email</th>
              <th>School</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(instructor, idx) in paginatedInstructors"
              :key="instructor.id"
              class="border-b"
            >
              <td>{{ (instructorPage - 1) * instructorsPerPage + idx + 1 }}</td>
              <td>{{ instructor.name }}</td>
              <td>{{ instructor.email }}</td>
              <td>
                <span v-if="instructor.school && instructor.school.length">
                  <span
                    v-for="(schoolName, i) in instructor.school"
                    :key="schoolName"
                    class="inline-block bg-emerald-100 text-emerald-800 rounded-full px-3 py-1 text-xs font-semibold mr-1 mb-1"
                  >
                    {{ schoolName }}
                  </span>
                </span>
                <span v-else class="text-gray-400 italic">No school assigned</span>
              </td>
              <td>
                <span :class="instructor.is_active ? 'text-emerald-600' : 'text-red-500'">{{
                  instructor.is_active ? 'Active' : 'Inactive'
                }}</span>
              </td>
              <td class="flex gap-2 py-2 relative">
                <button
                  v-if="!instructor.is_active"
                  @click="approveInstructor(instructor)"
                  class="action-btn-mini bg-emerald-700 hover:bg-emerald-800"
                  aria-label="Approve"
                >
                  Approve
                </button>
                <button
                  v-if="!instructor.is_active"
                  @click="resetAccount(instructor)"
                  class="action-btn-mini bg-red-500 hover:bg-red-600"
                  aria-label="Reject"
                >
                  Reject
                </button>
                <button
                  v-if="instructor.is_active && !instructor.school.length"
                  @click="openAssignSchoolModal(instructor)"
                  class="icon-btn"
                  aria-label="Assign School"
                >
                  <span class="material-symbols-outlined">school</span>
                </button>
                <button
                  v-if="instructor.is_active && instructor.school.length"
                  @click="openActionsMenu(instructor.id)"
                  class="icon-btn"
                  aria-label="More actions"
                >
                  <span class="material-symbols-outlined">more_vert</span>
                </button>
                <div
                  v-if="showActionsMenu === instructor.id"
                  ref="actionsMenuRef"
                  class="absolute z-50 bg-white border border-emerald-100 rounded-xl shadow-lg mt-2 right-0 min-w-[140px]"
                >
                  <button
                    @click="
                      () => {
                        closeActionsMenu()
                        openAssignSchoolModal(instructor)
                      }
                    "
                    class="block w-full text-left px-4 py-2 hover:bg-emerald-50 flex items-center gap-2"
                  >
                    <span class="material-symbols-outlined text-emerald-500">school</span>Add School
                  </button>
                  <button
                    @click="
                      () => {
                        closeActionsMenu()
                        resetAccount(instructor)
                      }
                    "
                    class="block w-full text-left px-4 py-2 hover:bg-emerald-50 flex items-center gap-2"
                  >
                    <span class="material-symbols-outlined text-emerald-500">restart_alt</span>Reset
                    Account
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="flex justify-center items-center gap-2 mt-6">
          <button
            @click="goToInstructorPage(instructorPage - 1)"
            :disabled="instructorPage === 1"
            class="px-3 py-1 rounded bg-emerald-100 text-emerald-700 font-bold disabled:opacity-50"
          >
            Prev
          </button>
          <span class="font-semibold">Page {{ instructorPage }} of {{ instructorTotalPages }}</span>
          <button
            @click="goToInstructorPage(instructorPage + 1)"
            :disabled="instructorPage === instructorTotalPages"
            class="px-3 py-1 rounded bg-emerald-100 text-emerald-700 font-bold disabled:opacity-50"
          >
            Next
          </button>
        </div>
      </section>
      <!-- Manage Schools -->
      <section v-if="activeSection === 'manage-schools'">
        <div class="flex items-center justify-between mb-4">
          <h2 class="section-title flex items-center gap-2 mb-0">
            <span class="material-symbols-outlined text-emerald-500">school</span>Manage Schools
          </h2>
          <button
            @click="openSchoolModal"
            class="ml-auto bg-emerald-700 hover:bg-emerald-800 text-white rounded-full shadow-lg p-3 flex items-center justify-center transition"
          >
            <span class="material-symbols-outlined text-2xl">add</span>
            <span class="hidden md:inline ml-2 font-bold">Add School</span>
          </button>
        </div>
        <!-- Filter and Search -->
        <div class="flex flex-wrap gap-4 items-center mb-4">
          <label class="font-semibold text-emerald-800">Status:</label>
          <select v-model="schoolStatusFilter" class="input">
            <option>All</option>
            <option>Active</option>
            <option>Archived</option>
          </select>
          <input
            v-model="schoolSearch"
            type="text"
            placeholder="Search schools..."
            class="input flex-1 min-w-[200px]"
          />
        </div>
        <div
          v-if="showSchoolModal"
          class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40"
        >
          <div class="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md relative">
            <button
              @click="closeSchoolModal"
              class="absolute top-3 right-3 text-gray-400 hover:text-red-500 text-2xl font-bold"
            >
              &times;
            </button>
            <h3 class="font-bold text-xl mb-4 text-emerald-800">Create School</h3>
            <form @submit.prevent="addSchool" class="flex flex-col gap-4">
              <input
                v-model="newSchool"
                type="text"
                placeholder="New School Name"
                class="input"
                required
              />
              <button
                type="submit"
                class="action-btn-normal bg-emerald-700 hover:bg-emerald-800 mx-auto block"
              >
                Add
              </button>
            </form>
          </div>
        </div>
        <table class="w-full mb-4">
          <thead>
            <tr class="text-left text-emerald-700">
              <th>#</th>
              <th>Name</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(schoolItem, idx) in paginatedSchools" :key="schoolItem.id" class="border-b">
              <td>{{ (schoolPage - 1) * schoolsPerPage + idx + 1 }}</td>
              <td>
                <span v-if="editSchool.id !== schoolItem.id">{{ schoolItem.name }}</span>
                <input v-else v-model="editSchool.name" class="input" />
              </td>
              <td>
                <span :class="schoolItem.archived ? 'text-red-500' : 'text-emerald-600'">
                  {{ schoolItem.archived ? 'Archived' : 'Active' }}
                </span>
              </td>
              <td class="flex gap-2 py-2">
                <button
                  v-if="!schoolItem.archived && editSchool.id !== schoolItem.id"
                  @click="startEditSchool(schoolItem)"
                  class="action-btn bg-emerald-500 hover:bg-emerald-600 px-3 py-1"
                >
                  Edit
                </button>
                <button
                  v-if="editSchool.id === schoolItem.id"
                  @click="updateSchool"
                  class="action-btn bg-emerald-700 hover:bg-emerald-800 px-3 py-1"
                >
                  Update
                </button>
                <button
                  v-if="!schoolItem.archived"
                  @click="archiveSchool(schoolItem)"
                  class="action-btn bg-red-500 hover:bg-red-600 px-3 py-1"
                >
                  Archive
                </button>
                <button
                  v-if="schoolItem.archived"
                  @click="unarchiveSchool(schoolItem)"
                  class="action-btn bg-emerald-700 hover:bg-emerald-800 px-3 py-1"
                >
                  Unarchive
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="flex justify-center items-center gap-2 mt-6">
          <button
            @click="goToSchoolPage(schoolPage - 1)"
            :disabled="schoolPage === 1"
            class="px-3 py-1 rounded bg-emerald-100 text-emerald-700 font-bold disabled:opacity-50"
          >
            Prev
          </button>
          <span class="font-semibold">Page {{ schoolPage }} of {{ schoolTotalPages }}</span>
          <button
            @click="goToSchoolPage(schoolPage + 1)"
            :disabled="schoolPage === schoolTotalPages"
            class="px-3 py-1 rounded bg-emerald-100 text-emerald-700 font-bold disabled:opacity-50"
          >
            Next
          </button>
        </div>
      </section>
      <!-- View Students per School -->
      <section v-if="activeSection === 'students'">
        <h2 class="section-title flex items-center gap-2">
          <span class="material-symbols-outlined text-emerald-500">groups</span>View Students per
          School
        </h2>
        <div class="flex gap-4 items-center mb-4">
          <label class="font-semibold text-emerald-800">School:</label>
          <select v-model="filterSchool" class="input">
            <option>All</option>
            <option v-for="schoolFilter in schools" :key="schoolFilter.id">
              {{ schoolFilter.name }}
            </option>
          </select>
        </div>
        <table class="w-full mb-4">
          <thead>
            <tr class="text-left text-emerald-700">
              <th>#</th>
              <th>Name</th>
              <th>Email</th>
              <th>School</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(student, idx) in paginatedStudents" :key="student.id" class="border-b">
              <td>{{ (studentPage - 1) * studentsPerPage + idx + 1 }}</td>
              <td>{{ student.name }}</td>
              <td>{{ student.email }}</td>
              <td>
                <span>{{ student.school }}</span>
              </td>
              <td>
                <span :class="student.is_active ? 'text-emerald-600' : 'text-red-500'">{{
                  student.is_active ? 'Active' : 'Inactive'
                }}</span>
              </td>
              <td class="flex gap-2 py-2">
                <button
                  @click="resetAccount(student)"
                  class="action-btn bg-emerald-500 hover:bg-emerald-600 px-3 py-1"
                >
                  Reset
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="flex justify-center items-center gap-2 mt-6">
          <button
            @click="goToStudentPage(studentPage - 1)"
            :disabled="studentPage === 1"
            class="px-3 py-1 rounded bg-emerald-100 text-emerald-700 font-bold disabled:opacity-50"
          >
            Prev
          </button>
          <span class="font-semibold">Page {{ studentPage }} of {{ studentTotalPages }}</span>
          <button
            @click="goToStudentPage(studentPage + 1)"
            :disabled="studentPage === studentTotalPages"
            class="px-3 py-1 rounded bg-emerald-100 text-emerald-700 font-bold disabled:opacity-50"
          >
            Next
          </button>
        </div>
      </section>
      <!-- Attendance Summary per School -->
      <section v-if="activeSection === 'attendance-summary'">
        <h2 class="section-title flex items-center gap-2">
          <span class="material-symbols-outlined text-emerald-500">summarize</span>Attendance
          Summary
        </h2>
        <div class="flex gap-4 items-center mb-4">
          <label class="font-semibold text-emerald-800">Filter by school</label>
          <select v-model="filterSchool" class="input">
            <option>All</option>
            <option v-for="schoolFilter2 in schools" :key="schoolFilter2.id">
              {{ schoolFilter2.name }}
            </option>
          </select>
          <label class="font-semibold text-emerald-800">Filter by attendance</label>
          <select v-model="filterAttendance" class="input">
            <option>All</option>
            <option>Present</option>
            <option>Absent</option>
            <option>Not Marked</option>
          </select>
        </div>
        <table class="w-full mb-4">
          <thead>
            <tr class="text-left text-emerald-700">
              <th>#</th>
              <th>Name</th>
              <th>Email</th>
              <th>Student ID</th>
              <th>School</th>
              <th>Total Presents</th>
              <th>Total Absences</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(student, idx) in paginatedAttendance"
              :key="student.studentId"
              class="border-b"
            >
              <td>{{ (page - 1) * itemsPerPage + idx + 1 }}</td>
              <td>{{ student.name }}</td>
              <td>{{ student.email }}</td>
              <td>{{ student.studentId }}</td>
              <td>{{ student.school }}</td>
              <td class="text-center font-semibold text-emerald-600">
                {{ countAttendance(student.studentId, 'present') }}
              </td>
              <td class="text-center font-semibold text-red-600">
                {{ countAttendance(student.studentId, 'absent') }}
              </td>
              <td>
                <button
                  @click="openAttendanceModal(student)"
                  class="action-btn-mini bg-emerald-500 hover:bg-emerald-700 text-white rounded-full px-2 py-1 text-xs shadow transition duration-150 min-w-[80px]"
                >
                  View Details
                </button>
              </td>
            </tr>
          </tbody>
        </table>
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
        <!-- Attendance Details Modal -->
        <div
          v-if="attendanceModal.show"
          class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40"
        >
          <div class="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-2xl relative">
            <h3 class="font-bold text-xl mb-4 text-emerald-800">
              Attendance Details for {{ attendanceModal.student?.name }}
            </h3>
            <div class="flex gap-4 mb-4 items-end">
              <div>
                <label class="block text-sm font-semibold text-emerald-700 mb-1"
                  >Filter by Date:</label
                >
                <input
                  type="date"
                  v-model="attendanceFilterDate"
                  class="rounded-lg border border-emerald-200 px-3 py-1"
                />
              </div>
              <button
                @click="attendanceFilterDate = ''"
                class="ml-2 px-3 py-1.5 rounded bg-gray-100 text-gray-700 hover:bg-gray-200 text-xs h-[36px]"
              >
                Clear
              </button>
            </div>
            <div class="overflow-x-auto max-h-[60vh] mb-6">
              <table class="w-full">
                <thead>
                  <tr class="text-left text-emerald-700">
                    <th>Date</th>
                    <th>Time</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="record in filteredAttendanceRecords" :key="record.id" class="border-b">
                    <td>{{ formatDate(record.date) }}</td>
                    <td>{{ formatTime(record.date) }}</td>
                    <td>
                      <span
                        v-if="record.status === 'present'"
                        class="text-emerald-600 font-semibold"
                        >Present</span
                      >
                      <span v-else class="text-red-600 font-semibold">Absent</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div class="flex justify-end gap-3">
              <button
                @click="closeAttendanceModal"
                class="px-4 py-2 rounded font-semibold bg-gray-100 text-gray-700 hover:bg-gray-200"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      </section>
      <!-- Reports -->
      <section v-if="activeSection === 'report-schools'">
        <h2 class="section-title flex items-center gap-2">
          <span class="material-symbols-outlined text-emerald-500">school</span>Generate Report:
          List of Schools
        </h2>
        <table class="w-full mb-4">
          <thead>
            <tr class="text-left text-emerald-700">
              <th>#</th>
              <th>School</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(school, idx) in schoolsReport" :key="school.id" class="border-b">
              <td>{{ idx + 1 }}</td>
              <td>{{ school.name }}</td>
              <td>
                <span v-if="!school.archived" class="text-emerald-600 font-semibold">Active</span>
                <span v-else class="text-red-600 font-semibold">Archived</span>
              </td>
            </tr>
          </tbody>
        </table>
        <button
          class="action-btn bg-emerald-700 hover:bg-emerald-800"
          @click="downloadSchoolsReport"
        >
          <span class="material-symbols-outlined">download</span>Download
        </button>
      </section>
      <section v-if="activeSection === 'report-students-per-school'">
        <h2 class="section-title flex items-center gap-2">
          <span class="material-symbols-outlined text-emerald-500">groups</span>Generate Report:
          Students per School
        </h2>
        <div class="flex gap-4 items-center mb-4 mt-2">
          <label class="font-semibold text-emerald-800">School:</label>
          <select
            v-model="studentsPerSchoolFilter"
            class="rounded-lg border border-emerald-200 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-400"
          >
            <option value="">All Schools</option>
            <option v-for="school in schools" :key="school.id" :value="school.name">
              {{ school.name }}
            </option>
          </select>
        </div>
        <table class="w-full mb-4">
          <thead>
            <tr class="text-left text-emerald-700">
              <th>
                <input
                  type="checkbox"
                  :checked="allStudentsPerSchoolSelected"
                  @change="toggleSelectAllStudentsPerSchool"
                />
              </th>
              <th>#</th>
              <th>Name</th>
              <th>Email</th>
              <th>Student ID</th>
              <th>School</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(student, idx) in filteredStudentsPerSchool"
              :key="student.id"
              class="border-b"
            >
              <td>
                <input
                  type="checkbox"
                  :checked="selectedStudentsPerSchool.includes(student.id)"
                  @change="toggleStudentPerSchool(student.id)"
                />
              </td>
              <td>{{ idx + 1 }}</td>
              <td>{{ student.name }}</td>
              <td>{{ student.email }}</td>
              <td>{{ student.studentId }}</td>
              <td>{{ student.school || 'No school assigned' }}</td>
              <td>
                <span v-if="student.is_active" class="text-emerald-600 font-semibold">Active</span>
                <span v-else class="text-orange-600 font-semibold">Pending Approval</span>
              </td>
            </tr>
          </tbody>
        </table>
        <button
          class="action-btn bg-emerald-700 hover:bg-emerald-800"
          @click="downloadStudentsPerSchool"
        >
          <span class="material-symbols-outlined">download</span>Download
        </button>
      </section>
      <section v-if="activeSection === 'report-students-summary'">
        <h2 class="section-title flex items-center gap-2">
          <span class="material-symbols-outlined text-emerald-500">bar_chart</span>Generate Report:
          Students w/ Attendance Summary
        </h2>
        <div class="flex gap-4 items-center mb-4 mt-2">
          <label class="font-semibold text-emerald-800">School:</label>
          <select
            v-model="summarySchoolFilter"
            class="rounded-lg border border-emerald-200 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-400"
          >
            <option value="">All Schools</option>
            <option v-for="school in schools" :key="school.id" :value="school.name">
              {{ school.name }}
            </option>
          </select>
        </div>
        <table class="w-full mb-4">
          <thead>
            <tr class="text-left text-emerald-700">
              <th>#</th>
              <th>Name</th>
              <th>Email</th>
              <th>Student ID</th>
              <th>School</th>
              <th>Total Presents</th>
              <th>Total Absences</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(student, idx) in filteredSummaryStudents"
              :key="student.id"
              class="border-b"
            >
              <td>{{ idx + 1 }}</td>
              <td>{{ student.name }}</td>
              <td>{{ student.email }}</td>
              <td>{{ student.studentId }}</td>
              <td>{{ student.school || 'No school assigned' }}</td>
              <td class="text-center font-semibold text-emerald-600">
                {{ countAttendance(student.studentId, 'present') }}
              </td>
              <td class="text-center font-semibold text-red-600">
                {{ countAttendance(student.studentId, 'absent') }}
              </td>
            </tr>
          </tbody>
        </table>
        <button
          class="action-btn bg-emerald-700 hover:bg-emerald-800"
          @click="downloadSummaryStudents"
        >
          <span class="material-symbols-outlined">download</span>Download
        </button>
      </section>
      <section v-if="activeSection === 'report-summary-each-student'">
        <h2 class="section-title flex items-center gap-2">
          <span class="material-symbols-outlined text-emerald-500">person_search</span>Generate
          Report: Summary per Student
        </h2>
        <div class="flex gap-4 items-center mb-4 mt-2">
          <label class="font-semibold text-emerald-800">School:</label>
          <select
            v-model="summaryPerStudentSchoolFilter"
            class="rounded-lg border border-emerald-200 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-400"
          >
            <option value="">All Schools</option>
            <option v-for="school in schools" :key="school.id" :value="school.name">
              {{ school.name }}
            </option>
          </select>
        </div>
        <table class="w-full mb-4">
          <thead>
            <tr class="text-left text-emerald-700">
              <th>
                <input
                  type="checkbox"
                  :checked="allSummaryPerStudentSelected"
                  @change="toggleSelectAllSummaryPerStudent"
                />
              </th>
              <th>#</th>
              <th>Name</th>
              <th>Email</th>
              <th>Student ID</th>
              <th>School</th>
              <th>Total Presents</th>
              <th>Total Absences</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(student, idx) in filteredSummaryPerStudent"
              :key="student.id"
              class="border-b"
            >
              <td>
                <input
                  type="checkbox"
                  :checked="selectedSummaryPerStudent.includes(student.id)"
                  @change="toggleSummaryPerStudent(student.id)"
                />
              </td>
              <td>{{ idx + 1 }}</td>
              <td>{{ student.name }}</td>
              <td>{{ student.email }}</td>
              <td>{{ student.studentId }}</td>
              <td>{{ student.school || 'No school assigned' }}</td>
              <td class="text-center font-semibold text-emerald-600">
                {{ countAttendance(student.studentId, 'present') }}
              </td>
              <td class="text-center font-semibold text-red-600">
                {{ countAttendance(student.studentId, 'absent') }}
              </td>
            </tr>
          </tbody>
        </table>
        <button
          class="action-btn bg-emerald-700 hover:bg-emerald-800"
          @click="downloadSummaryPerStudent"
        >
          <span class="material-symbols-outlined">download</span>Download
        </button>
      </section>
      <section v-if="activeSection === 'report-students'">
        <h2 class="section-title flex items-center gap-2">
          <span class="material-symbols-outlined text-emerald-500">list</span>Generate Report: List
          of Students
        </h2>
        <div class="flex gap-4 items-center mb-4 mt-2">
          <label class="font-semibold text-emerald-800">School:</label>
          <select
            v-model="reportSchoolFilter"
            class="rounded-lg border border-emerald-200 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-400"
          >
            <option value="">All Schools</option>
            <option v-for="school in schools" :key="school.id" :value="school.name">
              {{ school.name }}
            </option>
          </select>
        </div>
        <table class="w-full mb-4">
          <thead>
            <tr class="text-left text-emerald-700">
              <th>#</th>
              <th>Name</th>
              <th>Email</th>
              <th>Student ID</th>
              <th>School</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(student, idx) in filteredReportStudents" :key="student.id" class="border-b">
              <td>{{ idx + 1 }}</td>
              <td>{{ student.name }}</td>
              <td>{{ student.email }}</td>
              <td>{{ student.studentId }}</td>
              <td>{{ student.school || 'No school assigned' }}</td>
              <td>
                <span v-if="student.is_active" class="text-emerald-600 font-semibold">Active</span>
                <span v-else class="text-orange-600 font-semibold">Pending Approval</span>
              </td>
            </tr>
          </tbody>
        </table>
        <button class="action-btn bg-emerald-700 hover:bg-emerald-800" @click="downloadReport">
          <span class="material-symbols-outlined">download</span>Download
        </button>
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
  <!-- Assign School Modal -->
  <div
    v-if="showAssignSchoolModal"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40"
  >
    <div
      class="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md relative"
      ref="assignSchoolModalRef"
    >
      <button
        @click="closeAssignSchoolModal"
        class="absolute top-3 right-3 text-gray-400 hover:text-red-500 text-2xl font-bold"
      >
        &times;
      </button>
      <h3 class="font-bold text-xl mb-4 text-emerald-800 flex items-center gap-2">
        <span class="material-symbols-outlined text-emerald-600">school</span>
        Add School(s) to <span class="text-emerald-700">{{ assignSchoolInstructor?.name }}</span>
      </h3>
      <input
        v-model="assignSchoolSearch"
        type="text"
        placeholder="Search schools..."
        class="input mb-4 w-full"
      />
      <div class="max-h-56 overflow-y-auto">
        <div
          v-for="school in filteredAssignSchools"
          :key="school.id"
          :class="[
            'flex items-center gap-3 px-4 py-2 mb-1 border border-emerald-100 rounded-lg cursor-pointer transition',
            assignSchoolSelections.includes(school.name)
              ? 'bg-emerald-50 border-emerald-400'
              : 'hover:bg-emerald-50',
          ]"
          @click="
            () => {
              const idx = assignSchoolSelections.indexOf(school.name)
              if (idx === -1) assignSchoolSelections.push(school.name)
              else assignSchoolSelections.splice(idx, 1)
            }
          "
        >
          <span class="custom-checkbox-wrapper">
            <input
              type="checkbox"
              :id="'school-' + school.id"
              :value="school.name"
              v-model="assignSchoolSelections"
              class="custom-checkbox"
              @click.stop
            />
            <span class="custom-checkbox-indicator"></span>
          </span>
          <label
            :for="'school-' + school.id"
            class="flex items-center gap-2 cursor-pointer select-none w-full"
          >
            <span class="material-symbols-outlined text-emerald-500">school</span>
            <span>{{ school.name }}</span>
          </label>
        </div>
        <div v-if="filteredAssignSchools.length === 0" class="text-gray-400 text-center py-4">
          No schools found.
        </div>
      </div>
      <button
        @click="assignSchoolsToInstructor"
        class="mt-4 mx-auto action-btn-normal bg-emerald-700 hover:bg-emerald-800 block"
      >
        Save
      </button>
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
.nav-link {
  @apply text-emerald-800 font-semibold px-4 py-2 rounded-full hover:bg-emerald-50 transition cursor-pointer shadow-sm;
  transition:
    background 0.2s,
    color 0.2s;
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
}
.input {
  @apply border border-emerald-200 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-400;
}
.action-btn {
  @apply px-6 py-2 rounded-full text-white font-bold flex items-center gap-2 shadow hover:shadow-lg transition;
}
.bg-dark-green {
  background-color: #065f46 !important;
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
.icon-btn {
  @apply p-2 rounded-full flex items-center justify-center text-white text-lg shadow hover:shadow-md transition bg-emerald-500 hover:bg-emerald-600;
  min-width: 36px;
  min-height: 36px;
  width: 36px;
  height: 36px;
}
.icon-btn.bg-red-500 {
  background-color: #ef4444 !important;
}
.icon-btn.bg-emerald-700 {
  background-color: #065f46 !important;
}
.icon-btn.bg-emerald-800 {
  background-color: #064e3b !important;
}
.action-btn-mini {
  @apply px-4 py-1 rounded-full text-white font-semibold text-sm flex items-center gap-1 shadow hover:shadow-md transition min-w-[80px];
}
.action-btn-normal {
  @apply px-6 py-2 rounded-full text-white font-semibold text-base flex items-center gap-2 shadow hover:shadow-md transition;
}
/* Custom Checkbox Styles */
.custom-checkbox-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  height: 24px;
  width: 24px;
}
.custom-checkbox {
  opacity: 0;
  width: 24px;
  height: 24px;
  margin: 0;
  position: absolute;
  left: 0;
  top: 0;
  z-index: 2;
  cursor: pointer;
}
.custom-checkbox-indicator {
  display: inline-block;
  width: 22px;
  height: 22px;
  border-radius: 8px;
  border: 2px solid #a7f3d0;
  background: #fff;
  transition:
    border-color 0.2s,
    background 0.2s;
  position: relative;
  z-index: 1;
}
.custom-checkbox:checked + .custom-checkbox-indicator {
  background: #10b981;
  border-color: #10b981;
}
.custom-checkbox:checked + .custom-checkbox-indicator:after {
  content: '';
  position: absolute;
  left: 6px;
  top: 2px;
  width: 6px;
  height: 12px;
  border: solid #fff;
  border-width: 0 3px 3px 0;
  transform: rotate(45deg);
}
.custom-checkbox-indicator:hover {
  border-color: #34d399;
}
.custom-checkbox:focus + .custom-checkbox-indicator {
  box-shadow: 0 0 0 2px #a7f3d0;
}
/* 3-dots button hover/active */
.icon-btn {
  transition:
    background 0.15s,
    box-shadow 0.15s,
    color 0.15s;
}
.icon-btn:active,
.icon-btn:focus {
  outline: none;
  box-shadow: 0 0 0 2px #10b981;
  background: #059669;
}
</style>
