import io
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, Image)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from django.utils import timezone

CEREBRO_BLUE = colors.HexColor('#1e90ff')
CEREBRO_DARK = colors.HexColor('#0a0a0f')
CEREBRO_GRAY = colors.HexColor('#1a1a2e')
CEREBRO_LIGHT_GRAY = colors.HexColor('#2d2d44')
CEREBRO_WHITE = colors.white
CEREBRO_RED = colors.HexColor('#e74c3c')
CEREBRO_ORANGE = colors.HexColor('#f39c12')
CEREBRO_GREEN = colors.HexColor('#2ecc71')


def get_logo_path():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, 'static', 'img', 'cerebro_logo.png')


def add_header(elements, styles, title):
    logo_path = get_logo_path()
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=2*cm, height=2*cm)
        header_data = [[logo, Paragraph(f'<font color="#1e90ff"><b>CEREBRO</b></font>', styles['Title']),
                        Paragraph('<font color="#888888" size="8">Know where you fail</font>', styles['Normal'])]]
        header_table = Table(header_data, colWidths=[2.5*cm, 10*cm, 5*cm])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), CEREBRO_GRAY),
            ('TEXTCOLOR', (0, 0), (-1, -1), CEREBRO_WHITE),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(header_table)
    else:
        title_para = Paragraph('<font color="#1e90ff"><b>CEREBRO</b></font>', styles['Title'])
        elements.append(title_para)

    elements.append(Spacer(1, 0.3*cm))
    elements.append(HRFlowable(width="100%", thickness=2, color=CEREBRO_BLUE))
    elements.append(Spacer(1, 0.3*cm))
    page_title = Paragraph(f'<b>{title}</b>', styles['Heading1'])
    elements.append(page_title)
    elements.append(Spacer(1, 0.3*cm))


def add_footer_text(elements, styles):
    elements.append(Spacer(1, 0.5*cm))
    elements.append(HRFlowable(width="100%", thickness=1, color=CEREBRO_LIGHT_GRAY))
    elements.append(Spacer(1, 0.2*cm))
    footer = Paragraph(
        '<font color="#888888" size="8">Cerebro 2026 — Developed by Siméon Birindwa (Chrisim) | chrisim.net | Know where you fail</font>',
        styles['Normal']
    )
    footer.style.alignment = TA_CENTER
    elements.append(footer)


def generer_pdf_revision(session, planning, recommandations):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm
    )

    styles = getSampleStyleSheet()
    styles['Title'].textColor = CEREBRO_BLUE
    styles['Title'].fontSize = 18
    styles['Heading1'].textColor = CEREBRO_WHITE
    styles['Heading1'].fontSize = 14
    styles['Normal'].textColor = CEREBRO_WHITE
    styles['Normal'].fontSize = 10

    elements = []
    add_header(elements, styles, 'Plan de Révision Personnalisé')

    user = session.utilisateur
    nom_complet = user.get_full_name() or user.username
    date_gen = timezone.now().strftime('%d/%m/%Y à %H:%M')
    info_data = [
        ['Étudiant', nom_complet],
        ['Cours', session.cours.intitule],
        ['Crédits', f"{session.cours.credits} crédits"],
        ['Note actuelle', f"{session.note_actuelle}/20"],
        ['Note cible', f"{session.note_cible}/20"],
        ['Difficulté', f"{session.difficulte}/5"],
        ['Urgence', f"{session.urgence}/5"],
        ['Heures dispo/semaine', f"{session.heures_par_semaine}h"],
        ['Généré le', date_gen],
    ]
    info_table = Table(info_data, colWidths=[6*cm, 11.5*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), CEREBRO_GRAY),
        ('BACKGROUND', (1, 0), (1, -1), CEREBRO_LIGHT_GRAY),
        ('TEXTCOLOR', (0, 0), (-1, -1), CEREBRO_WHITE),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, CEREBRO_BLUE),
        ('ROWBACKGROUNDS', (1, 0), (1, -1), [CEREBRO_LIGHT_GRAY, CEREBRO_GRAY]),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.5*cm))

    niveau_risque = session.get_niveau_risque()
    couleur_risque = CEREBRO_RED if niveau_risque == 'critique' else (CEREBRO_ORANGE if niveau_risque == 'eleve' else CEREBRO_GREEN)
    label_risque = 'CRITIQUE' if niveau_risque == 'critique' else ('ÉLEVÉ' if niveau_risque == 'eleve' else 'STABLE')
    risque_para = Paragraph(
        f'<font color="#{couleur_risque.hexval()[2:]}"><b>Niveau de risque : {label_risque}</b></font>',
        styles['Normal']
    )
    elements.append(risque_para)
    elements.append(Spacer(1, 0.3*cm))

    elements.append(Paragraph('<b>Planning Hebdomadaire Recommandé</b>', styles['Heading1']))
    elements.append(Spacer(1, 0.2*cm))

    planning_headers = [['Jour', 'Matière', 'Durée', 'Focus']]
    planning_rows = planning_headers + [
        [p['jour'], p['cours'][:30], f"{p['heures']}h", p['focus'][:40]]
        for p in planning
    ]
    planning_table = Table(planning_rows, colWidths=[2.5*cm, 5*cm, 2*cm, 8*cm])
    planning_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), CEREBRO_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), CEREBRO_WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (-1, -1), CEREBRO_LIGHT_GRAY),
        ('TEXTCOLOR', (0, 1), (-1, -1), CEREBRO_WHITE),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, CEREBRO_BLUE),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [CEREBRO_LIGHT_GRAY, CEREBRO_GRAY]),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
    ]))
    elements.append(planning_table)
    elements.append(Spacer(1, 0.5*cm))

    elements.append(Paragraph('<b>Recommandations Personnalisées</b>', styles['Heading1']))
    elements.append(Spacer(1, 0.2*cm))
    for i, rec in enumerate(recommandations, 1):
        rec_para = Paragraph(f'<font color="#1e90ff">▶</font> {rec}', styles['Normal'])
        elements.append(rec_para)
        elements.append(Spacer(1, 0.15*cm))

    add_footer_text(elements, styles)

    doc.build(elements)
    buffer.seek(0)
    return buffer


