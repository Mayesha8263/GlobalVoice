<template>
  <body>
    <!-- Render TranslationForm component and send languageCodes as a prop -->
    <TranslationForm :language-codes="languageCodes" />
  </body>
</template>

<script>
import { useRoute } from 'vue-router';
import TranslationForm from '../components/TranslationForm.vue';

export default {
  setup() {
      const route = useRoute();
  },
  components: {
    TranslationForm,
  },
  props: {
    // Define userId prop with type and is required
    userId: {
      type:Number,
      required: true,
    },
  },
  data() {
    return {
      languageCodes: [],
    };
  },
  mounted() {
    // Fetch language codes when component is mounted
    this.fetchLanguageCodes();
  },
  methods: {
    // Fetch all language codes from server
    async fetchLanguageCodes() {
      try {
        const response = await fetch('http://localhost:8000/globalVoice/getLanguages/');
        const data = await response.json();
        this.languageCodes = data.languages;
      } catch (error) {
        console.error('Error fetching language codes:', error);
      }
    },
  },
};
</script>

<style scoped>
</style>