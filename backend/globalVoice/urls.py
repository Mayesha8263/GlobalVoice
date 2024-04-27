from django.urls import path, re_path
from .views import main_spa, signup_view, login_view, logout_view, translate_text_view, get_languages_view, save_input_translation, get_saved_inputs, save_output_translation, get_saved_ouputs, get_user, update_profile, remove_saved_items, transcribe, detect_language

app_name = "globalVoice"
urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('translate/', translate_text_view, name='translate'),
    path('getLanguages/', get_languages_view, name='languages'),
    path('saveInputTranslation/', save_input_translation, name='saveInputTranslation'),
    path('getSavedInputs/', get_saved_inputs, name='getSavedInputs'),
    path('saveOutputTranslation/', save_output_translation, name='saveOutputTranslation'),
    path('getSavedOutputs/', get_saved_ouputs, name='getSavedOutputs'),
    path('getUser/', get_user, name='getUser'),
    path('updateProfile/', update_profile, name='updateProfile'),
    path('removeSavedItem/', remove_saved_items, name='removeSavedItem'),
    path('transcribe/', transcribe, name='transcribe'),
    path('detectLanguage/', detect_language, name='detectLanguage'),
    re_path(r'.*', main_spa)
]
