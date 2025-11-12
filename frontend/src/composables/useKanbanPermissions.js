// src/composables/useKanbanPermissions.js
import { computed, ref, watch } from 'vue';
import { useAuthStore } from '@/store/auth';

export function useKanbanPermissions(projectRef, listsRef) {
  const auth = useAuthStore();

  const isEnterprise = computed(() => !projectRef.value?.is_personal);

  const isLeader = computed(() => {
    const u = auth.user;
    if (!u || !projectRef.value) return false;
    return projectRef.value?.leader?.id === u.id;
  });

  const isPersonalOwner = computed(() => {
    const u = auth.user;
    if (!u || !projectRef.value) return false;
    return !!projectRef.value?.is_personal && projectRef.value?.owner?.id === u.id;
  });

  // View filter: default show only my tasks for non-leader/non-owner
  const showOnlyMine = ref(true);
  watch(
    () => [projectRef.value?.id, isLeader.value, isPersonalOwner.value],
    () => {
      showOnlyMine.value = !(isLeader.value || isPersonalOwner.value);
    },
    { immediate: true }
  );

  const isMyTask = (t) => {
    const u = auth.user;
    if (!u) return false;
    if (isLeader.value || isPersonalOwner.value) return true;
    return t?.assignee?.id === u.id;
  };

  // View permission on board: deny admins; allow leader, personal owner, or members (assignee of any task in project)
  const isAssigneeInProject = computed(() => {
    const u = auth.user;
    if (!u) return false;
    for (const col of listsRef.value || []) {
      for (const t of col.tasks || []) {
        if (t?.assignee?.id === u.id) return true;
      }
    }
    return false;
  });

  const canViewBoard = computed(() => {
    const u = auth.user;
    if (!u) return false;
    if (u.role === 'admin') return false;
    if (isLeader.value || isPersonalOwner.value) return true;
    return isAssigneeInProject.value;
  });

  return {
    isEnterprise,
    isLeader,
    isPersonalOwner,
    showOnlyMine,
    isMyTask,
    canViewBoard,
  };
}
