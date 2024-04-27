from io import BytesIO
from django.shortcuts import render
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate
from django.contrib import auth
from django.views.decorators.http import require_POST
from django.db import transaction
import json
import torch
from transformers import AutoProcessor, AutoModelForCTC, Wav2Vec2Processor, Wav2Vec2ForCTC
from pydub import AudioSegment
import soundfile as sf
import matplotlib.pyplot as plt
import wave
from scipy.io import wavfile
import librosa
import numpy as np

from .models import CustomUser, Language, InputTranslation, OutputTranslation
from .forms import SignupForm, LoginForm
from .nllb_model import nllb_translator

def main_spa(request: HttpRequest) -> HttpResponse:
    return render(request, 'globalVoice/spa/index.html', {})

# Signing in new users
@csrf_exempt
def signup_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        data = json.loads(request.body)
        # Initialise signup for with received data
        form = SignupForm(data)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']

            # Check if email already exists in database
            if CustomUser.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email already exists'})
            
            # Create new user instance
            new_user = CustomUser(username=username, email=email)
            new_user.set_password(password)
            new_user.save()

            # Authenticate the new user
            user_auth = authenticate(username=username, password=password)
            if user_auth:
                login(request, user_auth)
                # Store username in session
                request.session['username'] = username     

                user_details = {
                    'id': user_auth.id,
                    'username': user_auth.username,
                }

                # Return success response with user details
                return JsonResponse({'message': 'Successfully signed in', 'user_details': user_details})
            else:
                print("Authentication Failed") 
                return JsonResponse({'error': 'Authentication Failed'})
        else:
            print("Form is invalid")
            return JsonResponse({'error': 'Form is invalid'})
    else:
        print("Signup Failed")
        return JsonResponse({'error': 'Signup Failed'})

# Logging in users
@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        # Initialise login form with received data
        form = LoginForm(data)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Authenticate user details
            user_auth = authenticate(username=username, password=password)
            if user_auth is not None:
                login(request, user_auth)
                # Store username in session
                request.session['username'] = username

                user_details = {
                    'id': user_auth.id,
                    'username': user_auth.username,
                }
                # Return success response with user details
                return JsonResponse({'message': 'Logged in successfully', 'user_details': user_details})
            else:
                print("invalid username or password")
                return JsonResponse({'error': 'Invalid username or password'})
        else:
            # Return error response with form errors
            errors = form.errors.as_json()
            return JsonResponse({'error': errors})
    else:
        return JsonResponse({'error': 'Login Failed'})
    
# Get user details 
@csrf_exempt
def get_user(request):
    if request.method == 'GET':
        # Get user id from request parameter
        user_id = request.GET.get('user_id')

        if not user_id:
            return JsonResponse({'error': 'User ID is required to get the user email'})

        # Fetch user details from the database
        user = CustomUser.objects.get(id=user_id)
        user_details = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'favourite_languages': [{'name': lang.name, 'code': lang.code} for lang in user.favourite_languages.all()],
        }
        # Return success response with user details
        return JsonResponse({'User Details': user_details})
    else:
        return JsonResponse({'error': 'Failed to get user email'})

# Editing user profile  
@csrf_exempt
def update_profile(request):
    if request.method == 'PUT':
        user_id = request.GET.get('user_id')
    
    if not user_id:
        return JsonResponse({'error': 'User ID is required'})
    
    # Fetch user profile details from the database
    profile = CustomUser.objects.get(id=user_id)
    data = json.loads(request.body.decode('utf-8')) if request.body else {}
    profile.email = data.get('email', profile.email)
    profile.save()

    new_username = data.get('username')
    profile.username = new_username
    profile.save()
    
    # Update favourite languages if available in request data
    if 'favLangCodes' in data:
        language_names = data['favLangCodes']
        languages = []

        # Iterate over language data to update or create languages
        for lang_data in language_names:
            language_name = lang_data.get('name')
            language_code = lang_data.get('code')

            if language_name and language_code:
                language_qs = Language.objects.filter(code=language_code, name=language_name)
                
                # Check if language exists, if not create a new one
                if language_qs.exists():
                    language = language_qs.first()
                else:
                    language = Language.objects.create(code=language_code, name=language_name)

                languages.append(language)

        # Set favourite languages for the user profile
        profile.favourite_languages.set(languages)
    profile.save()
    return JsonResponse({'message': 'Profile updated successfully'})
    

