from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from datetime import date, timedelta
import random

from .models import (Cours, ProfilEtudiant, SessionRevision, ExamenSession,
                     ExamenCours, CreateurProfil, AudioPresentation)
from .forms import (
    InscriptionForm, ConnexionForm, SessionRevisionForm,
    ExamenSessionForm, ExamenCoursForm, CreateurProfilForm,
    ProfilEtudiantForm, AudioPresentationForm
)
from .pdf_generator import generer_pdf_revision, generer_pdf_examens, generer_pdf_multi_revision


def _nettoyer_examens_passes(user, request):
    today = date.today()
    passes = ExamenCours.objects.filter(session__utilisateur=user, date_examen__lt=today)
    count = passes.count()
    if count > 0:
        noms = list(passes.values_list('cours__intitule', flat=True)[:3])
        passes.delete()
        if count == 1:
            messages.info(request, f'Examen passé retiré du planning : {noms[0]}. Algorithme recalculé.')
        else:
            liste = ', '.join(noms)
            messages.info(request, f'{count} examens passés retirés du planning ({liste}…). Planning mis à jour.')
    return count


def _get_audio_actif():
    try:
        return AudioPresentation.objects.filter(is_active=True).latest('created_at')
    except AudioPresentation.DoesNotExist:
        return None


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
    _nettoyer_examens_passes(user, request)

    profil, _ = ProfilEtudiant.objects.get_or_create(user=user)
    sessions = SessionRevision.objects.filter(utilisateur=user).select_related('cours')
    today = date.today()
    examens_sessions = ExamenSession.objects.filter(utilisateur=user).prefetch_related('cours_examens__cours')

    score_global = _calculer_score_global(sessions)
    statut, message_statut = _get_statut_etudiant(user, score_global)
    comparaison_promo = _simuler_comparaison_promo(score_global)

    top3_cours = sorted(sessions, key=lambda s: s.get_score_priorite(), reverse=True)[:3]

    prochain_examen = None
    jours_avant_examen = None
    for es in examens_sessions:
        for ec in es.cours_examens.filter(date_examen__gte=today).order_by('date_examen'):
            if prochain_examen is None or ec.date_examen < prochain_examen.date_examen:
                prochain_examen = ec
    if prochain_examen:
        jours_avant_examen = prochain_examen.jours_restants()

    examens_actifs_count = ExamenCours.objects.filter(
        session__utilisateur=user, date_examen__gte=today
    ).count()

    audio = _get_audio_actif()

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
        'examens_actifs_count': examens_actifs_count,
        'audio': audio,
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


# ===== MON PROFIL =====

@login_required
def mon_profil(request):
    user = request.user
    profil, _ = ProfilEtudiant.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = ProfilEtudiantForm(request.POST, request.FILES, instance=profil)
        if form.is_valid():
            profil_obj = form.save(commit=False)
            profil_obj.user = user
            profil_obj.save()
            user.first_name = form.cleaned_data.get('first_name', user.first_name)
            user.last_name = form.cleaned_data.get('last_name', user.last_name)
            email = form.cleaned_data.get('email', '').strip()
            if email:
                user.email = email
            user.save()
            messages.success(request, 'Profil mis à jour avec succès.')
            return redirect('mon_profil')
    else:
        form = ProfilEtudiantForm(instance=profil, initial={
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        })

    sessions_count = user.sessions_revision.count()
    examens_count = user.examens.count()
    context = {
        'form': form,
        'profil': profil,
        'sessions_count': sessions_count,
        'examens_count': examens_count,
    }
    return render(request, 'core/mon_profil.html', context)


