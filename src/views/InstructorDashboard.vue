<script setup lang="ts">
import { ref, onMounted, computed, onBeforeUnmount, watch } from 'vue'
import { useSnackbarStore } from '@/stores/snackbar'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'
import api from '@/services/api'


interface Student {
  id: number
  name: string
  email: string
  studentId: string
  is_active: boolean
  school?: string
  instructor?: string
  attendance?: 'present' | 'absent' | null
  totalPresents?: number
  totalAbsences?: number
}

interface AttendanceRecord {
  id: number
  student_id: number
  date: string
  status: string
}

const snackbar = useSnackbarStore()
const students = ref<Student[]>([])
const loading = ref(false)
const error = ref('')

const attendanceRecords = ref<Record<string, AttendanceRecord[]>>({})
const attendanceModal = ref({
  show: false,
  student: null as Student | null,
  records: [] as AttendanceRecord[],
})

const studentsPerPage = 10
const studentPage = ref(1)
const statusFilter = ref('all')
const selectedSchool = ref('')
const instructorSchools = ref<string[]>([])
const summarySchoolFilter = ref('')
const summaryAttendanceFilter = ref('')
const paginatedStudents = computed(() => {
  const start = (studentPage.value - 1) * studentsPerPage
  const filteredStudents = students.value.filter((student) => {
    if (statusFilter.value === 'all') return true
    if (statusFilter.value === 'active') return student.is_active
    if (statusFilter.value === 'inactive') return !student.is_active
    if (statusFilter.value === 'pending') return !student.is_active
    return true
  })
  return filteredStudents.slice(start, start + studentsPerPage)
})
const studentTotalPages = computed(() => {
  const filteredStudents = students.value.filter((student) => {
    if (statusFilter.value === 'all') return true
    if (statusFilter.value === 'active') return student.is_active
    if (statusFilter.value === 'inactive') return !student.is_active
    if (statusFilter.value === 'pending') return !student.is_active
    return true
  })
  return Math.ceil(filteredStudents.length / studentsPerPage) || 1
})
function goToStudentPage(p: number) {
  if (p >= 1 && p <= studentTotalPages.value) studentPage.value = p
}

// Watch for filter changes and reset to first page
watch(statusFilter, () => {
  studentPage.value = 1
})

// Watch for school selection changes
watch(selectedSchool, () => {
  if (activeSection.value === 'students') {
    fetchAllStudents()
  }
})

// Watch for summary filter changes
watch([summarySchoolFilter, summaryAttendanceFilter], () => {
  summaryPage.value = 1
})
// Placeholder for summary pagination if needed
const summaryPerPage = 10
const summaryPage = ref(1)
const paginatedSummary = computed(() => {
  // Filter students based on summary filters
  let filteredStudents = students.value

  // Filter by school
  if (summarySchoolFilter.value) {
    filteredStudents = filteredStudents.filter(
      (student) => student.school === summarySchoolFilter.value,
    )
  }

  // Filter by attendance (per student)
  if (summaryAttendanceFilter.value) {
    if (summaryAttendanceFilter.value === 'not_marked') {
      filteredStudents = filteredStudents.filter(
        (student) =>
          !attendanceRecords.value[student.studentId] ||
          attendanceRecords.value[student.studentId].length === 0,
      )
    } else if (summaryAttendanceFilter.value === 'present') {
      filteredStudents = filteredStudents.filter(
        (student) => countAttendance(student.studentId, 'present') > 0,
      )
    } else if (summaryAttendanceFilter.value === 'absent') {
      filteredStudents = filteredStudents.filter(
        (student) => countAttendance(student.studentId, 'absent') > 0,
      )
    }
  }

  const start = (summaryPage.value - 1) * summaryPerPage
  return filteredStudents.slice(start, start + summaryPerPage)
})
const summaryTotalPages = computed(() => {
  // Apply same filtering logic as paginatedSummary
  let filteredStudents = students.value

  // Filter by school
  if (summarySchoolFilter.value) {
    filteredStudents = filteredStudents.filter(
      (student) => student.school === summarySchoolFilter.value,
    )
  }

  // Filter by attendance
  if (summaryAttendanceFilter.value) {
    if (summaryAttendanceFilter.value === 'not_marked') {
      filteredStudents = filteredStudents.filter(
        (student) =>
          !attendanceRecords.value[student.studentId] ||
          attendanceRecords.value[student.studentId].length === 0,
      )
    } else if (summaryAttendanceFilter.value === 'present') {
      filteredStudents = filteredStudents.filter(
        (student) => countAttendance(student.studentId, 'present') > 0,
      )
    } else if (summaryAttendanceFilter.value === 'absent') {
      filteredStudents = filteredStudents.filter(
        (student) => countAttendance(student.studentId, 'absent') > 0,
      )
    }
  }

  return Math.ceil(filteredStudents.length / summaryPerPage) || 1
})
function goToSummaryPage(p: number) {
  if (p >= 1 && p <= summaryTotalPages.value) summaryPage.value = p
}

// const menuOpen = ref<number | null>(null)
const profileMenuOpen = ref(false)
function toggleProfileMenu() {
  profileMenuOpen.value = !profileMenuOpen.value
}
function closeProfileMenu() {
  profileMenuOpen.value = false
}

const activeSection = ref('approval')

function setSection(section: string) {
  activeSection.value = section
  // Refetch students when switching sections
  if (section === 'approval' || section === 'students') {
    fetchAllStudents()
  }
}

