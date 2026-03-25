from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.connexion, name='connexion'),
    path('register/', views.inscription, name='inscription'),
    path('logout/', views.deconnexion, name='deconnexion'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('revision/', views.plan_revision, name='plan_revision'),
    path('revision/<int:pk>/', views.plan_revision_detail, name='plan_revision_detail'),
    path('revision/<int:pk>/supprimer/', views.supprimer_revision, name='supprimer_revision'),
    path('revision/<int:pk>/pdf/', views.telecharger_pdf_revision, name='telecharger_pdf_revision'),

    path('examens/', views.planning_examens, name='planning_examens'),
    path('examens/<int:session_pk>/cours/', views.ajouter_cours_examen, name='ajouter_cours_examen'),
    path('examens/<int:session_pk>/', views.detail_session_examen, name='detail_session_examen'),
    path('examens/<int:session_pk>/supprimer/', views.supprimer_session_examen, name='supprimer_session_examen'),
    path('examens/<int:session_pk>/pdf/', views.telecharger_pdf_examens, name='telecharger_pdf_examens'),

    path('about/', views.about, name='about'),
    path('createur/', views.createur_public, name='createur'),
    path('createur/admin/', views.createur_admin, name='createur_admin'),
]
