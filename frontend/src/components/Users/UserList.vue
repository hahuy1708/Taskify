<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getUsers, getLeaders } from '@/api/userApi'
import UserTableRow from '@/components/Users/UserTableRow.vue'

const props = defineProps({
  mode: { type: [String, Object], default: 'all' }, // 'all' or 'leaders'
  search: { type: String, default: '' }
})

const users = ref([])
const loading = ref(true)
const router = useRouter()

const fetchUsers = async (searchQuery) => {
  loading.value = true
  try {
    users.value = await getUsers(searchQuery)
  } catch (error) {
    if (error?.response?.status === 403) {
      router.push('/unauthorized')
      return
    }
    console.error('Failed to fetch users:', error)
  } finally {
    loading.value = false
  }
}

const fetchLeaders = async (searchQuery) => {
  loading.value = true
  try {
    users.value = await getLeaders(searchQuery)
  } catch (error) {
    if (error?.response?.status === 403) {
      router.push('/unauthorized')
      return
    }
    console.error('Failed to fetch leaders:', error)
  } finally {
    loading.value = false
  }
}

const loadByMode = (mode, searchQuery) =>{
  if(mode === 'leaders') fetchLeaders(searchQuery)
  else fetchUsers(searchQuery) 
}

onMounted(() => loadByMode(props.mode, props.search))

watch(() => props.mode, (newMode) => {
  loadByMode(newMode, props.search)
})

watch(() => props.search, (val) => {
  loadByMode(props.mode, val)
})

defineExpose({ fetchUsers, fetchLeaders })
</script>

<template>
  <template v-if="loading">
    <tr>
      <td colspan="6" class="text-center py-8">
        <div class="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto"></div>
      </td>
    </tr>
  </template>

  <template v-else>
    <UserTableRow
      v-for="user in users"
      :key="user.id"
      :user="user"
    />
  </template>
</template>