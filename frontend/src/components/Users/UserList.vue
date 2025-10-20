<script setup>
import { ref, onMounted, watch } from 'vue'
import { getUsers, getLeaders } from '@/api/userApi'
import UserTableRow from '@/components/Users/UserTableRow.vue'

const props = defineProps({
  mode: { type: [String, Object], default: 'all' } // 'all' or 'leaders'
})

const users = ref([])
const loading = ref(true)

const fetchUsers = async () => {
  loading.value = true
  try {
    users.value = await getUsers()
  } catch (error) {
    console.error('Failed to fetch users:', error)
  } finally {
    loading.value = false
  }
}

const fetchLeaders = async () => {
  loading.value = true
  try {
    users.value = await getLeaders()
  } catch (error) {
    console.error('Failed to fetch leaders:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (props.mode === 'leaders' || props.mode === 'leaders') fetchLeaders()
  else fetchUsers()
})

watch(() => props.mode, (m) => {
  if (m === 'leaders') fetchLeaders()
  else fetchUsers()
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