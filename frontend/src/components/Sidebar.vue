<script setup>
import { computed, ref } from "vue";
import { useAuthStore } from "@/store/auth";
import {
  Home,
  Folder,
  Users,
  BarChart,
  Settings,
  CheckCircle,
  UserCog,
  UserCircle2,
} from "lucide-vue-next";

const store = useAuthStore();
const userRole = computed(() => store.user?.role || "user");
const usersOpen = ref(false);

const menuItems = computed(() => {
  if (userRole.value === "admin") {
    return [
      { to: "/dashboard/admin", icon: Home, label: "Dashboard" },
      { to: "/dashboard/projects", icon: Folder, label: "Projects" },
      { to: "/dashboard/users", icon: Users, label: "Users", hasSub: true },
      { to: "/dashobard/reports", icon: BarChart, label: "Reports" },
      { to: "/dashboard/settings", icon: Settings, label: "Settings" },
    ];
  } else {
    return [
      { to: "/dashboard/user", icon: Home, label: "My Dashboard" },
      { to: "/dashboard/projects", icon: Folder, label: "My Projects" },
      { to: "/dashboard/my-tasks", icon: CheckCircle, label: "My Tasks" },
      { to: "/dashboard/teams", icon: Users, label: "My Team" },
      { to: "/dashboard/settings", icon: Settings, label: "Settings" },
    ];
  }
});
</script>

<template>
  <aside class="w-64 bg-gray-900 text-white flex flex-col">
    <!-- Header -->
    <div class="flex items-center gap-3 px-5 h-16 border-b border-gray-800">
      <div class="h-9 w-9 rounded-xl bg-indigo-500 flex items-center justify-center font-bold">T</div>
      <div>
        <p class="text-base leading-none font-semibold">Taskify</p>
        <p class="text-xs text-gray-400 -mt-0.5">Project Management</p>
      </div>
    </div>

    <!-- Role section -->
    <div class="px-3 py-4 text-xs uppercase tracking-wider text-gray-400">
      {{ userRole === "admin" ? "Admin Panel" : "User Panel" }}
    </div>

    <!-- Navigation -->
    <nav class="px-2 space-y-1">
      <template v-for="item in menuItems" :key="item.to">
        <!-- Dropdown item -->
        <div v-if="item.hasSub" class="px-1">
          <button
            @click="usersOpen = !usersOpen"
            class="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-800 transition"
          >
            <component :is="item.icon" class="w-5 h-5 text-gray-300" />
            <span class="flex-1 text-left text-sm">{{ item.label }}</span>
            <span class="text-xs">{{ usersOpen ? "▾" : "▸" }}</span>
          </button>

          <div
            v-if="usersOpen"
            class="mt-1 space-y-1 pl-5 border-l border-gray-800 ml-4"
          >
            <!-- All Users -->
            <router-link
              to="/dashboard/users"
              class="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-800 transition text-sm text-gray-200"
            >
              <UserCircle2 class="w-4 h-4 text-gray-400" />
              <span>All Users</span>
            </router-link>

            <!-- Leaders -->
            <router-link
              to="/dashboard/users/leaders"
              class="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-800 transition text-sm text-gray-200"
            >
              <UserCog class="w-4 h-4 text-gray-400" />
              <span>Leaders</span>
            </router-link>
          </div>
        </div>

        <!-- Normal item -->
        <router-link
          v-else
          :to="item.to"
          class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-800 transition text-sm"
        >
          <component :is="item.icon" class="w-5 h-5 text-gray-300" />
          <span class="text-gray-100">{{ item.label }}</span>
        </router-link>
      </template>
    </nav>

    <div class="mt-auto p-4 text-sm text-gray-400">© 2025 Taskify</div>
  </aside>
</template>
