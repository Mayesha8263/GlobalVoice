<template>
    <body class="translate-container">
        <!-- Form for input and translation -->
        <form @submit.prevent="submitForm()">
            <div class="form-container">
                <!-- All input fields -->
                <div class="input-field">
                    <!-- Input buttons at the top -->
                    <div class="input-controls">
                        <div class="icon-container">
                            <!-- Button for speech recognition -->
                            <button @click="toggleSpeechRecognition" class="microphone-button">
                                <FontAwesomeIcon icon="microphone" size="2x" class="colored-icon" />
                            </button>
                        </div>
                        
                        <!-- Display listening message -->
                        <div v-if="isListening || recognisedText">
                            <p v-if="isListening">
                                (Default language is English)<br>
                                Listening...
                            </p>
                        </div>
                        
                        <!-- Select input language from dropdown -->
                        <select v-model="inputLanguage" @change="updateInputLanguageName" id="input_language" name="input_language">
                            <option value="" disabled selected>Pick an input language</option>
                            <option v-for="[langCode, langName] in languageCodes" :value="langCode">{{ langName }}</option>
                        </select>
                        <!-- Button to save input translation -->
                        <button class="default-button input-save-button" @click="saveInputTranslation" v-if="loggedIn || loggedInUser">Save +</button>
                    </div>
                    <!-- Input text area -->
                    <textarea class="input-text" v-model="inputText" type="text" id="input" name="input" placeholder="Enter Text" required />
                </div>

                <div class="divider"></div>

                <!-- Adding multiple translation boxes -->
                <div class="add-button-container">
                    <button class="default-button add-button"@click="addTargetLanguage" v-if="targetLanguages.length < 3">Add Language</button>
                </div>

                <!-- All output fields -->
                <div class="output-field">
                    <!-- Display loading spinner -->
                    <div v-if="isLoadingSpinner" id="loading-spinner" class="spinner"></div>

                    <!-- Loop through all target languages for each translation box -->
                    <div v-for="(target, index) in targetLanguages" :key="index" :class="{ 'output-field-container': shouldShowBorder(index) }">
                        <div class="button-group">
                            <!-- Select output language -->
                            <select class="output-dropdown" v-model="target.language" @change="updateOutputLanguageName(index)" id="target_language" :name="'target_language_' + index" required>
                                <option value="" disabled selected>Pick a target language</option>
                                <option v-for="[langCode, langName] in languageCodes" :value="langCode">{{ langName }}</option>
                            </select>

                            <!-- Button to start translation -->
                            <button class="default-button translate-button" @click="translate(index)" type="submit">Translate</button>
                            <!-- Button to remove translation box -->
                            <button class="remove-button-translate" @click="removeTargetLanguage(index)" v-if="index > 0">X</button>
                        </div>

                        <!-- Display translated text -->
                        <p class="translated-text">{{ target.translatedText }}</p>

                        <div class="output-bottom-container">
                            <div class="icon-container">
                                <!-- Button for text to speech feature -->
                                <button class="speak-button" v-if="shouldShowSpeakButton(target.targetLanguageName)" @click="speakTranslatedText(target.translatedText, target.targetLanguageName)">
                                    <font-awesome-icon icon="volume-high" size="2x" class="colored-icon" />
                                </button>
                            </div>

                            <!-- Button to save output translationss -->
                            <button class="default-button output-save-button" @click="saveOutputTranslation(index)" v-if="loggedIn || loggedInUser">Save +</button>
                        </div>
                    </div>
                </div>
            </div>
        </form>
    </body>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useSpeechRecognition } from '@vueuse/core';
import { library } from '@fortawesome/fontawesome-svg-core';
import { faMicrophone } from '@fortawesome/free-solid-svg-icons';
import { faVolumeHigh } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

