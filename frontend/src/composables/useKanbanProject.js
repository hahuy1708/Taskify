// src/composables/useKanbanProject.js
import { ref, watch } from 'vue';
import { getProjectDetails } from '@/api/projectAPi';

export function useKanbanProject(projectIdRef) {
  const project = ref(null);
  const lists = ref([]);
  const loading = ref(false);
  const error = ref('');

  const fetchKanban = async () => {
    const projectId = projectIdRef?.value;
    if (!projectId) {
      project.value = null;
      lists.value = [];
      return;
    }
    try {
      loading.value = true;
      error.value = '';
      const data = await getProjectDetails(projectId);
      project.value = data;
      lists.value = Array.isArray(data?.lists) ? data.lists : [];
    } catch (e) {
      error.value = 'Failed to load board.';
    } finally {
      loading.value = false;
    }
  };

  // Auto fetch when projectId changes
  watch(projectIdRef, fetchKanban, { immediate: true });

  return { project, lists, loading, error, fetchKanban };
}
