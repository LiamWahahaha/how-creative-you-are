<template>
  <v-container fluid>
    <v-layout justify-center>
      <v-card
        width="1200"
        class="mx-auto pt-2"
        flat
      >
        <v-card flat>
          <v-card-title>
            <h1>
              Kernel Catcher
            </h1>
          </v-card-title>
          <v-card-subtitle>
            <h2>
              Catch Kernel thief between different Kaggle Kernels
            </h2>
          </v-card-subtitle>
          <v-card-title>
            Search by CompetitionID
          </v-card-title>
          <v-card-text>
            <v-text-field
              outlined
              v-model="competition"
              append-icon="mdi-magnify"
              type="text"
              clearable
              @click:append="search"
            />
          </v-card-text>
        </v-card>
        <v-divider dark/>
        <v-card
          flat
          class="pt-5"
        >
          <v-card-title>
            Competition Information
          </v-card-title>
          <v-layout justify-space-around class='text-center'>
            <v-flex>
              <h3>{{ categories }}</h3>
              <p>Categories</p>
            </v-flex>
            <v-spacer/>
            <v-flex>
              <h3>{{ teams }}</h3>
              <p>Teams</p>
            </v-flex>
            <v-spacer/>
            <v-flex xs3>
              <h3>{{ competitors }}</h3>
              <p>Competitors</p>
            </v-flex>
            <v-flex xs3>
              <h3>{{ entries }}</h3>
              <p>Entries</p>
            </v-flex>
          </v-layout>
          <v-card-title>
            Result
            <Information/>
          </v-card-title>
          <v-card-subtitle>
            Only Display Top 50
          </v-card-subtitle>
          <v-card-text>
            <v-data-table
              height="350"
              fixed-header
              :headers="headers"
              :items="records"
              no-data-text="N/A"
            >
              <template v-slot:item.similarity_score="{ item }">
                <v-chip
                  :color="getColor(item.similarity_score)"
                  dark
                >
                  {{ item.similarity_score | showThreeDigit }}
                </v-chip>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-card>
    </v-layout>
  </v-container>
</template>

<script>
import Information from './Information';
import axios from 'axios';

export default {
  components: {
    Information
  },
  filters: {
    showThreeDigit: function (value) {
      if (value == -1) value = 0
      value = value * 100
      return value.toFixed(3)
    }
  },
  data () {
    return {
      competition: '',
      competitors: 'N/A',
      teams: 'N/A',
      categories: 'N/A',
      entries: 'N/A',
      headers: [
        {
          text: 'Competitor A/Kernel',
          align: 'start',
          sortable: false,
          value: 'suspect',
        },
        {
          text: 'Competitor B/Kernel',
          sortable: false,
          value: 'victim'
        },
        {
          text: 'Imported Packages',
          sortable: false,
          value: 'packages'
        },
        {
          text: 'Similarity Score',
          align: 'center',
          sortable: false,
          value: 'similarity_score'
        }
      ],
      records: []
    }
  },
  methods: {
    getColor (similarity_score) {
      if (similarity_score > 0.9) return '#FF0000'
      else if (similarity_score > 0.7) return '#FFB200'
      else if (similarity_score > 0.4) return '#128FD9'
      else return '#00A100'
    },
    retrieveCompetitionMeta () {
      const vm = this
      axios.get('http://52.207.89.168:5000/competition-meta', {
        params: {
          competition_id: this.competition
        }
      })
      .then(response => {
        vm.categories = response.data.categories || 'N/A'
        vm.teams = response.data.teams || 'N/A'
        vm.competitors = response.data.competitors || 'N/A'
        vm.entries = response.data.entries || 'N/A'
      })
      .catch(error => {
        console.log(error)
        vm.categories = 'N/A'
        vm.teams = 'N/A'
        vm.competitors = 'N/A'
        vm.entries = 'N/A'
      })

    },
    retrieveSimilarityScores () {
      const vm = this
      axios.get('http://52.207.89.168:5000/similarity-scores', {
        params: {
          competition_id: this.competition,
          top_n: 50
        }
      })
      .then(response => {
        vm.records = response.data.similarity_scores
      })
      .catch(error => {
        console.log(error)
        vm.records = []
      })
    },
    search () {
      this.retrieveCompetitionMeta()
      this.retrieveSimilarityScores()
    }
  },
}
</script>