async function fetchAllStudents() {
  loading.value = true
  error.value = ''
  try {
    const instructor = userStore.user
    if (!instructor) {
      error.value = 'Instructor not found.'
      return
    }

    const { data } = await api.get('/users')
    console.log('All users from API:', data)

    // Get instructor's schools (assuming schools are comma-separated)
    const schools = instructor.school ? instructor.school.split(',').map((s) => s.trim()) : []
    instructorSchools.value = schools
    console.log('Instructor schools:', schools)

    // For approval section: show all students from all assigned schools
    if (activeSection.value === 'approval') {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      students.value = data.filter((u: any) => u.role === 'student' && schools.includes(u.school))
      console.log('Students for approval (all schools):', students.value)
    } else {
      // For view students section: filter by selected school
      if (selectedSchool.value) {
        students.value = data.filter(
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          (u: any) => u.role === 'student' && u.school === selectedSchool.value,
        )
        console.log('Students for selected school:', students.value)
      } else {
        // Show all students from all assigned schools
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        students.value = data.filter((u: any) => u.role === 'student' && schools.includes(u.school))
        console.log('All students from assigned schools:', students.value)
      }
    }

    studentPage.value = 1
    await fetchAttendanceForVisibleStudents()
  } catch (e) {
    console.error('Error fetching students:', e)
    error.value = 'Failed to fetch students.'
  } finally {
    loading.value = false
  }
}

// function toggleMenu(studentId: number) {
//   menuOpen.value = menuOpen.value === studentId ? null : studentId
// }

// function closeMenu() {
//   menuOpen.value = null
// }

// function handleClickOutside(event: MouseEvent) {
//   const menus = document.querySelectorAll('.action-menu')
//   let clickedInside = false
//   menus.forEach((menu) => {
//     if (menu.contains(event.target as Node)) clickedInside = true
//   })
//   if (!clickedInside) closeMenu()
// }

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

// Logout confirmation modal logic
const showLogoutConfirm = ref(false)
function openLogoutConfirm() {
  showLogoutConfirm.value = true
}
function closeLogoutConfirm() {
  showLogoutConfirm.value = false
}
function confirmLogout() {
  // If you have a user store, call logout here
  // userStore.logout()
  closeProfileMenu()
  closeLogoutConfirm()
  router.push('/login')
}

const router = useRouter()

const userStore = useUserStore()
const profile = ref<{ name: string; email: string; school?: string; dob?: string }>({
  name: '',
  email: '',
  school: '',
  dob: '',
})

async function fetchProfile() {
  try {
    if (!userStore.user || !userStore.user.email) return
    const { data } = await api.post('/auth/profile', { email: userStore.user.email })
    profile.value = {
      name: data.name,
      email: data.email,
      school: data.school || '',
      dob: data.dob || '',
    }
    console.log('Instructor profile:', profile.value)
    console.log('User store user:', userStore.user)
  } catch (e) {
    console.error('Error fetching profile:', e)
  }
}

function resetAccount(student: Student) {
  alert(`Reset account for ${student.name}`)
}

async function resetStudent(student: Student) {
  try {
    // For now, we'll just mark as inactive in the frontend
    // In a real implementation, you'd have a backend endpoint for this
    student.is_active = false
    snackbar.trigger('Student account reset!', 'success')
    fetchAllStudents()
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  } catch (e) {
    snackbar.trigger('Failed to reset student account', 'error')
  }
}

async function fetchAttendanceRecords(studentId: string) {
  const { data } = await api.get(`/attendance/by-student/${studentId}`)
  attendanceRecords.value[studentId] = data
  return data
}

function getLastAttendance(studentId: string): AttendanceRecord | null {
  const records = attendanceRecords.value[studentId]
  if (!records || records.length === 0) return null
  // Sort by date descending
  return [...records].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())[0]
}

async function fetchAttendanceForVisibleStudents() {
  await Promise.all(paginatedStudents.value.map((s) => fetchAttendanceRecords(s.studentId)))
}

async function markPresent(student: Student) {
  try {
    const now = new Date().toISOString()
    await api.post('/attendance/mark', {
      student_id: student.id,
      status: 'present',
      date: now,
    })
    snackbar.trigger(`${student.name} marked as present!`, 'success')
    await fetchAttendanceForVisibleStudents()
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  } catch (e) {
    snackbar.trigger('Failed to mark student as present', 'error')
  }
}

async function markAbsent(student: Student) {
  try {
    const now = new Date().toISOString()
    await api.post('/attendance/mark', {
      student_id: student.id,
      status: 'absent',
      date: now,
    })
    snackbar.trigger(`${student.name} marked as absent!`, 'success')
    await fetchAttendanceForVisibleStudents()
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  } catch (e) {
    snackbar.trigger('Failed to mark student as absent', 'error')
  }
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

async function approveStudent(student: Student) {
  try {
    await api.post(`/students/approve/${student.id}`)
    student.is_active = true
    snackbar.trigger('Student approved!', 'success')
    fetchAllStudents()
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  } catch (e) {
    snackbar.trigger('Failed to approve student', 'error')
  }
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
  document.addEventListener('click', handleClickOutsideActionsMenu)
  fetchAllStudents()
  fetchProfile()
})
onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutsideActionsMenu)
})

// Remove old pagination logic
// const rowsPerPage = 6
// const currentPage = ref(1)
// const totalPages = computed(() => Math.max(1, Math.ceil(students.value.length / rowsPerPage)))
// const paginatedStudents = computed(() => {
//   const start = (currentPage.value - 1) * rowsPerPage
//   return students.value.slice(start, start + rowsPerPage)
// })
// function goToPage(page: number) {
//   if (page >= 1 && page <= totalPages.value) {
//     currentPage.value = page
//   }
// }
// const paginationRange = computed(() => {
//   const total = totalPages.value
//   const current = currentPage.value
//   if (total <= 3) {
//     return Array.from({ length: total }, (_, i) => i + 1)
//   }
//   const range = []
//   if (current > 2) range.push('...')
//   if (current === 1) {
//     range.push(1, 2, 3)
//   } else if (current === total) {
//     range.push(total - 2, total - 1, total)
//   } else {
//     range.push(current - 1, current, current + 1)
//   }
//   if (current < total - 1) range.push('...')
//   return range.filter(
//     (p) => p === '...' || (typeof p === 'number' && p >= 1 && p <= total)
//   )
// })

