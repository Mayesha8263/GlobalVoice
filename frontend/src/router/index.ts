import { createRouter, createWebHistory } from 'vue-router'

import Phrasebook from '../pages/Phrasebook.vue'
import Translator from '../pages/Translator.vue'
import Profile from '../pages/Profile.vue'

// Base URL based on environment
let base = (import.meta.env.MODE == 'development') ? import.meta.env.BASE_URL : '';

const router = createRouter({
    // Setup history mode
    history: createWebHistory(base),
    // Route to different pages
    routes: [
        { path: '/translator/', name: 'Translator', component: Translator},
        { path: '/phrasebook/', name: 'My Phrasebook', component: Phrasebook },
        { path: '/profile/', name: 'Profile', component: Profile },
    ],
})

export default router