# Logging out user
@csrf_exempt
@require_POST
def logout_view(request: HttpRequest) -> HttpResponse:
    auth.logout(request)
    return render(request, 'globalVoice/spa/authentication/login.html', {'form': LoginForm(request.POST)})

# Translate input text into output language
@csrf_exempt
def translate_text_view(request):
    if request.method == 'POST':
        # Get information from the request
        input_language = request.POST.get('input_language', '')
        input_text = request.POST.get('input', '')
        target_language = request.POST.get('target_language', '')

        # Checks if the input language is not provided
        if (input_language == ''):
            # Detect the language of the input text
            detected_language = detect_language()
            # Translating the text into the target language
            translated_text = nllb_translator.translate_text(detected_language, input_text, target_language)
        else:
            # If input language is provided then translate from specificd language
            translated_text = nllb_translator.translate_text(input_language, input_text, target_language)
        
        response_data = {'translated_text': translated_text}
        # Return translated text with proper encoding of unicode characters and return in json format
        return JsonResponse(response_data, json_dumps_params={'ensure_ascii': False, 'indent': 2}, content_type='application/json; charset=utf-8')
    else:
        return JsonResponse({'error': 'Invalid data'})

# Automatic language detection 
@csrf_exempt
def detect_language(request):
    if request.method == 'POST':
        # Parse request and decode from utf-8
        data = json.loads(request.body.decode('utf-8'))
        input_text = data.get('input_text', '')
        # Determine language of input text
        detected_language = nllb_translator.detect_language(input_text)
        return JsonResponse({'detected_language': detected_language})

# Get supported languages
@csrf_exempt
def get_languages_view(request):
    if request.method == 'GET':
        # Call function to retrieve supported language names
        languages = nllb_translator.get_language_names()
        return JsonResponse({'languages': languages})

# Save input translations
@csrf_exempt
def save_input_translation(request):
    if request.method == 'POST':
        # Retrieve input data from request
        input_sentence = request.POST.get('input', '')
        language_code = request.POST.get('input_language_code', '')
        language_name = request.POST.get('input_language_name', '')
        user_id = request.POST.get('user_id', '')

        # Create new language object with language code and name
        language = Language(code=language_code, name=language_name)
        language.save()

        # Retrieve user object from user id
        user = CustomUser.objects.get(id=user_id)

        # Check if input text, language and user are valid
        if input_sentence and language and user:
            translation = InputTranslation.objects.create(
                input_sentence=input_sentence,
                language=language,
                user=user
            )
            translation.save()

            return JsonResponse({'message': 'Translation saved successfully','translation': {'input_sentence': translation.input_sentence, 'language': translation.language.name}})
        else: 
            print("Invalid input data")
            return JsonResponse({'error': 'Invalid input data'}, status=400)
    else:
        print("Invalid request method")
        return JsonResponse({'error': 'Invalid request method'}, status=400)

# Save output translations
@csrf_exempt
def save_output_translation(request):
    if request.method == 'POST':
        # Retrieve data from request
        output_sentence = request.POST.get('output', '')
        language_code = request.POST.get('output_language_code', '')
        language_name = request.POST.get('output_language_name', '')
        user_id = request.POST.get('user_id', '')

         # Create new language object with language code and name
        language = Language(code=language_code, name=language_name)
        language.save()

        # Retrieve user object from user id
        user = CustomUser.objects.get(id=user_id)

        # Check if output text, language and user are valid
        if output_sentence and language and user:
            translation = OutputTranslation.objects.create(
                output_sentence=output_sentence,
                language=language,
                user=user
            )
            translation.save()

            return JsonResponse({'message': 'Translation saved successfully', 'translation': {'output_sentence': translation.output_sentence, 'language': translation.language.name}})
        else: 
            print("Invalid input data")
            return JsonResponse({'error': 'Invalid input data'}, status=400)
    else:
        print("Invalid request method")
        return JsonResponse({'error': 'Invalid request method'}, status=400)    

# Get saved inputs
@csrf_exempt
def get_saved_inputs(request):
    if request.method == 'GET':
        user_id = request.GET.get('user_id')

        if not user_id:
            return JsonResponse({'error': 'User ID is required'})

        # Get saved input translations from the database for specified user
        saved_inputs = InputTranslation.objects.filter(user__id=user_id)

        # Serialise retrieved input translations
        serialized_inputs = [
            {
                'id': translation.id,
                'input_sentence': translation.input_sentence,
                'language': {
                    'id': translation.language.id,
                    'name': translation.language.name,
                },
            }
            for translation in saved_inputs
        ]

        return JsonResponse({'savedInputs': serialized_inputs})
    else:
        return JsonResponse({'error': 'Unable to retrieve saved inputs'})
    