def generer_pdf_examens(session, cours_examens, timeline, recommandations):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm
    )

    styles = getSampleStyleSheet()
    styles['Title'].textColor = CEREBRO_BLUE
    styles['Title'].fontSize = 18
    styles['Heading1'].textColor = CEREBRO_WHITE
    styles['Heading1'].fontSize = 12
    styles['Normal'].textColor = CEREBRO_WHITE
    styles['Normal'].fontSize = 9

    elements = []
    add_header(elements, styles, f'Planning d\'Examens — {session.nom_session}')

    user = session.utilisateur
    nom_complet = user.get_full_name() or user.username
    info_data = [
        ['Étudiant', nom_complet],
        ['Session', session.nom_session],
        ['Heures dispo/semaine', f"{session.heures_par_semaine}h"],
        ['Nombre d\'examens', str(cours_examens.count())],
        ['Généré le', timezone.now().strftime('%d/%m/%Y à %H:%M')],
    ]
    info_table = Table(info_data, colWidths=[6*cm, 11.5*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), CEREBRO_GRAY),
        ('BACKGROUND', (1, 0), (1, -1), CEREBRO_LIGHT_GRAY),
        ('TEXTCOLOR', (0, 0), (-1, -1), CEREBRO_WHITE),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, CEREBRO_BLUE),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.5*cm))

    elements.append(Paragraph('<b>Calendrier des Examens</b>', styles['Heading1']))
    elements.append(Spacer(1, 0.2*cm))
    exam_headers = [['Cours', 'Date', 'J-', 'Note act.', 'Cible', 'Maîtrise', 'Risque', 'H/sem']]
    exam_rows = exam_headers
    for ce in cours_examens:
        niveau = ce.get_niveau_risque()
        label_r = 'CRIT.' if niveau == 'critique' else ('ÉLEVÉ' if niveau == 'eleve' else 'STABLE')
        exam_rows.append([
            ce.cours.intitule[:25],
            ce.date_examen.strftime('%d/%m/%Y'),
            str(ce.jours_restants()),
            f"{ce.note_actuelle}/20",
            f"{ce.note_cible}/20",
            f"{ce.maitrise}/5",
            label_r,
            f"{ce.get_heures_par_semaine()}h",
        ])

    col_widths = [4.5*cm, 2.5*cm, 1*cm, 1.8*cm, 1.5*cm, 2*cm, 1.8*cm, 1.5*cm]
    exam_table = Table(exam_rows, colWidths=col_widths)
    exam_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), CEREBRO_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), CEREBRO_WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (-1, -1), CEREBRO_LIGHT_GRAY),
        ('TEXTCOLOR', (0, 1), (-1, -1), CEREBRO_WHITE),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, CEREBRO_BLUE),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [CEREBRO_LIGHT_GRAY, CEREBRO_GRAY]),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    elements.append(exam_table)
    elements.append(Spacer(1, 0.5*cm))

    elements.append(Paragraph('<b>Recommandations</b>', styles['Heading1']))
    elements.append(Spacer(1, 0.2*cm))
    for rec in recommandations:
        rec_para = Paragraph(f'<font color="#1e90ff">▶</font> {rec}', styles['Normal'])
        elements.append(rec_para)
        elements.append(Spacer(1, 0.15*cm))

    add_footer_text(elements, styles)
    doc.build(elements)
    buffer.seek(0)
    return buffer
