from django import forms
from .nllb_model import nllb_translator

class LoginForm(forms.Form):
    '''Form for user login'''

    username = forms.CharField(
        label='Username',
        max_length=50,
        widget=forms.TextInput(attrs={'autocomplete': 'username'})
    )
    password = forms.CharField(
        label='Password',
        max_length=50,
        widget=forms.PasswordInput(attrs={'autocomplete': 'password'})
    )


class SignupForm(forms.Form):
    '''Form for user signup'''

    username = forms.CharField(
        label='Username',
        max_length=50,
        widget=forms.TextInput(
            attrs={
                'autocomplete': 'username',
            }
        )
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(
            attrs={
                'autocomplete': 'email',
            }
        )
    )
    password = forms.CharField(
        label='Password',
        max_length=50,
        widget=forms.PasswordInput(attrs={'autocomplete': 'password'})
    )