# Get saved outputs
@csrf_exempt
def get_saved_ouputs(request):
    if request.method == 'GET':
        user_id = request.GET.get('user_id')

        if not user_id:
            return JsonResponse({'error': 'User ID is required'})
        
        # Get saved ouput translations from the database for specified user
        saved_outputs = OutputTranslation.objects.filter(user__id=user_id)

        # Serialise retrieved output translations
        serialized_outputs = [
            {
                'id': translation.id,
                'output_sentence': translation.output_sentence,
                'language': {
                    'id': translation.language.id,
                    'name': translation.language.name,
                },
            }
            for translation in saved_outputs
        ]

        return JsonResponse({'savedOutputs': serialized_outputs})
    else:
        return JsonResponse({'error': 'Unable to retrieve saved outputs'})

# Remove saved items
@csrf_exempt 
def remove_saved_items(request):
    if request.method == 'DELETE':
        user_id = request.GET.get('user_id')
        item_id = request.GET.get('item_id')
        item_type = request.GET.get('type')

        # Check if provided data is provided
        if not user_id or not item_id or not item_type:
            return JsonResponse({'error': 'User ID, item ID and item type are required'}, status=400)
        
        try:
            # Ensure atomicity of deletion
            with transaction.atomic():
                # Determine type of saved item
                if item_type == 'input':
                    saved_item = InputTranslation.objects.get(id=item_id, user_id=user_id)
                elif item_type == 'output':
                    saved_item = OutputTranslation.objects.get(id=item_id, user_id=user_id)
                else:
                    return JsonResponse({'error': 'Invalid item type'}, status=400)
                
                # Delete item
                saved_item.delete()
            return JsonResponse({'success': f'Successfully removed {item_type}'})
        # Exception if translations do not exist
        except InputTranslation.DoesNotExist:
            return JsonResponse({'error': f'Input translation with ID {item_id} does not exist for user {user_id}'}, status=404)
        except OutputTranslation.DoesNotExist:
            return JsonResponse({'error': f'Output translation with ID {item_id} does not exist for user {user_id}.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Failed to remove {item_type}. {str(e)}'}, status=500)
    return JsonResponse({'error': 'Invalid HTTP method.'}, status=405)

# Transcribe audio data into text
@csrf_exempt
def transcribe(request):
    if request.method == 'POST':
        try:
            # Check if audio is present in the request
            if 'audio' not in request.FILES:
                return JsonResponse({'error': 'Audio data not found in request.'}, status=400)
    
            # Read audio data from request
            audio_blob = request.FILES['audio'].read()
            
            # Convert audio data into AudioSegment
            audio_segment = AudioSegment.from_file(BytesIO(audio_blob), format="webm")
            temp_wav_path = "temp_audio.wav"
            # Export to WAV file
            audio_segment.export(temp_wav_path, format="wav")

            # Load processor and model
            processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
            model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")
            
            # Load audio data and sample rate 
            audio_data, sample_rate = librosa.load(temp_wav_path, sr=None)
            target_sample_rate = 16000
            # Resample audio data 
            if sample_rate != target_sample_rate:
                audio_data = librosa.resample(audio_data, orig_sr=sample_rate, target_sr=target_sample_rate)
                sample_rate = target_sample_rate

            # Normalise audio data
            normalized_audio = audio_data / 32767.0

            # Create WAV file with normalised data
            sf.write('normalized_audio.wav', normalized_audio, sample_rate)

            # Process audio data using model
            input_values = processor(normalized_audio, return_tensors="pt", padding="longest", sampling_rate=target_sample_rate).input_values

            # Perform transcription using model
            with torch.no_grad():
                logits = model(input_values).logits

            # Decode predicted ids into text
            predicted_ids = torch.argmax(logits, dim=-1)
            print("predicted_ids:", predicted_ids)
            transcription = processor.batch_decode(predicted_ids)[0]
            print("Transcription:", transcription)


            return JsonResponse({'transcribedText': transcription}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid HTTP method.'}, status=405)

        