library.add(faMicrophone, faVolumeHigh);
export default {
    data() {
        return {
            // Input language code
            inputLanguage: '',
            inputLanguageName: '',
            inputText: '',
            // Target language code
            targetLanguage: '',
            targetLanguages: [
                { language: '', targetLanguageName: '', translatedText: '' },
            ],
            favouriteLanguages: [],
            // Flag for speech recognition
            isListening: false,
            // Transcribed text 
            recognisedText: '',
            // Speech recogntion instance
            recognition: null,
            audioChunks: [], 
            mediaRecorder: null, 
            // Flag for loading spinner
            isLoadingSpinner: false,
            // Array of all supported voices
            supportedVoices: [],
            voiceName: null,
            // Index of translation box
            index: null,
        };
    },
    components: {
        FontAwesomeIcon
    },
    computed: {
        // Check if user is logged in
        loggedIn() {
            return this.$store.state.loggedIn;
        },
        // Get logged in user details
        loggedInUser() {
            return this.$store.state.loggedInUser;
        },
    },
    props: {
        // Array of all language codes supported
        languageCodes: Array,
    },
    mounted() {
        // Load user details and voices when component mounts
        this.loadUserDetails();
        this.loadVoices();
    },
    methods: {
        // Load user details
        async loadUserDetails() {
            await this.getDetails();
        },

        // Get user details
        async getDetails() {
            try {
                const response = await fetch(`http://localhost:8000/globalVoice/getUser/?user_id=${this.$store.state.userDetails.id}`);
                const userData = await response.json();

                if (response.ok) {
                    this.email = userData['User Details'].email;
                    this.username = userData['User Details'].username;
                    this.favouriteLanguages = userData['User Details'].favourite_languages.map(language => language.name);
                }
            } catch (error) {
                console.error('Failed to fetch user details.')
            }
        },

        // Set target language and index of each translation box
        translate(index) {
            this.targetLanguage = this.targetLanguages[index];
            this.index = index;
        },

        // Submit translation form
        async submitForm() {
            try {
                // Detect language if input language is empty or is another detected language
                const containsDetected = this.languageCodes.some(([_, label]) => label.includes(`Detected - ${this.inputLanguage}`));
                if (this.inputLanguage == '' || containsDetected) {
                    const detectedLanguage = await this.detectLanguage();
                }
                // Show loading spinner
                this.showLoadingSpinner();
                const targetLanguage = this.targetLanguage;
                
                // Fetch translated text
                const response = await fetch('http://localhost:8000/globalVoice/translate/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams({
                        'input_language': this.inputLanguage,
                        'input': this.inputText,
                        'target_language': targetLanguage.language,
                    }),
                });

                if (response.ok) {
                    const data = await response.json();
                    targetLanguage.translatedText = data.translated_text;

                    // Save output translation is target language is a favourite language
                    if (this.favouriteLanguages.some(lang => lang === targetLanguage.targetLanguageName)) {
                        await this.saveOutputTranslation(this.index);
                    }
                } else {
                    console.error('Failed to submit form');
                }
            } catch (error) {
                console.error(error)
            } finally {
                // Hide loading spinner
                this.hideLoadingSpinner();
            }
        },

        // Detect language
        async detectLanguage() {
            try {
                const response = await fetch('http://localhost:8000/globalVoice/detectLanguage/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        input_text: this.inputText,
                    }),
                });
                const data = await response.json();
                const detectedLanguage = data.detected_language;

                // Push detected langauge in array of language codes
                this.languageCodes.push([detectedLanguage, `Detected - ${detectedLanguage}`]);
                this.inputLanguage = detectedLanguage;
                

                return detectedLanguage;
            } catch (error) {
                console.error('Error detecting language:', error);
            }
        },

        // Add target language to multiple translation boxes
        addTargetLanguage() {
            // Maximum translation box is 3
            if (this.targetLanguages.length < 3) {
                this.targetLanguages.push({language: '', targetLanguageName: '' });
            } else {
                console.warn('Maximum limit of 3 target languages reached.');
            }
        },

        // Check if border should be shown for translation box
        shouldShowBorder(index) {
            return this.targetLanguages.length > 1;
        },

        // Remove translation box
        removeTargetLanguage(index) {
            this.targetLanguages.splice(index, 1);
        },

        // Update input language name in form
        updateInputLanguageName() {
            const inputLanguage = this.languageCodes.find(([code]) => code === this.inputLanguage);
            this.inputLanguageName = inputLanguage ? inputLanguage[1] : '';
        },

        // Update output language name in form 
        updateOutputLanguageName(index) {
            const outputLanguage = this.languageCodes.find(([code]) => code === this.targetLanguages[index].language);
            this.targetLanguages[index].targetLanguageName = outputLanguage ? outputLanguage[1] : '';
        },

        // Save input phrases
        async saveInputTranslation() {
            try {
                // Get logged in user details
                const userId = this.$store.state.userDetails.id;

                const response = await fetch('http://localhost:8000/globalVoice/saveInputTranslation/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams({
                        'user_id': userId,
                        'input_language_code': this.inputLanguage,
                        'input_language_name': this.inputLanguageName,
                        'input': this.inputText,
                    }),
                });

                if (response.ok) {
                    console.log('Input text and input language saved successfully.', this.inputLanguage, this.inputText, userId);
                } else {
                    console.error('Failed to save input translation')
                }
            } catch {
                console.error(error);
            }
        },

        // Save output phrases
        async saveOutputTranslation(index) {
            try {
                // Get logged in user details
                const userId = this.$store.state.userDetails.id;

                const targetLanguage = this.targetLanguages[index];
                const response = await fetch('http://localhost:8000/globalVoice/saveOutputTranslation/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams({
                        'user_id': userId,
                        'output_language_code': targetLanguage.language,
                        'output_language_name': targetLanguage.targetLanguageName,
                        'output': targetLanguage.translatedText,
                    }),
                });

                if (response.ok) {
                    console.log('Output text and target language saved successfully:', targetLanguage.translatedText, targetLanguage.targetLanguageName, userId);
                } else {
                    console.error('Failed to save input translation');
                }
            } catch {
                console.error(error);
            }
        },

        // Toggle if speech recognition is happening
        toggleSpeechRecognition() {
            if (!this.isListening) {
                this.startSpeechRecognition();
            } else {
                this.stopSpeechRecognition();
            }
        },

        // Start speech recognition
        async startSpeechRecognition() {
            this.isListening = true;
            // Get user media stream for audio input
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
            const audioChunks = [];

            this.mediaRecorder.ondataavailable = (event) => {
                // Set flag to show speech recognition is not active
                this.isListening = false;
                audioChunks.push(event.data);
            };

            // Event handler for when media recorder stops recording
            this.mediaRecorder.onstop = async () => {
                // Convert audio data chunks into a Blob
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });

                // Create form data object and append audio Blob
                const formData = new FormData();
                formData.append('audio', audioBlob);
        
                try {
                    this.showLoadingSpinner();
                    const response = await fetch('http://localhost:8000/globalVoice/transcribe/', {
                        method: 'POST',
                        body: formData,
                    });

                    if (response.ok) {
                        // Parse transcription response
                        const data = await response.json();
                        console.log('Transcribed text:', data.transcribedText);
                        this.inputText = data.transcribedText;
                        // Detect language of transcribed text
                        this.detectLanguage();
                    } else {
                        console.error('Failed to transcribe audio');
                    }
                } catch (error) {
                    console.error('Error transcribing audio:', error);
                }
                finally {
                    this.hideLoadingSpinner();
                }
            };

            // Start recording audio
            this.mediaRecorder.start();
            // Stop recording after 10 seconds
            setTimeout(() => this.mediaRecorder.stop(), 10000);
        },

        // Stop speech recognition by the user
        stopSpeechRecognition() {
            if (this.isListening) {
                // Stop media recorder 
                this.mediaRecorder.stop();
                this.isListening = false;
                this.showLoadingSpinner();
            }
        },

        // Load voices from API
        loadVoices() {
            this.supportedVoices = responsiveVoice.getVoices();
        },

        // Toggle speech button for target language
        shouldShowSpeakButton(language) {
            // Check if there are supported voices of target language
            if (!this.supportedVoices || this.supportedVoices.length === 0) {
                return false;
            }

            // Split language into keywords
            const keywords = language.toLowerCase().split(' ');
            // Find matching voice for language keywords
            const voice = this.supportedVoices.find(voice => {
                const voiceName = voice.name.toLowerCase();
                this.voiceName = voice.name;
                return keywords.some(keyword => voiceName.includes(keyword))
            });
            // Return true is a matching voice is found
            return !!voice;
        },

        // Speak translated text
        async speakTranslatedText(text, language) {
            try {
                // Check if API is available
                if (typeof responsiveVoice !== 'undefined') {
                    // Speak text using selected voice
                    responsiveVoice.speak(text, this.voiceName);
                } else {
                    console.error('ResponsiveVoice.js is not loaded or initialized.');
                }
            } catch (error) {
                console.error('Unable to synthesize text:', error);
            }
        },

        // Show loading spinner
        showLoadingSpinner() {
            this.isLoadingSpinner = true;
            // Display loading spinner element
            const loadingSpinner = document.getElementById('loading-spinner');
            if (loadingSpinner) {
                loadingSpinner.style.display = 'block';
            } else {
                console.error("Element with ID 'loading-spinner' not found.");
            }
        },

        // Hide loading spinner
        hideLoadingSpinner() {
            this.isLoadingSpinner = false;
            // Hide loading spinner element
            const loadingSpinner = document.getElementById('loading-spinner');
            if (loadingSpinner) {
                loadingSpinner.style.display = 'none';
            } else {
                console.error("Element with ID 'loading-spinner' not found.");
            }
        },
    },
};
</script>

