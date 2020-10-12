<template>
  <div class="text-center">
    <v-chip
      class="ma-2"
      color="#FF0000"
      dark
    >
      {{ extreme }}
    </v-chip>
    <v-chip
      class="ma-2"
      color="#FFB200"
      dark
    >
      {{ high }}
    </v-chip>
    <v-chip
      class="ma-2"
      color="#128FD9"
      dark
    >
      {{ medium }}
    </v-chip>
    <v-chip
      class="ma-2"
      color="#00A100"
      dark
    >
      {{ low }}
    </v-chip>
  </div>
</template>

<script>
export default {
  data () {
    return {
      extreme: 'Extreme (90% ~ 100%)',
      high: 'High (70% ~ 90%)',
      medium: 'Medium (40% ~ 70%)',
      low: 'Low (0 ~ 40%)'
    }
  }
};
</script>