<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import UserList from '@/components/Users/UserList.vue'

const route = useRoute()
const router = useRouter()

const activeTab = ref('all') // 'all' or 'leaders'
if (route.path.endsWith('/leaders')) activeTab.value = 'leaders'

watch(route, (r) => {
	if (r.path.endsWith('/leaders')) activeTab.value = 'leaders'
	else activeTab.value = 'all'
})

const userListRef = ref(null)

const selectTab = (tab) => {
	activeTab.value = tab
	if (tab === 'leaders') router.push('/dashboard/users/leaders')
	else router.push('/dashboard/users')
}

</script>

<template>
	<div class="space-y-6">
		<div class="flex justify-between items-center">
			<div>
				<h1 class="text-2xl font-bold text-gray-900">User Management</h1>
				<p class="text-sm text-gray-500">Manage all users and leaders in the system</p>
			</div>
			<div>
				<button class="px-4 py-2 bg-blue-500 text-white rounded">Add User</button>
			</div>
		</div>

		<div class="bg-white rounded-xl p-4">
			<div class="flex gap-2 mb-4">
				<button :class="['px-4 py-2 rounded', activeTab === 'all' ? 'bg-gray-100' : 'bg-white']" @click="selectTab('all')">All Users</button>
				<button :class="['px-4 py-2 rounded', activeTab === 'leaders' ? 'bg-gray-100' : 'bg-white']" @click="selectTab('leaders')">Leaders</button>
			</div>

			<div>
				<table class="min-w-full divide-y divide-gray-200">
					<thead>
						<tr class="bg-gray-50">
							<th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">User</th>
							<th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Fullname</th>
							<th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Email</th>
							<th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Role</th>
							<th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Status</th>
							<th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Actions</th>
						</tr>
					</thead>
					<tbody>
						<UserList ref="userListRef" :mode="activeTab" />
					</tbody>
				</table>
			</div>
		</div>
	</div>
</template>