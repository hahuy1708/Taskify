<script setup>
import { ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import UserList from "@/components/Users/UserList.vue";
import { UserCog, UserCircle } from "lucide-vue-next";

const route = useRoute();
const router = useRouter();

const activeTab = ref("all"); // 'all' or 'leaders'
if (route.path.endsWith("/leaders")) activeTab.value = "leaders";

watch(route, (r) => {
  if (r.path.endsWith("/leaders")) activeTab.value = "leaders";
  else activeTab.value = "all";
});

const userListRef = ref(null);

const selectTab = (tab) => {
  activeTab.value = tab;
  if (tab === "leaders") router.push("/dashboard/users/leaders");
  else router.push("/dashboard/users");
};
</script>

<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">User Management</h1>
        <p class="text-sm text-gray-500">
          Manage all users and leaders in the system
        </p>
      </div>
      <div>
        <button class="px-4 py-2 bg-blue-500 text-white rounded">
          Add User
        </button>
      </div>
    </div>

    <div class="bg-white rounded-xl p-4">
      <div class="flex gap-3 mb-4">
        <button
          @click="selectTab('all')"
          :class="[
            'flex items-center gap-2 px-4 py-2 rounded-lg border transition-all',
            activeTab === 'all'
              ? 'bg-indigo-50 border-indigo-300 text-indigo-700 font-medium'
              : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50',
          ]"
        >
          <UserCircle class="w-4 h-4" />
          <span>All Users</span>
        </button>

        <button
          @click="selectTab('leaders')"
          :class="[
            'flex items-center gap-2 px-4 py-2 rounded-lg border transition-all',
            activeTab === 'leaders'
              ? 'bg-indigo-50 border-indigo-300 text-indigo-700 font-medium'
              : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50',
          ]"
        >
          <UserCog class="w-4 h-4" />
          <span>Leaders</span>
        </button>
      </div>

      <div>
        <table class="min-w-full divide-y divide-gray-200">
          <thead>
            <tr class="bg-gray-50">
              <th
                class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase"
              >
                User
              </th>
              <th
                class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase"
              >
                Fullname
              </th>
              <th
                class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase"
              >
                Email
              </th>
              <th
                class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase"
              >
                Role
              </th>
              <th
                class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase"
              >
                Status
              </th>
              <th
                class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase"
              >
                Actions
              </th>
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
