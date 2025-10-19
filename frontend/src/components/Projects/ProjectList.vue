<script setup>
import { ref, onMounted } from 'vue'
import { getProjects, deleteProject } from '@/api/projectAPi'
import ProjectTableRow from './ProjectTableRow.vue'
const emit = defineEmits(['edit'])

const projects = ref([])
const loading = ref(true)

const fetchProjects = async () => {
  loading.value = true
  try {
    projects.value = await getProjects()
  } catch (error) {
    console.error('Failed to fetch projects:', error)
  } finally {
    loading.value = false
  }
}

const handleEdit = (project) => {
  // Emit to parent so the parent can open an edit modal
  emit('edit', project)
}

const handleDelete = async (project) => {
  if (!confirm('Are you sure?')) return
  try {
    await deleteProject(project.id)
    await fetchProjects()
  } catch (error) {
    console.error('Failed to delete:', error)
  }
}

onMounted(fetchProjects)

// Expose fetchProjects to parent components so they can trigger a reload
defineExpose({ fetchProjects })
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
    <ProjectTableRow
      v-for="project in projects"
      :key="project.id"
      :project="project"
      @edit="handleEdit"
      @delete="handleDelete"
    />
  </template>
</template>