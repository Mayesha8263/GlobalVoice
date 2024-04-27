from django.contrib import admin
from django.urls import include, path, re_path
from globalVoice.views import main_spa

urlpatterns = [
    path('globalVoice/', include('globalVoice.urls')),
    re_path(r'.*', main_spa)
]
