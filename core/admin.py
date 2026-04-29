from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import Cours, ProfilEtudiant, SessionRevision, ExamenSession, ExamenCours, CreateurProfil, AudioPresentation


class ProfilInline(admin.StackedInline):
    model = ProfilEtudiant
    can_delete = False
    verbose_name_plural = 'Profil étudiant'
    fields = ['niveau', 'heures_par_semaine', 'bio']


class UserAdmin(BaseUserAdmin):
    inlines = [ProfilInline]
    list_display = ['username', 'get_full_name', 'email', 'date_joined', 'is_active', 'get_nb_revisions', 'get_nb_examens']
    list_filter = ['is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['-date_joined']
    readonly_fields = ['date_joined', 'last_login']

    def get_full_name(self, obj):
        return obj.get_full_name() or '—'
    get_full_name.short_description = 'Nom complet'

    def get_nb_revisions(self, obj):
        count = obj.sessions_revision.count()
        return format_html('<span style="color:#1e90ff;font-weight:600">{}</span>', count)
    get_nb_revisions.short_description = 'Révisions'

    def get_nb_examens(self, obj):
        count = obj.examens.count()
        return format_html('<span style="color:#2ecc71;font-weight:600">{}</span>', count)
    get_nb_examens.short_description = 'Sessions exam.'


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Cours)
class CoursAdmin(admin.ModelAdmin):
    list_display = ['code', 'intitule', 'credits', 'niveau', 'is_active']
    list_filter = ['niveau', 'is_active']
    search_fields = ['code', 'intitule']


@admin.register(ProfilEtudiant)
class ProfilEtudiantAdmin(admin.ModelAdmin):
    list_display = ['user', 'niveau', 'heures_par_semaine', 'get_date_inscription']
    list_filter = ['niveau']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']

    def get_date_inscription(self, obj):
        return obj.user.date_joined.strftime('%d/%m/%Y')
    get_date_inscription.short_description = 'Inscrit le'


@admin.register(SessionRevision)
class SessionRevisionAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'cours', 'note_actuelle', 'note_cible', 'created_at']
    list_filter = ['utilisateur', 'created_at']
    search_fields = ['utilisateur__username', 'cours__intitule']
    date_hierarchy = 'created_at'


@admin.register(ExamenSession)
class ExamenSessionAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'nom_session', 'heures_par_semaine', 'created_at']
    list_filter = ['created_at']
    search_fields = ['utilisateur__username']


@admin.register(ExamenCours)
class ExamenCoursAdmin(admin.ModelAdmin):
    list_display = ['session', 'cours', 'date_examen', 'note_actuelle', 'note_cible', 'maitrise']
    list_filter = ['date_examen']
    search_fields = ['cours__intitule']


@admin.register(AudioPresentation)
class AudioPresentationAdmin(admin.ModelAdmin):
    list_display = ['titre', 'is_active', 'created_at']
    list_filter = ['is_active']


@admin.register(CreateurProfil)
class CreateurProfilAdmin(admin.ModelAdmin):
    list_display = ['nom_complet', 'titre', 'is_visible', 'updated_at']


admin.site.site_header = 'CEREBRO — Administration'
admin.site.site_title = 'Cerebro Admin'
admin.site.index_title = 'Tableau de bord administrateur'