<style>
.translate-container {
    max-width: 1300px;
    margin: 0 auto;
}

.form-container {
    display: flex;
    flex-direction: column;
}

.icon-container {
    background-color: white;
    margin-right: 10px;
}

.colored-icon {
    color: #5D737E;
}

.microphone-button {
    padding: 10px;
    border: none;
    border-radius: 4px;
    background-color: transparent;
    cursor: pointer;
    margin-top: 30px;
    margin-bottom: 10px;
    border-radius: 20px;
}

.input-controls {
    display: flex;
    align-items: baseline;
    justify-content: flex-start;
}

select {
    padding: 10px;
    border: 2px solid #5D737E;
    border-radius: 10px;
}

.input-text {
    margin-left: 20px;
    margin-top: 20px;
    border: none;
    width: 98%;
    height: 40px;
    padding: 10px;
    font-size: 20px;
    box-sizing: border-box;
    outline: none;
    resize: none;
}

.default-button {
    padding: 10px;
    border: none;
    border-radius: 4px;
    background-color: #5D737E;
    color: #f9e3cf;
    font-weight: bolder;
    cursor: pointer;
    margin-top: 30px;
    margin-bottom: 10px;
    border-radius: 20px;
}

.input-save-button,
.output-save-button {
    font-size: 16px;
    margin: 10px;
    border-radius: 10px;
    font-weight: lighter;
}

