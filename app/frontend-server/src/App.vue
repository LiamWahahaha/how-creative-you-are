<template>
  <v-app>
    <v-main>
      <SimilarityDataTable/>
    </v-main>
  </v-app>
</template>

<script>
import SimilarityDataTable from './components/SimilarityDataTable';

export default {
  name: 'App',

  components: {
    SimilarityDataTable
  },

  data: () => ({})
};
</script>
