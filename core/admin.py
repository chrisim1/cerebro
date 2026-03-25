from django.contrib import admin
from .models import Cours, ProfilEtudiant, SessionRevision, ExamenSession, ExamenCours, CreateurProfil


@admin.register(Cours)
class CoursAdmin(admin.ModelAdmin):
    list_display = ['code', 'intitule', 'credits', 'niveau', 'is_active']
    list_filter = ['niveau', 'is_active']
    search_fields = ['code', 'intitule']


@admin.register(ProfilEtudiant)
class ProfilEtudiantAdmin(admin.ModelAdmin):
    list_display = ['user', 'niveau', 'heures_par_semaine']


@admin.register(SessionRevision)
class SessionRevisionAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'cours', 'note_actuelle', 'note_cible', 'created_at']
    list_filter = ['utilisateur']


@admin.register(ExamenSession)
class ExamenSessionAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'nom_session', 'heures_par_semaine', 'created_at']


@admin.register(ExamenCours)
class ExamenCoursAdmin(admin.ModelAdmin):
    list_display = ['session', 'cours', 'date_examen', 'note_actuelle', 'note_cible', 'maitrise']


@admin.register(CreateurProfil)
class CreateurProfilAdmin(admin.ModelAdmin):
    list_display = ['nom_complet', 'titre', 'is_visible', 'updated_at']
