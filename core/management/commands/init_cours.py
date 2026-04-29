from django.core.management.base import BaseCommand
from core.models import Cours


COURS_DATA = [
    # L1 Semestre 1
    {'code': 'COM1111', 'intitule': 'Communication — Techniques d\'expression orale et écrite', 'credits': 2, 'niveau': 'L1S1', 'cmi': 20, 'td': 5, 'tp': 5},
    {'code': 'COM1111', 'intitule': 'Communication — Bureautique informatique', 'credits': 4, 'niveau': 'L1S1', 'cmi': 30, 'td': 5, 'tp': 30},
    {'code': 'CHE1111', 'intitule': 'Civisme — Valeurs, Principes et symboles de la République', 'credits': 2, 'niveau': 'L1S1', 'cmi': 20, 'td': 5, 'tp': 5},
    {'code': 'CHE1111', 'intitule': 'Civisme — Hygiène et Environnement', 'credits': 2, 'niveau': 'L1S1', 'cmi': 20, 'td': 10, 'tp': 5},
    {'code': 'INF1111', 'intitule': 'Informatique — Introduction à l\'informatique', 'credits': 2, 'niveau': 'L1S1', 'cmi': 15, 'td': 5, 'tp': 10},
    {'code': 'INF1111', 'intitule': 'Informatique — Outils de bureautique, internet et design graphique', 'credits': 3, 'niveau': 'L1S1', 'cmi': 10, 'td': 10, 'tp': 25},
    {'code': 'COF1111', 'intitule': 'Comptabilité Fondamentale', 'credits': 2, 'niveau': 'L1S1', 'cmi': 15, 'td': 30, 'tp': 10},
    {'code': 'MAT1111', 'intitule': 'Mathématique — Algèbre Linéaire', 'credits': 3, 'niveau': 'L1S1', 'cmi': 25, 'td': 15, 'tp': 5},
    {'code': 'MAT1111', 'intitule': 'Mathématique — Analyse Mathématique', 'credits': 3, 'niveau': 'L1S1', 'cmi': 25, 'td': 15, 'tp': 5},
    {'code': 'AMP1111', 'intitule': 'Algorithme et méthode de programmation 1 — Algorithme 1', 'credits': 2, 'niveau': 'L1S1', 'cmi': 30, 'td': 10, 'tp': 10},
    {'code': 'AMP1111', 'intitule': 'Algorithme — Méthode de programmation (Visual Basic)', 'credits': 2, 'niveau': 'L1S1', 'cmi': 20, 'td': 15, 'tp': 15},
    {'code': 'PHO1111', 'intitule': 'Phonétique et Orthophonie', 'credits': 3, 'niveau': 'L1S1', 'cmi': 25, 'td': 10, 'tp': 15},

    # L1 Semestre 2
    {'code': 'SDI1121', 'intitule': 'Statistique Descriptive et Inférentielle', 'credits': 3, 'niveau': 'L1S2', 'cmi': 30, 'td': 10, 'tp': 15},
    {'code': 'DCA1121', 'intitule': 'Droit du Travail', 'credits': 1, 'niveau': 'L1S2', 'cmi': 10, 'td': 0, 'tp': 5},
    {'code': 'DCA1121', 'intitule': 'Comptabilité Analytique', 'credits': 3, 'niveau': 'L1S2', 'cmi': 25, 'td': 10, 'tp': 15},
    {'code': 'SIN1121', 'intitule': 'Systèmes Informatiques — Architecture des ordinateurs', 'credits': 2, 'niveau': 'L1S2', 'cmi': 15, 'td': 5, 'tp': 25},
    {'code': 'SIN1121', 'intitule': 'Systèmes Informatiques — Systèmes d\'exploitation', 'credits': 2, 'niveau': 'L1S2', 'cmi': 15, 'td': 5, 'tp': 25},
    {'code': 'LAP1121', 'intitule': 'Langage de Programmation — Langage C', 'credits': 2, 'niveau': 'L1S2', 'cmi': 15, 'td': 10, 'tp': 20},
    {'code': 'LAP1121', 'intitule': 'Langage de Programmation — Langage Java', 'credits': 2, 'niveau': 'L1S2', 'cmi': 15, 'td': 10, 'tp': 20},
    {'code': 'PRW1121', 'intitule': 'Programmation Web 1', 'credits': 3, 'niveau': 'L1S2', 'cmi': 30, 'td': 10, 'tp': 5},
    {'code': 'ICA1121', 'intitule': 'Anglais 1 — Idioms et conversation', 'credits': 3, 'niveau': 'L1S2', 'cmi': 25, 'td': 10, 'tp': 10},
    {'code': 'ICA1121', 'intitule': 'Anglais 2', 'credits': 3, 'niveau': 'L1S2', 'cmi': 25, 'td': 10, 'tp': 10},
    {'code': 'GTR1121', 'intitule': 'Grammaire Anglaise', 'credits': 3, 'niveau': 'L1S2', 'cmi': 20, 'td': 10, 'tp': 20},
    {'code': 'GTR1121', 'intitule': 'Rédaction Anglaise', 'credits': 3, 'niveau': 'L1S2', 'cmi': 25, 'td': 10, 'tp': 10},

    # L2 Semestre 3
    {'code': 'MNG1231', 'intitule': 'Management — Introduction au management des organisations', 'credits': 1, 'niveau': 'L2S3', 'cmi': 10, 'td': 0, 'tp': 5},
    {'code': 'MNG1231', 'intitule': 'Management — Introduction à la comptabilité des sociétés', 'credits': 1, 'niveau': 'L2S3', 'cmi': 10, 'td': 0, 'tp': 5},
    {'code': 'AMP1231', 'intitule': 'Algorithme — Algorithme et Structure des Données', 'credits': 2, 'niveau': 'L2S3', 'cmi': 20, 'td': 5, 'tp': 5},
    {'code': 'AMP1231', 'intitule': 'Algorithme — Langage de Programmation 2', 'credits': 2, 'niveau': 'L2S3', 'cmi': 15, 'td': 5, 'tp': 10},
    {'code': 'PRW1232', 'intitule': 'Programmation Web 2', 'credits': 3, 'niveau': 'L2S3', 'cmi': 40, 'td': 10, 'tp': 10},
    {'code': 'AAI1231', 'intitule': 'Anglais des Affaires 1', 'credits': 1, 'niveau': 'L2S3', 'cmi': 10, 'td': 5, 'tp': 0},
    {'code': 'AAI1231', 'intitule': 'Anglais Informatique 1', 'credits': 2, 'niveau': 'L2S3', 'cmi': 20, 'td': 5, 'tp': 5},
    {'code': 'MAT1232', 'intitule': 'Mathématiques 2 — Intégrales et Équations Différentielles', 'credits': 3, 'niveau': 'L2S3', 'cmi': 25, 'td': 5, 'tp': 5},
    {'code': 'MAT1232', 'intitule': 'Mathématiques 2 — Analyse Mathématique 2', 'credits': 3, 'niveau': 'L2S3', 'cmi': 25, 'td': 5, 'tp': 5},
    {'code': 'MAB1231', 'intitule': 'Méthode d\'Analyse Informatique', 'credits': 3, 'niveau': 'L2S3', 'cmi': 25, 'td': 15, 'tp': 5},
    {'code': 'MAB1231', 'intitule': 'Base de Données', 'credits': 2, 'niveau': 'L2S3', 'cmi': 20, 'td': 10, 'tp': 5},
    {'code': 'RTS1231', 'intitule': 'Réseau Informatique', 'credits': 3, 'niveau': 'L2S3', 'cmi': 25, 'td': 10, 'tp': 10},
    {'code': 'RTS1231', 'intitule': 'Télécommunication et Sécurité Informatique', 'credits': 3, 'niveau': 'L2S3', 'cmi': 25, 'td': 10, 'tp': 10},

    # L2 Semestre 4
    {'code': 'ROP1241', 'intitule': 'Recherche Opérationnelle', 'credits': 3, 'niveau': 'L2S4', 'cmi': 20, 'td': 20, 'tp': 5},
    {'code': 'BDC1241', 'intitule': 'Base de Données Réparties', 'credits': 2, 'niveau': 'L2S4', 'cmi': 15, 'td': 5, 'tp': 5},
    {'code': 'BDC1241', 'intitule': 'Conception des Systèmes d\'Information', 'credits': 2, 'niveau': 'L2S4', 'cmi': 15, 'td': 5, 'tp': 5},
    {'code': 'ARA1241', 'intitule': 'Administration Réseau sous Windows et Linux', 'credits': 3, 'niveau': 'L2S4', 'cmi': 15, 'td': 15, 'tp': 10},
    {'code': 'ARA1241', 'intitule': 'Architecture et Téléinformatique', 'credits': 3, 'niveau': 'L2S4', 'cmi': 15, 'td': 15, 'tp': 10},
    {'code': 'GLR1241', 'intitule': 'Génie Logiciel', 'credits': 3, 'niveau': 'L2S4', 'cmi': 15, 'td': 15, 'tp': 10},
    {'code': 'GLR1241', 'intitule': 'Conception des Réseaux Informatiques', 'credits': 3, 'niveau': 'L2S4', 'cmi': 15, 'td': 15, 'tp': 10},
    {'code': 'DAM1241', 'intitule': 'Développement d\'Application Desktop 1', 'credits': 4, 'niveau': 'L2S4', 'cmi': 15, 'td': 20, 'tp': 10},
    {'code': 'DAM1241', 'intitule': 'Développement d\'Application Mobile 1', 'credits': 4, 'niveau': 'L2S4', 'cmi': 15, 'td': 5, 'tp': 10},
    {'code': 'AAI1241', 'intitule': 'Anglais des Affaires 2', 'credits': 2, 'niveau': 'L2S4', 'cmi': 15, 'td': 5, 'tp': 5},
    {'code': 'AAI1241', 'intitule': 'Anglais Informatique 2', 'credits': 1, 'niveau': 'L2S4', 'cmi': 10, 'td': 0, 'tp': 5},
]


class Command(BaseCommand):
    help = 'Initialise les cours IGAF depuis le programme officiel UOB'

    def handle(self, *args, **options):
        created = 0
        for data in COURS_DATA:
            obj, was_created = Cours.objects.get_or_create(
                code=data['code'],
                intitule=data['intitule'],
                niveau=data['niveau'],
                defaults={
                    'credits': data['credits'],
                    'cmi': data['cmi'],
                    'td': data['td'],
                    'tp': data['tp'],
                }
            )
            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f'{created} cours créés. Total: {Cours.objects.count()} cours.'))
