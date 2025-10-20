<script setup>
import { toRefs } from 'vue'
import { EyeIcon, BanIcon } from 'lucide-vue-next'


const props = defineProps({
  user: { type: Object, required: true }
})

const { user } = toRefs(props)


</script>

<template>
  <tr class="border-b hover:bg-gray-50">
    <td class="px-6 py-4">
      <div class="flex items-center gap-3">
        <div class="h-8 w-8 rounded-full bg-indigo-100 flex items-center justify-center text-sm font-semibold text-indigo-700">{{ user.username ? user.username.charAt(0) : 'U' }}</div>
        <div>
          <router-link :to="`/dashboard/users/${user.id}`" class="text-xs text-gray-500 hover:underline">{{ user.username }}</router-link>
        </div>
      </div>
    </td>
    <td class="px-6 py-4">{{ user.full_name }}</td>
    <td class="px-6 py-4">{{ user.email }}</td>
    <td class="px-6 py-4">{{ user.role }}</td>
    <td class="px-6 py-4">
      <span :class="user.is_active ? 'text-emerald-600' : 'text-gray-500'">{{ user.is_active ? 'Active' : 'Inactive' }}</span>
    </td>
    <td class="px-6 py-4">
      <div class="flex items-center justify-center gap-3">
    <router-link :to="`/dashboard/users/${user.id}`" class="text-blue-600 hover:text-blue-800">
      <button class="w-5 h-5">
        <EyeIcon class="w-5 h-5" />
      </button>
    </router-link>
    <button class="text-red-600 hover:text-red-800">
      <BanIcon class="w-5 h-5" />
    </button>
  </div>
    </td>
  </tr>
</template>
