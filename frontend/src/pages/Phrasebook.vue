<template>
    <body>
        <div class="main-container">
            <!-- Saved inputs section -->
            <div class="saved-inputs">
                <p class="saved-title">Saved Inputs</p>
                <!-- Display saved inputs -->
                <ul v-if="Object.keys(savedInputs).length > 0">
                    <li v-for="(inputs, language) in savedInputs" :key="language">
                        <p class="saved">{{ language }}</p>
                        <ul>
                            <!-- Display each input for the language -->
                            <li v-for="input in inputs" :key="input.id" class="language-item">
                                {{ input.input_sentence }}
                                <!-- Remove button for the input phrase -->
                                <button @click="remove(input, 'input')" class="remove-button">
                                    Remove
                                </button>
                            </li>
                        </ul>
                    </li>
                </ul>
                <!-- Message when there are no saved inputs -->
                <p v-else class="no-data-message">Start your translations to save sentences!</p>
            </div>

            <!-- Saved outputs section -->
            <div class="saved-outputs">
                <p class="saved-title">Saved Outputs</p>
                <!-- Display saved outputs -->
                <ul v-if="Object.keys(savedOutputs).length > 0">
                    <li v-for="(outputs, language) in savedOutputs" :key="language">
                        <p class="saved">{{ language }}</p>
                        <ul>
                            <!-- Display each output for the language -->
                            <li v-for="output in outputs" :key="output.id" class="language-item">
                                {{ output.output_sentence }}
                                <!-- Remove button for the output phrase -->
                                <button @click="remove(output, 'output')" class="remove-button">
                                    Remove
                                </button>
                            </li>
                        </ul>
                    </li>
                </ul>
                <!-- Message when there are no saved outputs -->
                <p v-else class="no-data-message">Start your translations to save sentences!</p>
            </div>
        </div>
    </body>
</template>

<script lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { useStore } from 'vuex';


export default {
    setup() {
        const route = useRoute();
        const store = useStore();
        const savedInputs = ref([]);
        const savedOutputs = ref([]);

        // Compute user id from store
        const userId = computed(() => store.state.userDetails?.id);

        // Fetch saved inputs from server
        const fetchSavedInputs = async () => {
            try {
                console.log("user id:", userId);
                const response = await fetch(`http://localhost:8000/globalVoice/getSavedInputs/?user_id=${userId.value}`);
                const data = await response.json();

                const inputsByLanguage = {};
                // Organise inputs by language
                data.savedInputs.forEach(input => {
                    const languageName = input.language.name;
                    if (!inputsByLanguage[languageName]) {
                        inputsByLanguage[languageName] = [];
                    }
                    inputsByLanguage[languageName].push(input);
                });

                savedInputs.value = inputsByLanguage;
            } catch (error) {
                console.error('Error fetching saved inputs:', error);
            }
        };

        // Fetch saved outputs from server
        const fetchSavedOutputs = async () => {
            try {
                const response = await fetch(`http://localhost:8000/globalVoice/getSavedOutputs/?user_id=${userId.value}`);
                const data = await response.json();

                const outputsByLanguage = {};
                // Organise outputs by language
                data.savedOutputs.forEach(output => {
                    const languageName = output.language.name;
                    if (!outputsByLanguage[languageName]) {
                        outputsByLanguage[languageName] = [];
                    }
                    outputsByLanguage[languageName].push(output);
                });

                savedOutputs.value = outputsByLanguage;
            } catch (error) {
                console.error('Error fetching saved outputs: ', error);
            }
        };

        // Removes saved item from list
        const remove = async (item, type) => {
            try {
                // Delete specific saved item from server
                const response = await fetch(`http://localhost:8000/globalVoice/removeSavedItem/?user_id=${userId.value}&type=${type}&item_id=${item.id}`, {
                    method: 'DELETE',
                });

                if (response.ok) {
                    console.log(`Successfully removed ${type}:`, item);
                    // Update savedInputs or savedOutputs after item removal
                    if (type === 'input') {
                        for (const language in savedInputs.value) {
                            savedInputs.value[language] = savedInputs.value[language].filter(input => input.id !== item.id || input.input_sentence !== item.input_sentence);
                        }
                    } else if (type === 'output') {
                        for (const language in savedOutputs.value) {
                            savedOutputs.value[language] = savedOutputs.value[language].filter(output => output.id !== item.id || output.output_sentence !== item.output_sentence);
                        }
                    }
                } else {
                    console.error(`Failed to remove ${type}`);
                }
            } catch (error) {
                console.error('Error removing saved item:', error);
            }
        };
        
        // Fetch all saved inputs and outputs on component mount
        onMounted(() => {
            fetchSavedInputs();
            fetchSavedOutputs();
        });

        return {
            savedInputs,
            savedOutputs,
            remove,
        };
    },
};
</script>

<style>
.main-container {
    display: flex;
    gap: 20px;
    margin: 20px;
    color: #5D737E;
    padding: 20px;
}

.saved-title {
    text-align: center;
    padding-bottom: 15px;
}

.saved-title,
.saved {
    font-weight: bold;
    margin-top: 20px;
    margin-bottom: 0;
}

.saved-inputs,
.saved-outputs {
    flex: 1;
    padding: 20px;
    border: 1px solid #5D737E;
    border-radius: 8px;
}

.language-item {
    align-items: center;
    justify-content: space-between;
    padding: 5px;
}

ul {
    list-style-type: none;
}

.remove-button {
    background: none;
    border: none;
    color: red;
    cursor: pointer;
    opacity: 0;
    transition: opacity 0.2s ease-in-out;
    border-radius: 10px;
}

.language-item:hover .remove-button{
    opacity: 1;
}
</style>