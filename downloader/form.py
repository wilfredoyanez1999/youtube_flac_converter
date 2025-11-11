# downloader/forms.py

from django import forms

class LinkForm(forms.Form):
    # Campo de entrada para el enlace de YouTube
    link = forms.URLField(
        label='Link de YouTube', 
        max_length=500, 
        widget=forms.TextInput(attrs={'placeholder': 'Pega el link de YouTube aquí'})
    )