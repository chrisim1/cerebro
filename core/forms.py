from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import SessionRevision, ExamenSession, ExamenCours, Cours, CreateurProfil, ProfilEtudiant, AudioPresentation


class InscriptionForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=50, required=True,
        label='Prénom',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre prénom'})
    )
    last_name = forms.CharField(
        max_length=50, required=True,
        label='Nom',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom'})
    )
    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'votre@email.com'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom d\'utilisateur'}),
        }
        labels = {
            'username': 'Nom d\'utilisateur',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Mot de passe'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmer le mot de passe'})
        self.fields['password1'].label = 'Mot de passe'
        self.fields['password2'].label = 'Confirmer le mot de passe'


class ConnexionForm(forms.Form):
    username = forms.CharField(
        label='Nom d\'utilisateur',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom d\'utilisateur'})
    )
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'})
    )


class SessionRevisionForm(forms.ModelForm):
    class Meta:
        model = SessionRevision
        fields = ['cours', 'note_actuelle', 'note_cible', 'difficulte', 'urgence', 'heures_par_semaine']
        widgets = {
            'cours': forms.Select(attrs={'class': 'form-control'}),
            'note_actuelle': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.5', 'min': '0', 'max': '20',
                'placeholder': 'ex: 11'
            }),
            'note_cible': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.5', 'min': '0', 'max': '20',
                'placeholder': 'ex: 15'
            }),
            'difficulte': forms.NumberInput(attrs={
                'class': 'form-control', 'min': '0', 'max': '5',
                'placeholder': '0 = très facile, 5 = très difficile'
            }),
            'urgence': forms.NumberInput(attrs={
                'class': 'form-control', 'min': '0', 'max': '5',
                'placeholder': '0 = pas urgent, 5 = très urgent'
            }),
            'heures_par_semaine': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.5', 'min': '1', 'max': '80',
                'placeholder': 'ex: 15'
            }),
        }
        labels = {
            'cours': 'Cours',
            'note_actuelle': 'Note actuelle (sur 20)',
            'note_cible': 'Note cible (sur 20)',
            'difficulte': 'Difficulté perçue (0 à 5)',
            'urgence': 'Urgence (0 à 5)',
            'heures_par_semaine': 'Heures disponibles par semaine',
        }


class ExamenSessionForm(forms.ModelForm):
    class Meta:
        model = ExamenSession
        fields = ['nom_session', 'heures_par_semaine']
        widgets = {
            'nom_session': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'ex: Session de juin 2026'
            }),
            'heures_par_semaine': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.5', 'min': '1', 'max': '80',
                'placeholder': 'ex: 20'
            }),
        }
        labels = {
            'nom_session': 'Nom de la session',
            'heures_par_semaine': 'Heures disponibles par semaine',
        }


class ExamenCoursForm(forms.ModelForm):
    class Meta:
        model = ExamenCours
        fields = ['cours', 'date_examen', 'note_actuelle', 'note_cible', 'maitrise']
        widgets = {
            'cours': forms.Select(attrs={'class': 'form-control'}),
            'date_examen': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'note_actuelle': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.5', 'min': '0', 'max': '20'
            }),
            'note_cible': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.5', 'min': '0', 'max': '20'
            }),
            'maitrise': forms.NumberInput(attrs={
                'class': 'form-control', 'min': '0', 'max': '5',
                'placeholder': '0 = pas maîtrisé, 5 = parfaitement maîtrisé'
            }),
        }
        labels = {
            'cours': 'Cours',
            'date_examen': 'Date de l\'examen',
            'note_actuelle': 'Note actuelle (sur 20)',
            'note_cible': 'Note cible (sur 20)',
            'maitrise': 'Niveau de maîtrise (0 à 5)',
        }


class ProfilEtudiantForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=50, required=False, label='Prénom',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=50, required=False, label='Nom',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=False, label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = ProfilEtudiant
        fields = ['niveau', 'heures_par_semaine', 'photo', 'bio']
        widgets = {
            'niveau': forms.Select(attrs={'class': 'form-control'}),
            'heures_par_semaine': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.5', 'min': '1', 'max': '80'
            }),
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'bio': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Quelques mots sur toi…'
            }),
        }
        labels = {
            'niveau': 'Niveau d\'études',
            'heures_par_semaine': 'Heures disponibles par semaine',
            'photo': 'Photo de profil',
            'bio': 'À propos de toi',
        }


class AudioPresentationForm(forms.ModelForm):
    class Meta:
        model = AudioPresentation
        fields = ['titre', 'audio_file', 'description', 'is_active']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'audio_file': forms.FileInput(attrs={'class': 'form-control', 'accept': 'audio/*'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'titre': 'Titre',
            'audio_file': 'Fichier audio (MP3, WAV, OGG)',
            'description': 'Description',
            'is_active': 'Actif (visible sur le site)',
        }


class CreateurProfilForm(forms.ModelForm):
    class Meta:
        model = CreateurProfil
        fields = ['nom_complet', 'titre', 'description', 'photo', 'signature', 'competences',
                  'site_web', 'github', 'linkedin', 'projet_cerebro_desc', 'is_visible']
        widgets = {
            'nom_complet': forms.TextInput(attrs={'class': 'form-control'}),
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'signature': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'competences': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Python, Django, Machine Learning, ...'
            }),
            'site_web': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'github': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/...'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/in/...'}),
            'projet_cerebro_desc': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_visible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nom_complet': 'Nom complet',
            'titre': 'Titre / Rôle',
            'description': 'Description / Bio',
            'photo': 'Photo de profil',
            'signature': 'Signature manuscrite (PDF)',
            'competences': 'Compétences (séparées par des virgules)',
            'site_web': 'Site web personnel',
            'github': 'Profil GitHub',
            'linkedin': 'Profil LinkedIn',
            'projet_cerebro_desc': 'Description du projet Cerebro',
            'is_visible': 'Rendre le profil visible publiquement',
        }
