// src/composables/useKanbanDnd.js
import { ref } from 'vue';
import { useAuthStore } from '@/store/auth';
import { updateTask } from '@/api/taskApi';

export function useKanbanDnd(listsRef, { isEnterprise, isLeader, isPersonalOwner }, fetchKanban) {
  const auth = useAuthStore();

  const canDragTask = (t) => {
    const u = auth.user;
    if (!u) return false;
    if (t?.status === 'done') return false;
    if (isPersonalOwner.value) return true; // personal projects owner can move all
    // enterprise: leader can move unassigned tasks only
    if (isEnterprise.value && isLeader.value && !t?.assignee) return true;
    // assignee can drag their own task
    if (t?.assignee?.id === u.id) return true;
    return false;
  };

  const dragging = ref(null); // { taskId, fromListId }
  const dragOverListId = ref(null);

  const statusForListName = (name) => {
    const key = String(name || '').toLowerCase();
    if (key.includes('progress')) return 'in_progress';
    if (key.includes('done')) return 'done';
    return 'todo';
  };

  const onDragStart = (evt, task, list) => {
    if (!canDragTask(task)) return;
    dragging.value = { taskId: task.id, fromListId: list.id };
    try {
      evt.dataTransfer?.setData('text/plain', String(task.id));
    } catch { /* void */ }
  };

  const onDragOver = (evt, list) => {
    if (!dragging.value) return;
    evt.preventDefault();
    dragOverListId.value = list.id;
  };

  const onDragLeave = (evt, list) => {
    if (dragOverListId.value === list.id) dragOverListId.value = null;
  };

  const onDrop = async (evt, targetList) => {
    if (!dragging.value) return;
    evt.preventDefault();
    const { taskId, fromListId } = dragging.value;
    dragOverListId.value = null;
    dragging.value = null;
    if (fromListId === targetList.id) return;
    try {
      const from = listsRef.value.find((l) => l.id === fromListId);
      const to = listsRef.value.find((l) => l.id === targetList.id);
      if (!from || !to) return;
      const idx = (from.tasks || []).findIndex((t) => t.id === taskId);
      if (idx === -1) return;
      const moving = from.tasks[idx];
      if (!canDragTask(moving)) return; 
      // forward-only constraints, and lock last column
      if ((from.position ?? from?.pos ?? 0) >= 3) return;
      if ((to.position ?? to?.pos ?? 0) < (from.position ?? from?.pos ?? 0)) return;

      await updateTask(taskId, { list: targetList.id });
      // Move locally
      const [moved] = from.tasks.splice(idx, 1);
      moved.status = statusForListName(to.name);
      moved.list = targetList.id;
      to.tasks = to.tasks || [];
      to.tasks.push(moved);
    } catch (e) {
      await fetchKanban();
    }
  };

  return {
    canDragTask,
    dragging,
    dragOverListId,
    statusForListName,
    onDragStart,
    onDragOver,
    onDragLeave,
    onDrop,
  };
}