button:hover {
    background-color: #a4c5e7;
}

.divider {
    border-top: 3px solid #5D737E;
    margin-top: 30px;
    width: 100%;
}

.translated-text {
    text-align: center;
    color: #555;
    display: flex;
    align-items: center;
    font-size: 20px;
    padding: 5px;
    padding-bottom: 40px;
}

.button-group {
    display: flex;
    justify-content: flex-start;
    padding-bottom: 20px;
}

.output-dropdown {
    padding: 10px;
}

.translate-button {
    font-size: 16px;
    margin: 10px;
    border-radius: 10px;
    font-weight: lighter;
}

.remove-button-translate {
    background: none;
    border: none;
    color: black;
    cursor: pointer;
    font-size: 15px;
    margin-left: auto;
    font-weight: bold;
    border-radius: 20px;    
}

.remove-button:hover {
    background-color: lightgray;
} 

.output-field {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-start;
    gap: 20px;
    margin: 0;
    margin-left: 15px;
    margin-top: 20px;
} 

.output-field-container {
    position: relative;
    border: 2px solid #5D737E;
    border-radius: 10px;
    padding: 20px;
    padding-bottom: 5px;
    padding-right: 10px;
    margin-bottom: 20px;
    flex: 0 0 calc(33.33% - 20px);
    max-width: calc(33.33% - 20px);
}

@media only screen and (max-width: 1200px) {
    .output-field-container {
        flex: 0 0 100%;
        max-width: 100%;
    }
}

.output-bottom-container {
    bottom: 0;
    left: 0;
    width: 100%;
    padding-top: 150px;
}

.output-save-button {
    position: absolute;
    bottom: 0;
    right: 0;
}

.speak-button {
    position: absolute;
    bottom: 0;
    left: 0;
    border: none;
    background-color: transparent;
    cursor: pointer;
    margin-left: 5px;
    border-radius: 20px;
    padding: 10px;
}

.add-button {
    font-weight: lighter;
    font-size: 15px;
    margin-left: 20px;
    border-radius: 10px;;
}

.spinner {
    border: 4px solid rgba(0, 0, 0, 0.1);
    border-left-color: #007bff;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    position: fixed;
    top: 50%;
    left: 50%;
    margin-top: -20px;
    margin-left: -20px;
    z-index: 9999;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
</style>