# ===== ANALYSE MULTI-COURS =====

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
def plan_revision_multi(request):
    user = request.user
    cours_par_niveau = {}
    for niveau, label in Cours.NIVEAU_CHOICES:
        cours_par_niveau[label] = list(Cours.objects.filter(niveau=niveau, is_active=True))

    if request.method == 'POST':
        nb_cours = int(request.POST.get('nb_cours', 0))
        sessions_crees = []
        erreurs = []

        for i in range(nb_cours):
            cours_id = request.POST.get(f'cours_{i}')
            note_actuelle = request.POST.get(f'note_actuelle_{i}')
            note_cible = request.POST.get(f'note_cible_{i}')
            difficulte = request.POST.get(f'difficulte_{i}', '3')
            urgence = request.POST.get(f'urgence_{i}', '3')
            heures = request.POST.get(f'heures_{i}', '10')

            if not cours_id or not note_actuelle or not note_cible:
                continue

            try:
                cours = Cours.objects.get(pk=cours_id)
                na = float(note_actuelle)
                nc = float(note_cible)
                d = int(difficulte)
                u = int(urgence)
                h = float(heures)

                if not (0 <= na <= 20 and 0 <= nc <= 20 and 0 <= d <= 5 and 0 <= u <= 5 and h > 0):
                    erreurs.append(f"Valeurs invalides pour {cours.intitule}")
                    continue

                existing = SessionRevision.objects.filter(utilisateur=user, cours=cours).first()
                if existing:
                    existing.note_actuelle = na
                    existing.note_cible = nc
                    existing.difficulte = d
                    existing.urgence = u
                    existing.heures_par_semaine = h
                    existing.save()
                    sessions_crees.append(existing)
                else:
                    s = SessionRevision.objects.create(
                        utilisateur=user, cours=cours,
                        note_actuelle=na, note_cible=nc,
                        difficulte=d, urgence=u, heures_par_semaine=h
                    )
                    sessions_crees.append(s)
            except (Cours.DoesNotExist, ValueError) as e:
                erreurs.append(str(e))

        if erreurs:
            for e in erreurs:
                messages.error(request, e)

        if sessions_crees:
            ids = ','.join(str(s.pk) for s in sessions_crees)
            return redirect(f'/revision/multi/resultat/?ids={ids}')
        else:
            messages.error(request, 'Aucun cours valide soumis.')

    context = {
        'cours_par_niveau': cours_par_niveau,
        'tous_les_cours': Cours.objects.filter(is_active=True).order_by('niveau', 'code'),
    }
    return render(request, 'core/plan_revision_multi.html', context)


@login_required
def plan_revision_multi_resultat(request):
    ids_str = request.GET.get('ids', '')
    ids = [int(x) for x in ids_str.split(',') if x.strip().isdigit()]
    sessions = SessionRevision.objects.filter(pk__in=ids, utilisateur=request.user).select_related('cours')

    if not sessions:
        messages.error(request, 'Aucune session trouvée.')
        return redirect('plan_revision_multi')

    sessions_triees = sorted(sessions, key=lambda s: s.get_score_priorite(), reverse=True)

    total_heures_semaine = sum(s.get_heures_recommandees_par_semaine() for s in sessions_triees)
    score_global = _calculer_score_global(sessions)

    planning_multi = _generer_planning_multi(sessions_triees)
    recommandations = _generer_recommandations_multi(sessions_triees, request.user)

    context = {
        'sessions': sessions_triees,
        'total_heures_semaine': round(total_heures_semaine, 1),
        'score_global': round(score_global, 1),
        'planning_multi': planning_multi,
        'recommandations': recommandations,
        'ids_str': ids_str,
    }
    return render(request, 'core/plan_revision_multi_resultat.html', context)


def _generer_planning_multi(sessions_triees):
    jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']
    planning = {j: [] for j in jours}

    for i, session in enumerate(sessions_triees):
        heures = session.get_heures_recommandees_par_semaine()
        if heures <= 0:
            continue
        nb_jours = min(len(jours), max(1, round(heures / 1.5)))
        heures_par_jour = round(heures / nb_jours, 1)
        for j in range(nb_jours):
            jour = jours[(i * 2 + j) % 6]
            planning[jour].append({
                'cours': session.cours.intitule,
                'heures': heures_par_jour,
                'risque': session.get_niveau_risque(),
                'score': session.get_score_priorite(),
            })

    return planning