// Pagination and numbering for students and summary
// const studentsPerPage = 10
// const studentPage = ref(1)
// const paginatedStudents = computed(() => {
//   const start = (studentPage.value - 1) * studentsPerPage
//   return students.value.slice(start, start + studentsPerPage)
// })
// const studentTotalPages = computed(() => {
//   return Math.ceil(students.value.length / studentsPerPage) || 1
// })
// function goToStudentPage(p: number) {
//   if (p >= 1 && p <= studentTotalPages.value) studentPage.value = p
// }
// Placeholder for summary pagination if needed
// const summaryPerPage = 10
// const summaryPage = ref(1)
// const paginatedSummary = computed(() => {
//   // For demonstration, use students as summary data
//   const start = (summaryPage.value - 1) * summaryPerPage
//   return students.value.slice(start, start + summaryPerPage)
// })
// const summaryTotalPages = computed(() => {
//   return Math.ceil(students.value.length / summaryPerPage) || 1
// })
// function goToSummaryPage(p: number) {
//   if (p >= 1 && p <= summaryTotalPages.value) summaryPage.value = p
// }

const editingProfile = ref(false)
const profileForm = ref({
  name: '',
  email: '',
  school: '',
  dob: '',
})

function startEditProfile() {
  editingProfile.value = true
  profileForm.value = {
    name: profile.value.name || '',
    email: profile.value.email || '',
    school: profile.value.school || '',
    dob: profile.value.dob || '',
  }
}

async function saveProfile() {
  try {
    if (!userStore.user) throw new Error('User not found')
    await api.put(`/users/${userStore.user.id}`, profileForm.value)
    profile.value = { ...profileForm.value }
    editingProfile.value = false
    snackbar.trigger('Profile updated!', 'success')
    fetchProfile()
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  } catch (e) {
    snackbar.trigger('Failed to update profile', 'error')
  }
}

function cancelEditProfile() {
  editingProfile.value = false
}

const reportSchoolFilter = ref('')
const filteredReportStudents = computed(() => {
  if (!reportSchoolFilter.value) return students.value
  return students.value.filter((s) => s.school === reportSchoolFilter.value)
})

// const showReportPreview = ref(false)
// const pdfPreviewUrl = ref('')

// async function openReportPreview() {
//   // Generate PDF in memory
//   const doc = new jsPDF()
//   doc.setFontSize(14)
//   doc.text('Student Report', 14, 18)
//   const headers = ['#', 'Name', 'Email', 'Student ID', 'School', 'Status']
//   const rows = filteredReportStudents.value.map((s, idx) => [
//     (idx + 1).toString(),
//     s.name,
//     s.email,
//     s.studentId,
//     s.school || '',
//     s.is_active ? 'Active' : 'Pending Approval',
//   ])
//   // Simple table rendering
//   let y = 30
//   doc.setFontSize(11)
//   doc.text(headers, 14, y)
//   y += 8
//   rows.forEach((row) => {
//     doc.text(row, 14, y)
//     y += 8
//     if (y > 270) {
//       doc.addPage()
//       y = 20
//     }
//   })
//   // Create Blob URL for preview
//   const pdfBlob = doc.output('blob')
//   pdfPreviewUrl.value = URL.createObjectURL(pdfBlob)
//   showReportPreview.value = true
// }
// // function closeReportPreview() {
// //   showReportPreview.value = false
// //   if (pdfPreviewUrl.value) {
// //     URL.revokeObjectURL(pdfPreviewUrl.value)
// //     pdfPreviewUrl.value = ''
// //   }
// // }
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
    headStyles: { fillColor: [22, 163, 74] }, // emerald-600
    margin: { left: 14, right: 14 },
  })

  // Open PDF in new tab
  const pdfBlob = doc.output('blob')
  const url = URL.createObjectURL(pdfBlob)
  window.open(url, '_blank')
}

// // Attendance summary for report: grouped by school
// const groupedAttendanceSummary = computed(() => {
//   const summary: Record<
//     string,
//     {
//       school: string
//       status: string
//       totalStudents: number
//       totalPresents: number
//       totalAbsences: number
//     }
//   > = {}
//   students.value.forEach((s) => {
//     const school = s.school || 'No school assigned'
//     if (!summary[school]) {
//       summary[school] = {
//         school,
//         status: s.is_active ? 'Active' : 'Pending Approval',
//         totalStudents: 0,
//         totalPresents: 0,
//         totalAbsences: 0,
//       }
//     }
//     summary[school].totalStudents++
//     summary[school].totalPresents += s.totalPresents || 0
//     summary[school].totalAbsences += s.totalAbsences || 0
//   })
//   return Object.values(summary)
// })

