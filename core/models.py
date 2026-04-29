from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Cours(models.Model):
    NIVEAU_CHOICES = [
        ('L1S1', 'L1 - Semestre 1'),
        ('L1S2', 'L1 - Semestre 2'),
        ('L2S3', 'L2 - Semestre 3'),
        ('L2S4', 'L2 - Semestre 4'),
    ]
    code = models.CharField(max_length=20)
    intitule = models.CharField(max_length=200)
    credits = models.IntegerField(default=2)
    niveau = models.CharField(max_length=10, choices=NIVEAU_CHOICES, default='L1S1')
    cmi = models.IntegerField(default=0, help_text="Cours Magistraux Intégrés")
    td = models.IntegerField(default=0, help_text="Travaux Dirigés")
    tp = models.IntegerField(default=0, help_text="Travaux Pratiques")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['niveau', 'code', 'intitule']
        verbose_name = 'Cours'
        verbose_name_plural = 'Cours'

    def __str__(self):
        return f"{self.code} - {self.intitule} ({self.credits} cr)"


class ProfilEtudiant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    niveau = models.CharField(max_length=10, choices=Cours.NIVEAU_CHOICES, default='L1S1')
    heures_par_semaine = models.FloatField(default=10.0)
    photo = models.ImageField(upload_to='profils/', blank=True, null=True)
    bio = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profil de {self.user.get_full_name() or self.user.username}"

    def get_photo_url(self):
        if self.photo and hasattr(self.photo, 'url'):
            return self.photo.url
        return None


class SessionRevision(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions_revision')
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE)
    note_actuelle = models.FloatField(help_text="Note actuelle sur 20")
    note_cible = models.FloatField(help_text="Note cible sur 20")
    difficulte = models.IntegerField(default=3, help_text="Difficulté de 0 à 5")
    urgence = models.IntegerField(default=3, help_text="Urgence de 0 à 5")
    heures_par_semaine = models.FloatField(default=10.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.utilisateur.username} - {self.cours.intitule}"

    def get_score_priorite(self):
        ecart = max(0, self.note_cible - self.note_actuelle)
        score = (ecart / 20) * 40 + (self.difficulte / 5) * 35 + (self.urgence / 5) * 25
        return round(score, 2)

    def get_niveau_risque(self):
        score = self.get_score_priorite()
        if score >= 60:
            return 'critique'
        elif score >= 35:
            return 'eleve'
        else:
            return 'stable'

    def get_heures_recommandees_par_semaine(self):
        ecart = max(0, self.note_cible - self.note_actuelle)
        base = (ecart / 20) * self.heures_par_semaine
        facteur_difficulte = 1 + (self.difficulte / 10)
        facteur_urgence = 1 + (self.urgence / 10)
        heures = base * facteur_difficulte * facteur_urgence
        return round(min(heures, self.heures_par_semaine), 1)


class ExamenSession(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='examens')
    nom_session = models.CharField(max_length=100, default='Session principale')
    heures_par_semaine = models.FloatField(default=10.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.utilisateur.username} - {self.nom_session}"


class ExamenCours(models.Model):
    session = models.ForeignKey(ExamenSession, on_delete=models.CASCADE, related_name='cours_examens')
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE)
    date_examen = models.DateField()
    note_actuelle = models.FloatField(help_text="Note actuelle sur 20")
    note_cible = models.FloatField(help_text="Note cible sur 20")
    maitrise = models.IntegerField(default=3, help_text="Niveau de maîtrise de 0 à 5")

    class Meta:
        ordering = ['date_examen']

    def __str__(self):
        return f"{self.cours.intitule} - {self.date_examen}"

    def jours_restants(self):
        today = timezone.now().date()
        delta = self.date_examen - today
        return max(0, delta.days)

    def semaines_restantes(self):
        return max(0.1, self.jours_restants() / 7)

    def heures_totales_disponibles(self):
        return self.session.heures_par_semaine * self.semaines_restantes()

    def get_score_priorite(self):
        ecart = max(0, self.note_cible - self.note_actuelle)
        manque_maitrise = max(0, 5 - self.maitrise)
        urgence_temps = max(0, 30 - self.jours_restants()) / 30
        score = (ecart / 20) * 40 + (manque_maitrise / 5) * 35 + urgence_temps * 25
        return round(score, 2)

    def get_niveau_risque(self):
        score = self.get_score_priorite()
        if score >= 60:
            return 'critique'
        elif score >= 35:
            return 'eleve'
        else:
            return 'stable'

    def get_heures_recommandees_total(self):
        ecart = max(0, self.note_cible - self.note_actuelle)
        facteur_maitrise = (5 - self.maitrise) / 5
        heures = self.heures_totales_disponibles() * (0.3 + facteur_maitrise * 0.5 + (ecart / 20) * 0.2)
        return round(min(heures, self.heures_totales_disponibles()), 1)

    def get_heures_par_semaine(self):
        semaines = self.semaines_restantes()
        if semaines <= 0:
            return 0
        return round(self.get_heures_recommandees_total() / semaines, 1)


class AudioPresentation(models.Model):
    titre = models.CharField(max_length=200, default='Présentation Cerebro')
    audio_file = models.FileField(upload_to='audio/', help_text="Fichier audio MP3, WAV ou OGG")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Audio de présentation'
        verbose_name_plural = 'Audios de présentation'

    def __str__(self):
        return self.titre


class CreateurProfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='createur_profil')
    nom_complet = models.CharField(max_length=200)
    titre = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to='createur/', blank=True, null=True)
    signature = models.ImageField(upload_to='signatures/', blank=True, null=True,
                                  help_text="Signature manuscrite (PNG fond transparent ou fond blanc) — apparaîtra sur tous les PDFs")
    competences = models.TextField(blank=True, help_text="Compétences séparées par des virgules")
    site_web = models.URLField(blank=True)
    github = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    projet_cerebro_desc = models.TextField(blank=True)
    is_visible = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom_complet

    def get_competences_liste(self):
        if self.competences:
            return [c.strip() for c in self.competences.split(',') if c.strip()]
        return []
