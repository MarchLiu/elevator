<template>
  <div class="home">
    <h1>Elevator System</h1>
    <div class="elevator-container">
      <!-- Elevator visualization will go here -->
      <p>Welcome to the elevator system. This is where the elevator visualization will be displayed.</p>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'HomeView'
})
</script>

<style scoped>
.home {
  padding: 20px;
}

.elevator-container {
  margin-top: 20px;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
</style> 