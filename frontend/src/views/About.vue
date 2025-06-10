<template>
  <div class="about">
    <h1>About</h1>
    <p>This is an elevator system simulation project built with:</p>
    <ul>
      <li>Vue 3</li>
      <li>TypeScript</li>
      <li>FastAPI</li>
      <li>PostgreSQL</li>
    </ul>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'AboutView'
})
</script>

<style scoped>
.about {
  padding: 20px;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  margin: 10px 0;
}
</style> 