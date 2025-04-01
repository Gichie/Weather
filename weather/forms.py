from django import forms


class SearchLocationForm(forms.Form):
    location = forms.CharField(
        max_length=190,
        label='Поиск',
        widget=forms.TextInput(attrs={'placeholder': 'Введите название локации', 'class': 'form-input'}),
    )
