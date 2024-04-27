<template>
    <!-- Login modal -->
    <div class="modal fade" ref="loginModal" id="LoginModal" tabindex="-1" role="dialog" aria-labelledby="LoginModalLabel" aria-hidden="true">
        <div class="modal-dialog" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="LoginModalLabel">Login</h5>
                    <button type="button" class="close" data-bs-dismiss="modal" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div class="modal-body">
                    <!-- Login form -->
                    <form @submit.prevent="submitLoginForm()">
                        <!-- Username field -->
                        <div class="form-group">
                            <label class="mt-3" for="username">Username:</label>
                            <input class="form-control" v-model="formData.username" :class=" { 'is-invalid': error }" type="text" id="username" name="username" placeholder="Enter Username" required>
                        </div>

                        <!-- Password field -->
                        <div class="form-group">
                            <label class="mt-3"  for="password">Password:</label>
                            <input class="form-control" v-model="formData.password" :class=" { 'is-invalid': error }" type="password" id="password" name="password" placeholder="Enter Password" required>
                        </div>
                        
                        <!-- Display error messages -->
                        <div v-if="error" class="text-danger mb-3">{{ error }}</div>

                        <button type="submit" data-bs-dismiss="modal" class="btn btn-primary mt-3">Login</button>
                    </form>

                    <!-- Signup link -->
                    <p>Don't have an account? <button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#SignupModal">Signup here</button></p>
                </div>
            </div>
        </div>
    </div>

    <!-- Signup modal -->
    <div class="modal fade" ref="signupModal" id="SignupModal" tabindex="-1" role="dialog" aria-labelledby="SignupModalLabel" aria-hidden="true">
        <div class="modal-dialog" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="SignupModalLabel">Signup</h5>
                    <button type="button" class="close" data-bs-dismiss="modal" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div class="modal-body">
                    <!-- Signup form -->
                    <form @submit.prevent="submitSignupForm()">
                        <!-- Username field -->
                        <div class="form-group">
                            <label class="mt-3" for="username">Username:</label>
                            <input class="form-control" v-model="formData.username" :class=" { 'is-invalid': error }" type="text" id="username" name="username" placeholder="Enter Username" required>
                        </div>

                        <!-- Email field -->
                        <div class="form-group">
                            <label class="mt-3" for="email">Email:</label>
                            <input class="form-control" v-model="formData.email" :class=" { 'is-invalid': error }" type="email" id="email" name="email" placeholder="Enter Email" required>
                        </div>

                        <!-- Password field -->
                        <div class="form-group">
                            <label class="mt-3" for="password">Password:</label>
                            <input class="form-control" v-model="formData.password" :class=" { 'is-invalid': error }" type="password" id="password" name="password" placeholder="Enter Password" required>
                        </div>

                        <!-- Display error messages -->
                        <div v-if="error" class="text-danger mb-3">{{ error }}</div>

                        <button type="submit" data-bs-dismiss="modal" class="btn btn-primary mt-3">Signup</button>
                    </form>
                    <!-- Login link -->
                    <p>Already have an account? <button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#LoginModal">Login here</button></p>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { mapMutations } from 'vuex';

export default {
    props: {
        formData: Object,
    },
    data() {
        return {
            // Tracks login status
            loggedIn: false,
            // Stores error messages
            error: null,
        }
    },
    methods: {
        ...mapMutations(['setUserDetails']),

        // Handles form submission when logging in
        async submitLoginForm() {
            try {
            const response = await fetch('http://localhost:8000/globalVoice/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                },
            body: JSON.stringify(this.formData),
            });
            const responseData = await response.json();

            // Check for error or success message
            if (responseData.error) {
                console.error("Error in logging in:", responseData.error)
                this.error = responseData.error;
            } else if (responseData.message) {
                console.log(responseData.message);
                this.loggedIn = true;
                // Set user details
                this.setUserDetails(responseData.user_details);
                this.error = null;
            } else {
                this.errors = responseData;
            }
            // Clears form data
            this.$emit('clear-form');
        } catch (error) {
            console.error(error);
        }
        },

        // Handles form submission when signing up
        async submitSignupForm() {
            try {
                const response = await fetch('http://localhost:8000/globalVoice/signup/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.formData),
            });
            const responseData = await response.json();

            // Checks for error or success message
            if (responseData.error) {
                console.error("Error in signing up:", responseData.error)
                this.error = responseData.error;
            } else if (responseData.message) {
                // Close signup modal
                this.handleModalClosed(); 
                console.log(responseData.message);
                this.loggedIn = true;
                // Set user details
                this.setUserDetails(responseData.user_details);
                this.error = null;
            } else {
                this.errors = responseData;
            }
            // Clears form data
            this.$emit('clear-form');
            } catch (error) {
            console.error(error);
            }
        },

        // Closes modal
        handleModalClosed() {
            // Remove modal backdrop
            this.$refs.signupModal.remove('show');
            document.body.classList.remove('modal-open');
            document.body.querySelector('.modal-backdrop').remove();
        },
    },
};
</script>