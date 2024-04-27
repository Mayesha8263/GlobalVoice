<template>
    <body>
        <!-- Profile page container -->
        <div class="profile-page">
            <!-- User information section -->
            <div class="user-info">
                <!-- Display username -->
                <div class="h2">{{ username }}</div>
                <div class="other-info">
                    <!-- Display email -->
                    <div class="email">
                        <Label class="label">Email: </Label>
                        <p>{{ email }}</p>
                    </div>
                    <!-- Display favourite languages -->
                    <div class="favLangs">
                        <Label class="label">Favourite Languages:</Label>
                        <ul>
                            <!-- Display each favourite language -->
                            <li v-for="language in favouriteLanguages" :key="language">
                                <span class="language-item">
                                    {{ language }}
                                    <!-- Button to remove the language -->
                                    <button @click="removeLanguage(language)" class="remove-button">
                                        Remove
                                    </button>
                                </span>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <!-- Edit profile form -->
            <div class="edit-form">
                <form @submit.prevent="updateProfile">
                    <div class="h2">Edit Profile</div>
                    <div class="profile-form">
                        <!-- Input field for username -->
                        <label for="username">Username:</label>
                        <!-- Existing username as placeholder -->
                        <input class="profile-input" v-model="username" type="text" placeholder="Username" required />
                        <!-- Input field for email -->
                        <label for="email">Email:</label>
                        <!-- Existing email as placeholder -->
                        <input class="profile-input" v-model="email" type="email" placeholder="Email" required />
                        <!-- Dropdown to select favourite languages -->
                        <label>Pick your favourite languages:</label>
                        <select v-model="selectedLanguage" @change="updateSelectedLanguages" multiple>
                            <option v-for="[langCode, langName] in languageCodes" :value="langName">
                                {{ langName }}
                            </option>
                        </select>
                        <!-- Button to update profile -->
                        <button class="default-button" type="submit" id="updateProfileBtn">Update Profile</button>
                    </div>
                </form>
            </div>
        </div>
    </body>
</template>

<script>
import { useRoute } from 'vue-router';
import { ref, onMounted } from 'vue';

export default {
    data() {
        return {
            username: null,
            email: null,
            selectedLanguage: [],
            favouriteLanguages: [],
            favLangCodes: [],
            languageCodes: [],
        };
    },
    mounted() {
        // Fetch language codes and user details when component mounts
        this.fetchLanguageCodes();
        this.getDetails();
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

        // Update the selected languages by user
        updateSelectedLanguages() {
            // Concatenates existing favourite languages array with selected language array
            this.favouriteLanguages = [...this.favouriteLanguages, ...this.selectedLanguage];
            // Removes duplicate entries 
            this.favouriteLanguages = [...new Set(this.favouriteLanguages)];
            this.selectedLanguages = [];
        },

        // Get user details from server
        async getDetails() {
            try {
                const response = await fetch(`http://localhost:8000/globalVoice/getUser/?user_id=${this.$store.state.userDetails.id}`);
                const userData = await response.json();

                if (response.ok) {
                    // Update username, email and favourite languages with new data
                    this.email = userData['User Details'].email;
                    this.username = userData['User Details'].username;
                    this.favouriteLanguages = userData['User Details'].favourite_languages.map(language => language.name);
                }
            } catch (error) {
                console.error('Failed to fetch user details.')
            }
        },

        // Maps language codes to language name
        async mapLanguageCodes() {
            this.favLangCodes = this.favouriteLanguages.map(languageName => {
                const matchingLanguage = this.languageCodes.find(([code, name]) => name === languageName);
                return matchingLanguage ? {name: matchingLanguage[1], code: matchingLanguage[0]} : {};
            });
        },
        
        // Updates user profile
        async updateProfile() {
            this.mapLanguageCodes();
            try {
                const response = await fetch(`http://localhost:8000/globalVoice/updateProfile/?user_id=${this.$store.state.userDetails.id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        username: this.username,
                        email: this.email,
                        favLangCodes: this.favLangCodes,
                    }),
                });

                if (response.ok) {
                    // Show successful update to user
                    this.addSuccessHighlight();
                } else {
                    console.error('Failed to update profile');
                }
            } catch (error) {
                console.error('Error updating profile:', error);
            }
        },

        // Highlight update profile button to show successful update
        addSuccessHighlight() {
            const updateProfileBtn = document.getElementById('updateProfileBtn');
            updateProfileBtn.classList.add('success-highlight');
            // Remove highlight when timeout
            setTimeout(() => {
                updateProfileBtn.classList.remove('success-highlight');
            }, 1000);
        },

        // Remove language from favourite language array
        removeLanguage(language) {
            const index = this.favouriteLanguages.indexOf(language);
            if (index !== -1) {
                this.favouriteLanguages.splice(index, 1);
            }
        },
    },
}
</script>

<style scoped>
.profile-page {
    display: flex;
    gap: 20px;
    margin: 20px;
    color: #5D737E;
}

.profile-form {
    display: flex;
    flex-direction: column;
    align-items: center; 
    justify-content: center;
}

.user-info,
.edit-form {
    flex: 1;
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 8px;
    color: #5D737E;
    border-color: #5D737E;
}

.user-info {
    display: flex;
    flex-direction: column;
    font-size: 20px;
    align-items: center;
    justify-content: center;
    background-color: #5D737E;
    color: #f9e3cf;
}

.other-info {
    padding-top: 30px;
}

.email {
    display: flex;
}

input,
select {
    border-color: #5D737E;
    width:100%;
    margin-bottom: 20px;
}

.profile-input {
    border-radius: 10px;
    padding: 10px;
    border: 2px solid #5D737E;
}

.default-button {
    width: 50%;
}

.h2 {
    text-align: center;
}

.label{ 
    font-weight: bold;
    margin-right: 10px;
}

.email,
.favLangs{
    margin-bottom: 15px;
}

ul {
    list-style-type: none;
    padding-left: 0;
}

.email-text {
    padding-left: 30px;
}

.language-item {
    align-items: center;
    justify-content: space-between;
}

.remove-button {
    background: none;
    border: none;
    color: red;
    cursor: pointer;
    opacity: 0;
    transition: opacity 0.2s ease-in-out;
}

.language-item:hover .remove-button{
    opacity: 1;
}

.success-highlight {
    background-color: rgb(132, 163, 132);
    color: white;
}

@media screen and (max-width: 768px) {
    .profile-page {
        flex-direction: column;
    }

    .user-info,
    .edit-form {
        width: 100%;
    }
}
</style>