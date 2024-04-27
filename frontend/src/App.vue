<template>
  <div id="app">
    <header>
      <!-- Navigation bar -->
      <nav class="navbar">
        <div class="nav-group">
          <img :src="logoUrl" alt="Logo" class="logo" />
          <h1 class="title">GlobalVoice</h1>
        </div>

        <!-- Navigation links -->
        <ul class="nav-links">
          <!-- Profile page link that is visible when logged in -->
          <li v-if="loggedIn" class="nav-link">
            <router-link
              class="nav-link"
              :to="{ name: 'Profile' }"
            >
              Profile
            </router-link>
          </li>
          <!-- Phrasebook page link that is visible when logged in -->
          <li v-if="loggedIn" class="nav-link">
            <router-link
              class="nav-link"
              :to="{ name: 'My Phrasebook' }"
            >
              My Phrasebook
            </router-link>
          </li>
          <!-- Translation page link -->
          <li class="nav-link">
            <router-link
              class="nav-link"
              :to="{ name: 'Translator' }"
            >
              Translator
            </router-link>
          </li>
          <!-- Login link when not logged in -->
          <li v-if="!loggedIn" class="nav-link" data-bs-toggle="modal" data-bs-target="#LoginModal">
            Login
          </li>
          <!-- Logout link for when user is logged in -->
          <li v-if="loggedIn" class="nav-link" @click="logout">
            Logout
          </li>
        </ul>
      </nav>
    </header>

    <!-- Render components based on routes -->
    <RouterView 
      class="flex-shrink-0" 
    />

    <!-- LoginForm component -->
    <LoginForm :formData="formData" @clear-form="clearForm" />
    </div>
</template>
  
<script>
import { RouterView } from 'vue-router';
import TranslationForm from './components/TranslationForm.vue';
import LoginForm from './components/LoginForm.vue';
import logo from './assets/logo.png';

export default {
  components: {
    RouterView,
    TranslationForm,
    LoginForm,
  },
  computed: {
    // Computed to determine is user is logged in
    loggedIn() {
      return this.$store.state.loggedIn;
    },
  },
  data() {
    return {
      formData: {
        username: '',
        email: '',
        password: '',
      },
      logoUrl: logo,
    };
  },
  created() {
    // Redirect to Translator page
    this.$router.push({name: 'Translator'});
  },
  methods: {
    // Clear forms and set logged in status to true
    async clearForm() {
      this.$store.commit('setLoggedIn', true);
      this.formData = {
          username: '',
          email: '',
          password: '',
      };
    },

    // Handle user logout
    async logout() {
      try {
        const response = await fetch('http://localhost:8000/globalVoice/logout/', {
          method: 'POST',
          credentials: 'include',
        });

        if (response.ok) {
          console.log('Logout successful');
          this.$store.commit('setLoggedIn', false);
          window.location.href = '/api/login/';
        } else {
          // Handle failed logout
          if (response.headers.get('content-type')?.includes('application/json')) {
            const errorData = await response.json();
            console.error('Logout failed:', errorData.error);
          } else {
            console.error('Logout failed. Non-JSON response received.');
          }
        }
      } catch (error) {
        console.error('An unexpected error occured during logout:', error);
      }
    },
  },
};
</script>

<style>
.navbar {
  background-color: #5D737E;
  color: #f9e3cf;
  padding: 10px;
  text-align: center;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
}

.nav-group {
  display: flex;
  align-items: center
}

.logo {
  width: 30px;
  height: auto;
  margin-left: 20px;
}

.title {
  font-size: 24px;
  margin-left: 10px;
}

.nav-links {
  list-style-type: none;
  margin: 0;
  display: flex;
  font-weight: bold;
  gap: 20px;
  margin-right: 20px;
}

.nav-links li {
  margin-left: 20px;
}

.nav-link {
  color: #54708C;
  text-decoration: none;
  font-size: 16px; 
  cursor: pointer;
}

.nav-link:hover {
  text-decoration: underline;
}

@media screen and (max-width: 767px) {
    
    .navbar {
        flex-direction: column;
    }
  .nav-links {
    justify-content: center;
    align-items: center;
    gap: 30px;
  }

  .nav-links li {
    margin: 10px 0;
  }
}
</style>