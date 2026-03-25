from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from datetime import date, timedelta
import random

from .models import Cours, ProfilEtudiant, SessionRevision, ExamenSession, ExamenCours, CreateurProfil
from .forms import (
    InscriptionForm, ConnexionForm, SessionRevisionForm,
    ExamenSessionForm, ExamenCoursForm, CreateurProfilForm
)
from .pdf_generator import generer_pdf_revision, generer_pdf_examens


def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('connexion')


def connexion(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = ConnexionForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Identifiants incorrects. Vérifiez votre nom d\'utilisateur et mot de passe.')
    else:
        form = ConnexionForm()
    return render(request, 'registration/login.html', {'form': form})


def inscription(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            ProfilEtudiant.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, f'Bienvenue {user.first_name} ! Votre compte Cerebro a été créé.')
            return redirect('dashboard')
    else:
        form = InscriptionForm()
    return render(request, 'registration/register.html', {'form': form})


def deconnexion(request):
    logout(request)
    return redirect('connexion')


@login_required
def dashboard(request):
    user = request.user
    profil, _ = ProfilEtudiant.objects.get_or_create(user=user)
    sessions = SessionRevision.objects.filter(utilisateur=user).select_related('cours')
    examens_sessions = ExamenSession.objects.filter(utilisateur=user).prefetch_related('cours_examens__cours')

    score_global = _calculer_score_global(sessions)
    statut, message_statut = _get_statut_etudiant(user, score_global)
    comparaison_promo = _simuler_comparaison_promo(score_global)

    top3_cours = sorted(sessions, key=lambda s: s.get_score_priorite(), reverse=True)[:3]

    prochain_examen = None
    jours_avant_examen = None
    for es in examens_sessions:
        for ec in es.cours_examens.all():
            if ec.jours_restants() >= 0:
                if prochain_examen is None or ec.date_examen < prochain_examen.date_examen:
                    prochain_examen = ec
    if prochain_examen:
        jours_avant_examen = prochain_examen.jours_restants()

    context = {
        'profil': profil,
        'sessions': sessions,
        'examens_sessions': examens_sessions,
        'score_global': score_global,
        'statut': statut,
        'message_statut': message_statut,
        'comparaison_promo': comparaison_promo,
        'top3_cours': top3_cours,
        'prochain_examen': prochain_examen,
        'jours_avant_examen': jours_avant_examen,
    }
    return render(request, 'core/dashboard.html', context)


def _calculer_score_global(sessions):
    if not sessions:
        return 0
    scores = []
    for s in sessions:
        if s.note_cible > 0:
            ratio = min(1.0, s.note_actuelle / s.note_cible)
            scores.append(ratio * 100)
    if not scores:
        return 0
    return round(sum(scores) / len(scores), 1)


def _get_statut_etudiant(user, score):
    prenom = user.first_name or user.username
    if score < 30:
        return 'danger', f"{prenom}, tu risques d'échouer tes études. Il faut agir maintenant !"
    elif score < 50:
        return 'alerte', f"{prenom}, tu es en dessous du niveau requis. Intensifie tes révisions !"
    elif score < 70:
        return 'moyen', f"{prenom}, tu es sur la bonne voie mais il faut maintenir l'effort !"
    elif score < 85:
        return 'bien', f"{prenom}, tu progresses bien. Continue comme ça !"
    else:
        return 'excellent', f"{prenom}, tu es en excellente position. Garde ce rythme !"


def _simuler_comparaison_promo(score):
    pourcentage = min(95, max(5, int(score * 0.9 + random.randint(-5, 5))))
    return pourcentage


@login_required
def plan_revision(request):
    user = request.user
    if request.method == 'POST':
        form = SessionRevisionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.utilisateur = user
            session.save()
            messages.success(request, 'Analyse effectuée avec succès !')
            return redirect('plan_revision_detail', pk=session.pk)
    else:
        form = SessionRevisionForm()

    sessions = SessionRevision.objects.filter(utilisateur=user).select_related('cours')
    context = {'form': form, 'sessions': sessions}
    return render(request, 'core/plan_revision.html', context)


@login_required
def plan_revision_detail(request, pk):
    session = get_object_or_404(SessionRevision, pk=pk, utilisateur=request.user)
    heures_semaine = session.get_heures_recommandees_par_semaine()
    heures_quotidiennes = round(heures_semaine / 5, 1)
    niveau_risque = session.get_niveau_risque()
    score_priorite = session.get_score_priorite()
    ecart = max(0, session.note_cible - session.note_actuelle)

    recommandations = _generer_recommandations_revision(session, heures_semaine)
    planning_semaine = _generer_planning_semaine_simple(session, heures_semaine)

    context = {
        'session': session,
        'heures_semaine': heures_semaine,
        'heures_quotidiennes': heures_quotidiennes,
        'niveau_risque': niveau_risque,
        'score_priorite': score_priorite,
        'ecart': ecart,
        'recommandations': recommandations,
        'planning_semaine': planning_semaine,
    }
    return render(request, 'core/plan_revision_detail.html', context)


