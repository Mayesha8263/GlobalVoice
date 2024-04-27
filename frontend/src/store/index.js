import { createStore } from 'vuex';

export default createStore({
    // Initial state of store
    state: {
        loggedIn: false,
        userDetails: {},
        userId: null,
    },
    mutations: {
        // Update loggedIn state
        setLoggedIn(state, value) {
            state.loggedIn = value;
        },
        // Update userDetails state
        setUserDetails(state, userDetails) {
            state.userDetails = userDetails;
        },
        // Update userId state
        setUserId(state, userId) {
            state.userId = userId
        },
    },
    actions: {
        // Handle logout
        async logout(context) {
            try {
                const response = await fetch('http://localhost:8000/globalVoice/logout/', {
                    method: 'POST',
                });
                if (response.ok) {
                    console.log('Logout successful');
                    // Set loggedIn to false
                    context.commit('setLoggedIn', false);
                    // Clear user details
                    context.commit('setUserDetails', null);  
                    window.location.href = '/api/login/';
                } else {
                    console.error('Failed to logout user');
                }
            } catch (error) {
                console.error('An unexpected error occurred during logout:', error);
            }
        },

        // Fetch user details from server
        async fetchUserDetails(context) {
            try {
                const response = await fetch('http://localhost:8000/globalVoice/getUser/', {
                    credentials: 'include',
                });
                const userData = await response.json();

                if (response.ok) {
                    // Update userDetails state
                    context.commit('setUserDetails', userData);
                } else {
                    console.error('Failed to fetch user details');
                }
            } catch (error) {
                console.error(error)
            }
        },

        // Handle user login
        async loginUser(context, userData) {
            try {
                const response = await fetch('http://localhost:8000/globalVoice/login/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(userData),
                });
                const responseData = await response.json();

                if (response.ok) {
                    // Update userDetails, loggedIn and userId states
                    context.commit('setUserDetails', responseData.user_details);
                    context.commit('setLoggedIn', true);
                    context.commit('setUserId', responseData.user_details.id);

                    console.log('State after login:', context.state);
                    
                } else {
                    console.error('Failed to log in:', responseData.error);
                }
            } catch (error) {
                console.error(error);
            }
        },
    },
});