def _generer_recommandations_multi(sessions, user):
    nom = user.get_full_name() or user.username
    recs = []
    critiques = [s for s in sessions if s.get_niveau_risque() == 'critique']
    eleves = [s for s in sessions if s.get_niveau_risque() == 'eleve']

    if critiques:
        noms = ', '.join(s.cours.intitule for s in critiques[:2])
        recs.append(f"{nom}, priorité absolue sur : {noms}. Commence dès aujourd'hui !")

    if eleves:
        noms = ', '.join(s.cours.intitule for s in eleves[:2])
        recs.append(f"Attention requise sur : {noms}. Planifie des sessions intensives cette semaine.")

    total_heures = sum(s.get_heures_recommandees_par_semaine() for s in sessions)
    recs.append(f"Volume total de révision recommandé : {round(total_heures, 1)}h/semaine pour {len(sessions)} cours.")

    gros_ecart = [s for s in sessions if (s.note_cible - s.note_actuelle) >= 6]
    if gros_ecart:
        noms = ', '.join(s.cours.intitule for s in gros_ecart[:2])
        recs.append(f"Écart important détecté en {noms}. Consulte ton professeur pour des ressources complémentaires.")

    if not critiques and not eleves:
        recs.append(f"{nom}, ton niveau global est satisfaisant. Maintiens tes révisions régulières pour consolider tes acquis.")

    return recs


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
    _nettoyer_examens_passes(user, request)

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

    today = date.today()
    sessions = ExamenSession.objects.filter(utilisateur=user).prefetch_related('cours_examens__cours')
    context = {'form': form, 'sessions': sessions, 'today': today}
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
    _nettoyer_examens_passes(request.user, request)

    today = date.today()
    cours_examens = session.cours_examens.filter(date_examen__gte=today).select_related('cours').order_by('date_examen')

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
def telecharger_pdf_multi(request):
    ids_str = request.GET.get('ids', '')
    ids = [int(x) for x in ids_str.split(',') if x.strip().isdigit()]
    sessions = SessionRevision.objects.filter(pk__in=ids, utilisateur=request.user).select_related('cours')
    sessions_triees = sorted(sessions, key=lambda s: s.get_score_priorite(), reverse=True)

    planning_multi = _generer_planning_multi(sessions_triees)
    recommandations = _generer_recommandations_multi(sessions_triees, request.user)

    buffer = generer_pdf_multi_revision(request.user, sessions_triees, planning_multi, recommandations)
    response = HttpResponse(buffer, content_type='application/pdf')
    nom_fichier = f"cerebro_analyse_multi_{timezone.now().strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{nom_fichier}"'
    return response


@login_required
def telecharger_pdf_examens(request, session_pk):
    session = get_object_or_404(ExamenSession, pk=session_pk, utilisateur=request.user)
    today = date.today()
    cours_examens = session.cours_examens.filter(date_examen__gte=today).select_related('cours').order_by('date_examen')
    timeline = _generer_timeline_examens(cours_examens, session.heures_par_semaine)
    recommandations = _generer_recommandations_examens(session, cours_examens)
    buffer = generer_pdf_examens(session, cours_examens, timeline, recommandations)
    response = HttpResponse(buffer, content_type='application/pdf')
    nom_fichier = f"cerebro_examens_{timezone.now().strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{nom_fichier}"'
    return response


def about(request):
    audio = _get_audio_actif()
    return render(request, 'core/about.html', {'audio': audio})


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
        if request.POST.get('signature_only') == '1':
            sig_file = request.FILES.get('signature')
            if sig_file:
                if profil is None:
                    profil = CreateurProfil(user=request.user, nom_complet=request.user.get_full_name() or request.user.username)
                profil.signature = sig_file
                profil.save()
                messages.success(request, 'Signature mise à jour avec succès — elle apparaîtra sur tous vos prochains PDFs.')
            else:
                messages.error(request, 'Aucun fichier sélectionné.')
            return redirect('createur_admin')

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


@login_required
@user_passes_test(is_admin)
def audio_admin(request):
    audios = AudioPresentation.objects.all().order_by('-created_at')

    if request.method == 'POST':
        if 'supprimer' in request.POST:
            audio_id = request.POST.get('supprimer')
            try:
                audio = AudioPresentation.objects.get(pk=audio_id)
                audio.delete()
                messages.success(request, 'Audio supprimé.')
            except AudioPresentation.DoesNotExist:
                pass
            return redirect('audio_admin')

        if 'toggle_actif' in request.POST:
            audio_id = request.POST.get('toggle_actif')
            try:
                audio = AudioPresentation.objects.get(pk=audio_id)
                AudioPresentation.objects.all().update(is_active=False)
                audio.is_active = True
                audio.save()
                messages.success(request, f'"{audio.titre}" est maintenant l\'audio actif.')
            except AudioPresentation.DoesNotExist:
                pass
            return redirect('audio_admin')

        form = AudioPresentationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Audio uploadé avec succès.')
            return redirect('audio_admin')
    else:
        form = AudioPresentationForm()

    context = {'form': form, 'audios': audios}
    return render(request, 'core/audio_admin.html', context)
