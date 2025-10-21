<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { getProfile, getUserDetail } from "@/api/authApi";
import UserEditModal from "@/components/Users/Modals/UserEditModal.vue";
import UserSetPasswordModal from "@/components/Users/Modals/UserSetPasswordModal.vue";

const user = ref(null);
const loading = ref(true);
const showEditModal = ref(false);
const showSetPasswordModal = ref(false);

const route = useRoute();

const fetchUserProfile = async () => {
  loading.value = true;
  try {
    const userId = route.params.id;
    if (userId) {
      user.value = await getUserDetail(userId);
    } else {
      user.value = await getProfile();
    }
  } catch (error) {
    console.error("Failed to fetch user profile:", error);
  } finally {
    loading.value = false;
  }
};

const handleUpdateSuccess = (updatedUser) => {
  user.value = updatedUser;
  showEditModal.value = false;
};

const handleSetPasswordSuccess = () => {
  showSetPasswordModal.value = false;
  fetchUserProfile();
};

onMounted(fetchUserProfile);
</script>

<template>
  <div v-if="loading" class="flex justify-center items-center h-64">
    <div
  class="w-24 h-24 rounded-full bg-indigo-100 flex items-center justify-center text-3xl font-semibold text-indigo-600 shadow-sm"
>
  {{
    user && (user.full_name
      ? user.full_name.charAt(0).toUpperCase()
      : (user.username ? user.username.charAt(0).toUpperCase() : "U"))
  }}
</div>
  </div>

  <div
    v-else
    class="max-w-4xl mx-auto mt-10 bg-white shadow-md rounded-2xl p-8 border border-gray-100"
  >
    <div class="flex flex-col items-center mb-8">
      <div
        class="w-24 h-24 rounded-full bg-indigo-100 flex items-center justify-center text-3xl font-semibold text-indigo-600 shadow-sm"
      >
        {{
          user.full_name
            ? user.full_name.charAt(0).toUpperCase()
            : user.username.charAt(0).toUpperCase()
        }}
      </div>
      <h2 class="text-2xl font-bold mt-4 text-gray-800">{{ user.full_name }}</h2>
      <p class="text-gray-500 text-sm">{{ user.email }}</p>
    </div>

    <hr class="my-6 border-gray-200" />

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
      <div>
        <h3 class="text-lg font-semibold text-gray-700 mb-2">Account Info</h3>
        <div class="space-y-2 text-gray-600">
          <p><span class="font-semibold">Username:</span> {{ user.username }}</p>
          <p><span class="font-semibold">Role:</span> {{ user.role || "User" }}</p>
          <p><span class="font-semibold">Birthdate:</span> {{ user.birth_date || "—" }}</p>
        </div>
      </div>

      <div>
        <h3 class="text-lg font-semibold text-gray-700 mb-2">Contact Info</h3>
        <div class="space-y-2 text-gray-600">
          <p><span class="font-semibold">Phone:</span> {{ user.phone_number || "—" }}</p>
          <p><span class="font-semibold">Address:</span> {{ user.address || "—" }}</p>
        </div>
      </div>
    </div>

    <div class="mt-8 text-right space-x-3">
      <button
        @click="showEditModal = true"
        class="px-5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg shadow-sm transition duration-150"
      >
        Edit Profile
      </button>
      <button
        @click="showSetPasswordModal = true"
        class="px-5 py-2 bg-amber-500 hover:bg-amber-600 text-white font-medium rounded-lg shadow-sm transition duration-150"
      >
        Change Password
      </button>
    </div>
  </div>

  <!-- Modals -->
  <UserEditModal
    v-if="showEditModal"
    :user="user"
    @close="showEditModal = false"
    @success="handleUpdateSuccess"
  />

  <UserSetPasswordModal
    v-if="showSetPasswordModal"
    @close="showSetPasswordModal = false"
    @success="handleSetPasswordSuccess"
  />
</template>