def _generer_recommandations_revision(session, heures_semaine):
    user = session.utilisateur
    nom_complet = user.get_full_name() or user.username
    cours_nom = session.cours.intitule
    ecart = max(0, session.note_cible - session.note_actuelle)
    recs = []

    if heures_semaine > 0:
        recs.append(f"{nom_complet}, tu dois augmenter ton temps sur {cours_nom} à {heures_semaine}h par semaine.")
    if session.note_actuelle < session.note_cible:
        recs.append(f"Ton niveau actuel ({session.note_actuelle}/20) est insuffisant pour atteindre {session.note_cible}/20.")
    if session.difficulte >= 4:
        recs.append(f"{cours_nom} est classé difficile. Commence par les fondamentaux avant les exercices avancés.")
    if session.urgence >= 4:
        recs.append("L'urgence est élevée. Priorise ce cours dans ton planning hebdomadaire.")
    if ecart >= 8:
        recs.append(f"L'écart entre ta note actuelle et ta cible est important ({ecart} points). Consulte ton professeur pour des ressources supplémentaires.")
    elif ecart >= 4:
        recs.append(f"Avec {heures_semaine}h de révision par semaine, tu peux combler cet écart de {ecart} points progressivement.")
    else:
        recs.append("Tu es proche de ton objectif. Maintiens le cap avec des révisions régulières.")

    return recs


def _generer_planning_semaine_simple(session, heures_semaine):
    jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']
    heures_par_jour = round(heures_semaine / 5, 1)
    planning = []
    for i, jour in enumerate(jours):
        if i < 5:
            planning.append({
                'jour': jour,
                'cours': session.cours.intitule,
                'heures': heures_par_jour,
                'focus': _get_focus_jour(i, session)
            })
        else:
            planning.append({
                'jour': jour,
                'cours': session.cours.intitule,
                'heures': round(heures_par_jour * 0.5, 1),
                'focus': 'Révision synthétique et exercices'
            })
    return planning


def _get_focus_jour(index, session):
    focus_list = [
        'Lecture et compréhension des concepts',
        'Exercices pratiques et applications',
        'Révision des points difficiles',
        'Exercices type examen',
        'Consolidation et mémorisation',
    ]
    return focus_list[index % len(focus_list)]


@login_required
def supprimer_revision(request, pk):
    session = get_object_or_404(SessionRevision, pk=pk, utilisateur=request.user)
    if request.method == 'POST':
        session.delete()
        messages.success(request, 'Session supprimée.')
    return redirect('plan_revision')


@login_required
def planning_examens(request):
    user = request.user
    if request.method == 'POST':
        form = ExamenSessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.utilisateur = user
            session.save()
            messages.success(request, 'Session d\'examens créée. Ajoutez maintenant vos cours.')
            return redirect('ajouter_cours_examen', session_pk=session.pk)
    else:
        form = ExamenSessionForm()

    sessions = ExamenSession.objects.filter(utilisateur=user).prefetch_related('cours_examens__cours')
    context = {'form': form, 'sessions': sessions}
    return render(request, 'core/planning_examens.html', context)


@login_required
def ajouter_cours_examen(request, session_pk):
    session = get_object_or_404(ExamenSession, pk=session_pk, utilisateur=request.user)
    if request.method == 'POST':
        form = ExamenCoursForm(request.POST)
        if form.is_valid():
            cours_examen = form.save(commit=False)
            cours_examen.session = session
            cours_examen.save()
            messages.success(request, f'{cours_examen.cours.intitule} ajouté à la session.')
            if 'ajouter_autre' in request.POST:
                return redirect('ajouter_cours_examen', session_pk=session.pk)
            return redirect('detail_session_examen', session_pk=session.pk)
    else:
        form = ExamenCoursForm()
    context = {'form': form, 'session': session}
    return render(request, 'core/ajouter_cours_examen.html', context)


@login_required
def detail_session_examen(request, session_pk):
    session = get_object_or_404(ExamenSession, pk=session_pk, utilisateur=request.user)
    cours_examens = session.cours_examens.select_related('cours').order_by('date_examen')

    total_heures_dispo = sum(ce.heures_totales_disponibles() for ce in cours_examens)
    total_heures_recommandees = sum(ce.get_heures_recommandees_total() for ce in cours_examens)

    timeline = _generer_timeline_examens(cours_examens, session.heures_par_semaine)
    recommandations = _generer_recommandations_examens(session, cours_examens)

    context = {
        'session': session,
        'cours_examens': cours_examens,
        'total_heures_dispo': round(total_heures_dispo, 1),
        'total_heures_recommandees': round(total_heures_recommandees, 1),
        'timeline': timeline,
        'recommandations': recommandations,
    }
    return render(request, 'core/detail_session_examen.html', context)