function downloadReportSummary() {
  if (summaryReportSelectedSchools.value.length === 0) {
    snackbar.trigger('Please select at least one school to generate the report.', 'warning')
    return
  }
  const doc = new jsPDF()
  doc.setFontSize(14)
  doc.text('Attendance Summary Report', 14, 18)
  const headers = [['School', 'Date', 'Present (Student IDs)', 'Absent (Student IDs)']]
  const rows = summaryReportSelectedSchools.value.map((school) => [
    school,
    summaryReportDate.value,
    getSchoolPresentIdsOnDate(school, summaryReportDate.value).join(', '),
    getSchoolAbsentIdsOnDate(school, summaryReportDate.value).join(', '),
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

// Per-student report with school filter and search
const reportPerStudentSchoolFilter = ref('')
const reportPerStudentSearch = ref('')
const filteredReportPerStudent = computed(() => {
  let filtered = students.value
  if (reportPerStudentSchoolFilter.value) {
    filtered = filtered.filter((s) => s.school === reportPerStudentSchoolFilter.value)
  }
  if (reportPerStudentSearch.value) {
    const q = reportPerStudentSearch.value.toLowerCase()
    filtered = filtered.filter(
      (s) => s.name.toLowerCase().includes(q) || s.email.toLowerCase().includes(q),
    )
  }
  return filtered
})

const selectedStudentIds = ref<number[]>([])

function toggleSelectAllPerStudent() {
  if (allPerStudentSelected.value) {
    selectedStudentIds.value = []
  } else {
    selectedStudentIds.value = filteredReportPerStudent.value.map((s) => s.id)
  }
}
const allPerStudentSelected = computed(
  () =>
    filteredReportPerStudent.value.length > 0 &&
    filteredReportPerStudent.value.every((s) => selectedStudentIds.value.includes(s.id)),
)

function toggleStudentSelection(id: number) {
  if (selectedStudentIds.value.includes(id)) {
    selectedStudentIds.value = selectedStudentIds.value.filter((sid) => sid !== id)
  } else {
    selectedStudentIds.value.push(id)
  }
}

function downloadReportPerStudent() {
  const doc = new jsPDF()
  doc.setFontSize(14)
  doc.text('Per-Student Attendance Report', 14, 18)
  const headers = [['#', 'Name', 'Email', 'Total Presents', 'Total Absences']]
  const selected = filteredReportPerStudent.value.filter((s) =>
    selectedStudentIds.value.includes(s.id),
  )
  const rows = selected.map((s, idx) => [
    idx + 1,
    s.name,
    s.email,
    s.totalPresents || 0,
    s.totalAbsences || 0,
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

// Add this function for Philippine time conversion
function toPhilippineTime(dateStr: string): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  // Convert to UTC+8
  const utc = date.getTime() + date.getTimezoneOffset() * 60000
  const phTime = new Date(utc + 8 * 60 * 60 * 1000)
  return phTime.toLocaleString('en-PH', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  })
}

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

// Add for edit attendance modal
const editAttendanceModal = ref({
  show: false,
  student: null as Student | null,
  record: null as AttendanceRecord | null,
  newStatus: '',
})

function isToday(dateStr: string) {
  const today = new Date()
  const date = new Date(dateStr)
  return (
    date.getFullYear() === today.getFullYear() &&
    date.getMonth() === today.getMonth() &&
    date.getDate() === today.getDate()
  )
}

function getTodayAttendance(studentId: string): AttendanceRecord | null {
  const records = attendanceRecords.value[studentId]
  if (!records) return null
  return records.find((r) => isToday(r.date)) || null
}

function openEditAttendanceModal(student: Student) {
  const record = getTodayAttendance(student.studentId)
  if (!record) return
  editAttendanceModal.value = {
    show: true,
    student,
    record,
    newStatus: record.status,
  }
}
function closeEditAttendanceModal() {
  editAttendanceModal.value = { show: false, student: null, record: null, newStatus: '' }
}

async function saveEditAttendance() {
  const { student, newStatus } = editAttendanceModal.value
  if (!student) return
  try {
    await api.put(`/attendance/by-student/${student.studentId}`, { status: newStatus })
    snackbar.trigger('Attendance updated!', 'success')
    await fetchAttendanceRecords(student.studentId)
    closeEditAttendanceModal()
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  } catch (e) {
    snackbar.trigger('Failed to update attendance', 'error')
  }
}

// Helper to count presents/absences for a student
function countAttendance(studentId: string, status: 'present' | 'absent'): number {
  const records = attendanceRecords.value[studentId] || []
  return records.filter((r) => r.status === status).length
}

// Helper to count presents/absences for a school
// function countSchoolAttendance(school: string, status: 'present' | 'absent'): number {
//   return students.value
//     .filter((s) => s.school === school)
//     .reduce((sum, s) => sum + countAttendance(s.studentId, status), 0)
// }

// // Helper to count students in a school
// function countSchoolStudents(school: string): number {
//   return students.value.filter((s) => s.school === school).length
// }

// Date picker for Attendance Summary report
const summaryReportDate = ref(new Date().toISOString().slice(0, 10)) // yyyy-mm-dd

// School filter for Attendance Summary report
const summaryReportSchool = ref('')

// Track selected schools for Attendance Summary report
const summaryReportSelectedSchools = ref<string[]>([])

function toggleAllSummarySchools(checked: boolean) {
  if (checked) {
    summaryReportSelectedSchools.value = getUniqueSchools().filter(
      (s) => !summaryReportSchool.value || s === summaryReportSchool.value,
    )
  } else {
    summaryReportSelectedSchools.value = []
  }
}
function toggleSummarySchool(school: string) {
  if (summaryReportSelectedSchools.value.includes(school)) {
    summaryReportSelectedSchools.value = summaryReportSelectedSchools.value.filter(
      (s) => s !== school,
    )
  } else {
    summaryReportSelectedSchools.value.push(school)
  }
}
function isAllSummarySchoolsSelected() {
  const visibleSchools = getUniqueSchools().filter(
    (s) => !summaryReportSchool.value || s === summaryReportSchool.value,
  )
  return (
    visibleSchools.length > 0 &&
    visibleSchools.every((s) => summaryReportSelectedSchools.value.includes(s))
  )
}

// Helper to get present/absent student IDs for a school on a given date
function getSchoolPresentIdsOnDate(school: string, dateStr: string): string[] {
  return students.value
    .filter((s) => s.school === school)
    .filter((s) =>
      attendanceRecords.value[s.studentId]?.some(
        (r) => isSameDay(r.date, dateStr) && r.status === 'present',
      ),
    )
    .map((s) => s.studentId)
}
function getSchoolAbsentIdsOnDate(school: string, dateStr: string): string[] {
  return students.value
    .filter((s) => s.school === school)
    .filter((s) =>
      attendanceRecords.value[s.studentId]?.some(
        (r) => isSameDay(r.date, dateStr) && r.status === 'absent',
      ),
    )
    .map((s) => s.studentId)
}

// Helper to get unique schools (ensure only one definition and in <script setup> scope)
function getUniqueSchools(): string[] {
  const schools = students.value.map((s) => s.school || 'No school assigned')
  return Array.from(new Set(schools))
}

function isSameDay(dateStr: string, targetDateStr: string): boolean {
  const d = new Date(dateStr)
  const t = new Date(targetDateStr)
  return (
    d.getFullYear() === t.getFullYear() &&
    d.getMonth() === t.getMonth() &&
    d.getDate() === t.getDate()
  )
}

function clearSummaryReport() {
  summaryReportDate.value = new Date().toISOString().slice(0, 10)
}
</script>

<template>
  <!-- Header Bar (Top) -->
  <div class="w-full header-bar flex items-center justify-between px-8 py-4 z-50 sticky top-0">
    <span class="header-title font-extrabold text-2xl tracking-tight">AFP Attendance</span>
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
          >
            <span class="material-symbols-outlined text-white">logout</span>Logout
          </button>
        </div>
      </transition>
    </div>
  </div>

  <!-- Navbar (now below header, inside main content area) -->
  <div class="w-full flex justify-center mt-4 mb-6">
    <div class="navbar-modern flex flex-wrap items-center gap-2 md:gap-6">
      <button
        @click="setSection('approval')"
        :class="['nav-link flex items-center gap-2', { active: activeSection === 'approval' }]"
      >
        <span class="material-symbols-outlined text-emerald-500">verified_user</span>
        Approve Accounts
      </button>
      <button
        @click="setSection('students')"
        :class="['nav-link flex items-center gap-2', { active: activeSection === 'students' }]"
      >
        <span class="material-symbols-outlined text-emerald-500">groups</span>
        View Students
      </button>
      <button
        @click="setSection('summary')"
        :class="['nav-link flex items-center gap-2', { active: activeSection === 'summary' }]"
      >
        <span class="material-symbols-outlined text-emerald-500">summarize</span>
        Attendance Summary
      </button>
      <button
        @click="setSection('profile')"
        :class="['nav-link flex items-center gap-2', { active: activeSection === 'profile' }]"
      >
        <span class="material-symbols-outlined text-emerald-500">person</span>
        Update Profile
      </button>
      <div
        class="relative group"
        @mouseenter="openReportMenu"
        @mouseleave="closeReportMenu"
        @focusin="openReportMenu"
        @focusout="closeReportMenu"
      >
        <button class="nav-link flex items-center gap-2" type="button">
          <span class="material-symbols-outlined text-emerald-500">description</span>
          Generate Report
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
            @click="setSection('report-students')"
            class="block w-full text-left px-4 py-2 hover:bg-emerald-50 flex items-center gap-2"
          >
            <span class="material-symbols-outlined text-emerald-500">list</span>List of Students
          </button>
          <button
            @click="setSection('report-summary')"
            class="block w-full text-left px-4 py-2 hover:bg-emerald-50 flex items-center gap-2"
          >
            <span class="material-symbols-outlined text-emerald-500">bar_chart</span>Attendance
            Summary
          </button>
          <button
            @click="setSection('report-per-student')"
            class="block w-full text-left px-4 py-2 hover:bg-emerald-50 flex items-center gap-2"
          >
            <span class="material-symbols-outlined text-emerald-500">person_search</span>Per-Student
            Summary
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Main Content Container -->
  <div class="flex justify-center items-start min-h-[60vh] pt-2 pb-16 overflow-y-auto max-h-screen">
    <div class="w-full max-w-6xl card-section mt-0 mx-auto px-4 md:px-8">
      <!-- Approve Student Accounts -->
      <section v-if="activeSection === 'approval'">
        <h2 class="section-title flex items-center gap-2">
          <span class="material-symbols-outlined text-emerald-500">verified_user</span>Approve
          Student Accounts
        </h2>

        <!-- Status Filter -->
        <div class="flex gap-4 items-center mb-6 mt-2">
          <label class="font-semibold text-emerald-800">Filter by Status:</label>
          <select
            v-model="statusFilter"
            class="rounded-lg border border-emerald-200 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-400"
          >
            <option value="all">All Students</option>
            <option value="active">Active Students</option>
            <option value="inactive">Inactive Students</option>
            <option value="pending">Pending Approval</option>
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
              <th>Assigned Instructor</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(student, idx) in paginatedStudents" :key="student.id" class="border-b">
              <td>{{ (studentPage - 1) * studentsPerPage + idx + 1 }}</td>
              <td>{{ student.name }}</td>
              <td>{{ student.email }}</td>
              <td>{{ student.studentId }}</td>
              <td>{{ student.school || 'No school assigned' }}</td>
              <td>{{ student.instructor || 'Not assigned' }}</td>
              <td>
                <span v-if="student.is_active" class="text-emerald-600 font-semibold">
                  Active
                </span>
                <span v-else class="text-orange-600 font-semibold"> Pending Approval </span>
              </td>
              <td class="flex gap-2 py-2 relative justify-center items-center">
                <template v-if="!student.is_active">
                  <button
                    @click="approveStudent(student)"
                    class="action-btn-mini bg-emerald-600 hover:bg-emerald-700 text-white rounded-full px-3 py-1.5 text-sm shadow transition duration-150"
                    aria-label="Approve"
                  >
                    Approve
                  </button>
                  <button
                    @click="resetAccount(student)"
                    class="action-btn-mini bg-red-500 hover:bg-red-700 text-white rounded-full px-3 py-1.5 text-sm shadow transition duration-150"
                    aria-label="Reject"
                  >
                    Reject
                  </button>
                </template>
                <template v-else>
                  <button
                    @click="openActionsMenu(student.id)"
                    class="icon-btn"
                    aria-label="More actions"
                  >
                    <span class="material-symbols-outlined">more_vert</span>
                  </button>
                  <div
                    v-if="showActionsMenu === student.id"
                    ref="actionsMenuRef"
                    class="absolute z-50 bg-white border border-emerald-100 rounded-xl shadow-lg mt-2 left-full ml-2 min-w-[140px]"
                  >
                    <button
                      @click="resetStudent(student)"
                      class="block w-full text-left px-4 py-2 hover:bg-emerald-50 flex items-center gap-2"
                    >
                      <span class="material-symbols-outlined text-red-500">refresh</span>
                      Reset
                    </button>
                  </div>
                </template>
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
      <!-- View Students by School (now includes Mark Present/Absent) -->
      <section v-if="activeSection === 'students'">
        <h2 class="section-title flex items-center gap-2">
          <span class="material-symbols-outlined text-emerald-500">groups</span>View Students
        </h2>
        <div class="flex gap-4 items-center mb-4 mt-2">
          <label class="font-semibold text-emerald-800">School:</label>
          <select
            v-model="selectedSchool"
            @change="fetchAllStudents"
            class="rounded-lg border border-emerald-200 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-400"
          >
            <option value="">All Assigned Schools</option>
            <option v-for="school in instructorSchools" :key="school" :value="school">
              {{ school }}
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
              <th>Status</th>
              <th>Attendance</th>
              <th>Last Attendance</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(student, idx) in paginatedStudents" :key="student.id" class="border-b">
              <td>{{ (studentPage - 1) * studentsPerPage + idx + 1 }}</td>
              <td>{{ student.name }}</td>
              <td>{{ student.email }}</td>
              <td>{{ student.studentId }}</td>
              <td>
                <span v-if="student.is_active" class="text-emerald-600 font-semibold">
                  Active
                </span>
                <span v-else class="text-orange-600 font-semibold"> Pending Approval </span>
              </td>
              <td>
                <template v-if="getTodayAttendance(student.studentId)">
                  <span
                    :class="{
                      'text-emerald-600 font-semibold':
                        getTodayAttendance(student.studentId)?.status === 'present',
                      'text-red-600 font-semibold':
                        getTodayAttendance(student.studentId)?.status === 'absent',
                    }"
                  >
                    {{
                      getTodayAttendance(student.studentId)?.status === 'present'
                        ? 'Present'
                        : 'Absent'
                    }}
                  </span>
                </template>
                <template v-else>
                  <span class="text-gray-500 font-semibold">Not Marked</span>
                </template>
              </td>
              <td>
                <span v-if="getLastAttendance(student.studentId)">
                  {{ toPhilippineTime(getLastAttendance(student.studentId)?.date || '') }}
                </span>
                <span v-else class="text-gray-400">-</span>
              </td>
              <td class="flex gap-2 py-2 justify-start">
                <template v-if="getTodayAttendance(student.studentId)">
                  <div class="relative">
                    <button
                      @click="openActionsMenu(student.id)"
                      class="icon-btn"
                      aria-label="More actions"
                    >
                      <span class="material-symbols-outlined">more_vert</span>
                    </button>
                    <div
                      v-if="showActionsMenu === student.id"
                      ref="actionsMenuRef"
                      class="absolute z-50 bg-white border border-emerald-100 rounded-xl shadow-lg mt-2 left-full ml-2 min-w-[140px]"
                    >
                      <button
                        @click="openEditAttendanceModal(student)"
                        class="block w-full text-left px-4 py-2 hover:bg-emerald-50 flex items-center gap-2"
                      >
                        <span class="material-symbols-outlined text-emerald-500">edit</span>
                        Edit Attendance
                      </button>
                    </div>
                  </div>
                </template>
                <template v-else>
                  <button
                    @click="markPresent(student)"
                    :disabled="!student.is_active"
                    class="action-btn-mini bg-emerald-600 hover:bg-emerald-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-full px-3 py-1.5 text-sm shadow transition duration-150"
                    aria-label="Mark Present"
                  >
                    Present
                  </button>
                  <button
                    @click="markAbsent(student)"
                    :disabled="!student.is_active"
                    class="action-btn-mini bg-red-500 hover:bg-red-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-full px-3 py-1.5 text-sm shadow transition duration-150"
                    aria-label="Mark Absent"
                  >
                    Absent
                  </button>
                </template>
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
      <!-- Attendance Summary with Filter -->
      <section v-if="activeSection === 'summary'">
        <h2 class="section-title flex items-center gap-2">
          <span class="material-symbols-outlined text-emerald-500">summarize</span>Attendance
          Summary
        </h2>
        <!-- Filters -->
        <div class="flex gap-4 items-center mb-6 mt-2 flex-wrap">
          <div class="flex gap-2 items-center">
            <label class="font-semibold text-emerald-800">School:</label>
            <select
              v-model="summarySchoolFilter"
              class="rounded-lg border border-emerald-200 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-400"
            >
              <option value="">All Schools</option>
              <option v-for="school in instructorSchools" :key="school" :value="school">
                {{ school }}
              </option>
            </select>
          </div>
          <div class="flex gap-2 items-center">
            <label class="font-semibold text-emerald-800">Attendance:</label>
            <select
              v-model="summaryAttendanceFilter"
              class="rounded-lg border border-emerald-200 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-400"
            >
              <option value="">All</option>
              <option value="present">Present</option>
              <option value="absent">Absent</option>
              <option value="not_marked">Not Marked</option>
            </select>
          </div>
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
            <tr v-for="(student, idx) in paginatedSummary" :key="student.id" class="border-b">
              <td>{{ (summaryPage - 1) * summaryPerPage + idx + 1 }}</td>
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
              <td>
                <button
                  @click="openAttendanceModal(student)"
                  class="action-btn-mini bg-emerald-500 hover:bg-emerald-700 text-white rounded-full px-4 py-2 text-sm shadow transition duration-150 min-w-[110px]"
                >
                  View Details
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="flex justify-center items-center gap-2 mt-6">
          <button
            @click="goToSummaryPage(summaryPage - 1)"
            :disabled="summaryPage === 1"
            class="px-3 py-1 rounded bg-emerald-100 text-emerald-700 font-bold disabled:opacity-50"
          >
            Prev
          </button>
          <span class="font-semibold">Page {{ summaryPage }} of {{ summaryTotalPages }}</span>
          <button
            @click="goToSummaryPage(summaryPage + 1)"
            :disabled="summaryPage === summaryTotalPages"
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
      <!-- Update Profile -->
      <section v-if="activeSection === 'profile'">
        <h2 class="section-title flex items-center gap-2">
          <span class="material-symbols-outlined text-emerald-500">person</span>Update Profile
        </h2>
        <div v-if="!editingProfile">
          <div class="mb-2">
            <span class="block text-lg font-bold text-emerald-700">Name:</span>
            <span class="block text-xl">{{ profile.name }}</span>
          </div>
          <div class="mb-2">
            <span class="block text-lg font-bold text-emerald-700">Email:</span>
            <span class="block text-xl">{{ profile.email }}</span>
          </div>
          <div class="mb-2">
            <span class="block text-lg font-bold text-emerald-700">Assigned School(s):</span>
            <span class="block text-xl">{{ profile.school || 'No school assigned yet.' }}</span>
          </div>
          <div class="mb-2">
            <span class="block text-lg font-bold text-emerald-700">Date of Birth:</span>
            <span class="block text-xl">{{ profile.dob || 'N/A' }}</span>
          </div>
          <button
            @click="startEditProfile"
            class="action-btn bg-emerald-600 hover:bg-emerald-700 mt-4"
          >
            Edit Profile
          </button>
        </div>
        <div v-else>
          <div class="mb-2">
            <label class="block text-lg font-bold text-emerald-700">Name:</label>
            <input
              v-model="profileForm.name"
              class="w-full rounded-lg border border-emerald-200 px-4 py-2 mt-1"
            />
          </div>
          <div class="mb-2">
            <label class="block text-lg font-bold text-emerald-700">Email:</label>
            <input
              v-model="profileForm.email"
              class="w-full rounded-lg border border-emerald-200 px-4 py-2 mt-1"
            />
          </div>
          <div class="mb-2">
            <label class="block text-lg font-bold text-emerald-700">Assigned School(s):</label>
            <input
              v-model="profileForm.school"
              class="w-full rounded-lg border border-emerald-200 px-4 py-2 mt-1"
            />
          </div>
          <div class="mb-2">
            <label class="block text-lg font-bold text-emerald-700">Date of Birth:</label>
            <input
              v-model="profileForm.dob"
              class="w-full rounded-lg border border-emerald-200 px-4 py-2 mt-1"
            />
          </div>
          <div class="flex gap-3 mt-4">
            <button @click="saveProfile" class="action-btn bg-emerald-600 hover:bg-emerald-700">
              Save
            </button>
            <button @click="cancelEditProfile" class="action-btn bg-gray-400 hover:bg-gray-500">
              Cancel
            </button>
          </div>
        </div>
        <slot name="profile-form">
          <!-- Profile Form Placeholder -->
        </slot>
      </section>
      <!-- Generate Reports -->
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
            <option v-for="school in instructorSchools" :key="school" :value="school">
              {{ school }}
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
      <section v-if="activeSection === 'report-summary'">
        <h2 class="section-title flex items-center gap-2">
          <span class="material-symbols-outlined text-emerald-500">bar_chart</span>Generate Report:
          Attendance Summary
        </h2>
        <div class="flex gap-4 items-center mb-4 mt-2">
          <label class="font-semibold text-emerald-800">School:</label>
          <select
            v-model="summaryReportSchool"
            class="rounded-lg border border-emerald-200 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-400"
          >
            <option value="">All Schools</option>
            <option v-for="school in getUniqueSchools()" :key="school" :value="school">
              {{ school }}
            </option>
          </select>
          <label class="font-semibold text-emerald-800">Date:</label>
          <input
            type="date"
            v-model="summaryReportDate"
            class="rounded-lg border border-emerald-200 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-400"
          />
          <button
            @click="clearSummaryReport"
            class="ml-2 px-3 py-1.5 rounded bg-gray-100 text-gray-700 hover:bg-gray-200 text-xs"
          >
            Clear
          </button>
        </div>
        <table class="w-full mb-4">
          <thead>
            <tr class="text-left text-emerald-700">
              <th>
                <input
                  type="checkbox"
                  :checked="isAllSummarySchoolsSelected()"
                  @change="toggleAllSummarySchools(($event.target as HTMLInputElement)?.checked)"
                />
              </th>
              <th>School</th>
              <th>Date</th>
              <th>Present (Student IDs)</th>
              <th>Absent (Student IDs)</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="school in getUniqueSchools().filter(
                (s) => !summaryReportSchool || s === summaryReportSchool,
              )"
              :key="school"
              class="border-b"
            >
              <td>
                <input
                  type="checkbox"
                  :checked="summaryReportSelectedSchools.includes(school)"
                  @change="toggleSummarySchool(school)"
                />
              </td>
              <td>{{ school }}</td>
              <td>{{ summaryReportDate }}</td>
              <td>
                <span
                  v-for="(id) in getSchoolPresentIdsOnDate(school, summaryReportDate).slice(
                    0,
                    3,
                  )"
                  :key="id"
                  class="inline-block bg-emerald-100 text-emerald-700 rounded px-2 py-1 mr-1 mb-1 text-xs font-mono"
                  >{{ id }}</span
                >
                <template v-if="getSchoolPresentIdsOnDate(school, summaryReportDate).length > 3">
                  <details>
                    <summary class="cursor-pointer text-emerald-600 text-xs inline">
                      Show more
                    </summary>
                    <div>
                      <span
                        v-for="id in getSchoolPresentIdsOnDate(school, summaryReportDate).slice(3)"
                        :key="id"
                        class="inline-block bg-emerald-50 text-emerald-700 rounded px-2 py-1 mr-1 mb-1 text-xs font-mono"
                        >{{ id }}</span
                      >
                    </div>
                  </details>
                </template>
              </td>
              <td>
                <span
                  v-for="(id) in getSchoolAbsentIdsOnDate(school, summaryReportDate).slice(
                    0,
                    3,
                  )"
                  :key="id"
                  class="inline-block bg-red-100 text-red-700 rounded px-2 py-1 mr-1 mb-1 text-xs font-mono"
                  >{{ id }}</span
                >
                <template v-if="getSchoolAbsentIdsOnDate(school, summaryReportDate).length > 3">
                  <details>
                    <summary class="cursor-pointer text-red-600 text-xs inline">Show more</summary>
                    <div>
                      <span
                        v-for="id in getSchoolAbsentIdsOnDate(school, summaryReportDate).slice(3)"
                        :key="id"
                        class="inline-block bg-red-50 text-red-700 rounded px-2 py-1 mr-1 mb-1 text-xs font-mono"
                        >{{ id }}</span
                      >
                    </div>
                  </details>
                </template>
              </td>
            </tr>
          </tbody>
        </table>
        <button
          class="action-btn bg-emerald-700 hover:bg-emerald-800"
          @click="downloadReportSummary"
        >
          <span class="material-symbols-outlined">download</span>Download
        </button>
      </section>
      <section v-if="activeSection === 'report-per-student'">
        <h2 class="section-title flex items-center gap-2">
          <span class="material-symbols-outlined text-emerald-500">person_search</span>Generate
          Report: Per-Student Summary
        </h2>
        <div class="flex gap-4 items-center mb-4 mt-2">
          <label class="font-semibold text-emerald-800">School:</label>
          <select
            v-model="reportPerStudentSchoolFilter"
            class="rounded-lg border border-emerald-200 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-400"
          >
            <option value="">All Schools</option>
            <option v-for="school in instructorSchools" :key="school" :value="school">
              {{ school }}
            </option>
          </select>
          <input
            v-model="reportPerStudentSearch"
            placeholder="Search student..."
            class="rounded-lg border border-emerald-200 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-400"
          />
        </div>
        <table class="w-full mb-4">
          <thead>
            <tr class="text-left text-emerald-700">
              <th>
                <input
                  type="checkbox"
                  :checked="allPerStudentSelected"
                  @change="toggleSelectAllPerStudent"
                />
              </th>
              <th>#</th>
              <th>Name</th>
              <th>Email</th>
              <th>Total Presents</th>
              <th>Total Absences</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(student, idx) in filteredReportPerStudent"
              :key="student.id"
              class="border-b"
            >
              <td>
                <input
                  type="checkbox"
                  :checked="selectedStudentIds.includes(student.id)"
                  @change="toggleStudentSelection(student.id)"
                />
              </td>
              <td>{{ idx + 1 }}</td>
              <td>{{ student.name }}</td>
              <td>{{ student.email }}</td>
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
          @click="downloadReportPerStudent"
          :disabled="selectedStudentIds.length === 0"
        >
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

  <!-- Add Edit Attendance Modal -->
  <div
    v-if="editAttendanceModal.show"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40"
  >
    <div class="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-sm relative">
      <h3 class="font-bold text-xl mb-4 text-emerald-800">
        Edit Attendance for {{ editAttendanceModal.student?.name }}
      </h3>
      <div class="mb-4">
        <label class="block text-lg font-bold text-emerald-700 mb-2">Status:</label>
        <select
          v-model="editAttendanceModal.newStatus"
          class="rounded-lg border border-emerald-200 px-4 py-2 w-full"
        >
          <option value="present">Present</option>
          <option value="absent">Absent</option>
        </select>
      </div>
      <div class="flex justify-end gap-3 mt-4">
        <button
          @click="closeEditAttendanceModal"
          class="px-4 py-2 rounded font-semibold bg-gray-100 text-gray-700 hover:bg-gray-200"
        >
          Cancel
        </button>
        <button
          @click="saveEditAttendance"
          class="px-4 py-2 rounded font-semibold bg-emerald-600 text-white hover:bg-emerald-700"
        >
          Save
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined');

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
.action-menu-btns {
  background: #fff;
  border: 1px solid #e0e0e0;
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.07);
  border-radius: 9999px;
  padding: 0.25rem 0.5rem;
  margin-left: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.navbar-modern {
  @apply shadow-md rounded-full px-6 py-3 border border-emerald-100;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 320px;
  max-width: 90vw;
}

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

.icon-btn {
  @apply w-8 h-8 rounded-full flex items-center justify-center text-gray-600 hover:bg-gray-100 transition duration-150;
  position: relative;
  margin: 0 auto;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .nav-link {
    font-size: 0.95rem;
    padding: 0.5rem 1rem;
  }
  .card-section {
    padding: 1.5rem 1rem;
  }
  .section-title {
    font-size: 1.1rem;
  }
}
</style>