def _generer_timeline_examens(cours_examens, heures_par_semaine):
    jours_semaine = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']
    timeline = {jour: [] for jour in jours_semaine}

    cours_tries = sorted(cours_examens, key=lambda ce: ce.get_score_priorite(), reverse=True)

    for i, ce in enumerate(cours_tries):
        jour_principal = jours_semaine[i % 6]
        heures_jour = round(ce.get_heures_par_semaine() * 0.4, 1)
        if heures_jour > 0:
            timeline[jour_principal].append({
                'cours': ce.cours.intitule,
                'heures': heures_jour,
                'risque': ce.get_niveau_risque(),
                'date_examen': ce.date_examen,
                'jours_restants': ce.jours_restants(),
            })

        if len(cours_tries) > 1 and heures_par_semaine > 5:
            jour_sec = jours_semaine[(i + 3) % 6]
            heures_sec = round(ce.get_heures_par_semaine() * 0.3, 1)
            if heures_sec > 0:
                timeline[jour_sec].append({
                    'cours': ce.cours.intitule,
                    'heures': heures_sec,
                    'risque': ce.get_niveau_risque(),
                    'date_examen': ce.date_examen,
                    'jours_restants': ce.jours_restants(),
                })

    return timeline


def _generer_recommandations_examens(session, cours_examens):
    user = session.utilisateur
    nom_complet = user.get_full_name() or user.username
    recs = []

    cours_critiques = [ce for ce in cours_examens if ce.get_niveau_risque() == 'critique']
    cours_eleves = [ce for ce in cours_examens if ce.get_niveau_risque() == 'eleve']

    if cours_critiques:
        noms = ', '.join([ce.cours.intitule for ce in cours_critiques[:2]])
        recs.append(f"{nom_complet}, tu dois augmenter ton temps sur {noms} — niveau critique détecté.")

    for ce in cours_examens:
        ecart = max(0, ce.note_cible - ce.note_actuelle)
        if ecart > 5:
            recs.append(f"Ton niveau actuel en {ce.cours.intitule} est insuffisant pour atteindre {ce.note_cible}/20.")

    if cours_eleves:
        for ce in cours_eleves[:2]:
            recs.append(f"{ce.cours.intitule} requiert une attention particulière — {ce.jours_restants()} jours avant l'examen.")

    urgent = [ce for ce in cours_examens if ce.jours_restants() <= 14]
    if urgent:
        noms = ', '.join([ce.cours.intitule for ce in urgent[:2]])
        recs.append(f"Examens imminents dans moins de 14 jours : {noms}. Focus total requis !")

    if not recs:
        recs.append(f"{nom_complet}, tu sembles bien préparé. Continue tes révisions régulièrement.")

    return recs


@login_required
def supprimer_session_examen(request, session_pk):
    session = get_object_or_404(ExamenSession, pk=session_pk, utilisateur=request.user)
    if request.method == 'POST':
        session.delete()
        messages.success(request, 'Session d\'examens supprimée.')
    return redirect('planning_examens')


@login_required
def telecharger_pdf_revision(request, pk):
    session = get_object_or_404(SessionRevision, pk=pk, utilisateur=request.user)
    heures_semaine = session.get_heures_recommandees_par_semaine()
    planning = _generer_planning_semaine_simple(session, heures_semaine)
    recommandations = _generer_recommandations_revision(session, heures_semaine)
    buffer = generer_pdf_revision(session, planning, recommandations)
    response = HttpResponse(buffer, content_type='application/pdf')
    nom_fichier = f"cerebro_revision_{session.cours.code}_{timezone.now().strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{nom_fichier}"'
    return response


@login_required
def telecharger_pdf_examens(request, session_pk):
    session = get_object_or_404(ExamenSession, pk=session_pk, utilisateur=request.user)
    cours_examens = session.cours_examens.select_related('cours').order_by('date_examen')
    timeline = _generer_timeline_examens(cours_examens, session.heures_par_semaine)
    recommandations = _generer_recommandations_examens(session, cours_examens)
    buffer = generer_pdf_examens(session, cours_examens, timeline, recommandations)
    response = HttpResponse(buffer, content_type='application/pdf')
    nom_fichier = f"cerebro_examens_{timezone.now().strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{nom_fichier}"'
    return response


def about(request):
    return render(request, 'core/about.html')


def createur_public(request):
    try:
        profil = CreateurProfil.objects.filter(is_visible=True).latest('updated_at')
    except CreateurProfil.DoesNotExist:
        profil = None
    return render(request, 'core/createur.html', {'profil': profil})


def is_admin(user):
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_admin)
def createur_admin(request):
    try:
        profil = CreateurProfil.objects.get(user=request.user)
    except CreateurProfil.DoesNotExist:
        profil = None

    if request.method == 'POST':
        if profil:
            form = CreateurProfilForm(request.POST, request.FILES, instance=profil)
        else:
            form = CreateurProfilForm(request.POST, request.FILES)
        if form.is_valid():
            profil_obj = form.save(commit=False)
            profil_obj.user = request.user
            profil_obj.save()
            messages.success(request, 'Profil créateur mis à jour avec succès.')
            return redirect('createur_admin')
    else:
        form = CreateurProfilForm(instance=profil)

    return render(request, 'core/createur_admin.html', {'form': form, 'profil': profil})
