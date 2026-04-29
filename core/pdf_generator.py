import io
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, Image, KeepTogether)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from django.utils import timezone

CEREBRO_BLUE = colors.HexColor('#1e90ff')
CEREBRO_DARK = colors.HexColor('#07070d')
CEREBRO_NAVY = colors.HexColor('#0d0d1f')
CEREBRO_CARD = colors.HexColor('#0f0f1a')
CEREBRO_CARD2 = colors.HexColor('#141424')
CEREBRO_BORDER = colors.HexColor('#1e1e35')
CEREBRO_WHITE = colors.HexColor('#ffffff')
CEREBRO_GRAY_TEXT = colors.HexColor('#9999bb')
CEREBRO_RED = colors.HexColor('#e74c3c')
CEREBRO_ORANGE = colors.HexColor('#f39c12')
CEREBRO_GREEN = colors.HexColor('#2ecc71')
CEREBRO_LIGHT_BLUE = colors.HexColor('#4da6ff')


def get_logo_path():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, 'static', 'img', 'cerebro_logo.png')


def _build_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='CerebroTitle',
        fontSize=22,
        fontName='Helvetica-Bold',
        textColor=CEREBRO_BLUE,
        spaceAfter=4,
        leading=28,
    ))
    styles.add(ParagraphStyle(
        name='CerebroSubtitle',
        fontSize=11,
        fontName='Helvetica',
        textColor=CEREBRO_GRAY_TEXT,
        spaceAfter=0,
    ))
    styles.add(ParagraphStyle(
        name='CerebroSection',
        fontSize=11,
        fontName='Helvetica-Bold',
        textColor=CEREBRO_BLUE,
        spaceBefore=14,
        spaceAfter=6,
        borderPad=4,
    ))
    styles.add(ParagraphStyle(
        name='CerebroBody',
        fontSize=9,
        fontName='Helvetica',
        textColor=CEREBRO_WHITE,
        spaceAfter=4,
        leading=14,
    ))
    styles.add(ParagraphStyle(
        name='CerebroSmall',
        fontSize=8,
        fontName='Helvetica',
        textColor=CEREBRO_GRAY_TEXT,
        spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        name='CerebroCenter',
        fontSize=9,
        fontName='Helvetica',
        textColor=CEREBRO_WHITE,
        alignment=TA_CENTER,
    ))

    return styles


def _add_page_header(elements, styles, titre_doc, user_name, date_gen):
    logo_path = get_logo_path()

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=1.6*cm, height=1.6*cm)
    else:
        logo = Paragraph('', styles['CerebroBody'])

    title_para = Paragraph('<font color="#1e90ff"><b>CEREBRO</b></font>', styles['CerebroTitle'])
    tagline_para = Paragraph('Know where you fail', styles['CerebroSubtitle'])

    header_right_data = [[title_para], [tagline_para]]
    header_right = Table(header_right_data, colWidths=[10*cm])
    header_right.setStyle(TableStyle([('LEFTPADDING', (0,0), (-1,-1), 0),
                                       ('RIGHTPADDING', (0,0), (-1,-1), 0),
                                       ('TOPPADDING', (0,0), (-1,-1), 0),
                                       ('BOTTOMPADDING', (0,0), (-1,-1), 2)]))

    user_para = Paragraph(f'<font color="#9999bb">Étudiant :</font> <b>{user_name}</b>', styles['CerebroBody'])
    date_para = Paragraph(f'<font color="#9999bb">Généré le :</font> {date_gen}', styles['CerebroSmall'])
    header_right2_data = [[user_para], [date_para]]
    header_right2 = Table(header_right2_data, colWidths=[6*cm])
    header_right2.setStyle(TableStyle([('LEFTPADDING', (0,0), (-1,-1), 0),
                                        ('ALIGN', (0,0), (-1,-1), 'RIGHT')]))

    banner_data = [[logo, header_right, header_right2]]
    banner = Table(banner_data, colWidths=[2*cm, 10*cm, 6*cm])
    banner.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CEREBRO_CARD),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('ROUNDEDCORNERS', [4, 4, 4, 4]),
    ]))
    elements.append(banner)
    elements.append(Spacer(1, 0.3*cm))

    elements.append(HRFlowable(width="100%", thickness=2, color=CEREBRO_BLUE))
    elements.append(Spacer(1, 0.2*cm))

    doc_title = Paragraph(f'<b>{titre_doc}</b>', ParagraphStyle(
        'DocTitle', fontSize=13, fontName='Helvetica-Bold',
        textColor=CEREBRO_WHITE, spaceAfter=4
    ))
    elements.append(doc_title)
    elements.append(Spacer(1, 0.3*cm))


def _get_signature_path():
    try:
        from core.models import CreateurProfil
        cp = CreateurProfil.objects.filter(signature__isnull=False).exclude(signature='').first()
        if cp and cp.signature:
            return cp.signature.path
    except Exception:
        pass
    return None


def _add_footer(elements, styles):
    elements.append(Spacer(1, 0.6*cm))
    elements.append(HRFlowable(width="100%", thickness=1, color=CEREBRO_BORDER))
    elements.append(Spacer(1, 0.3*cm))

    sig_path = _get_signature_path()

    if sig_path and os.path.exists(sig_path):
        sig_img = Image(sig_path, width=3.5*cm, height=1.4*cm)
        sig_img.hAlign = 'RIGHT'

        sig_block_data = [[
            Paragraph(
                '<font color="#9999bb" size="7">Siméon Birindwa (Chrisim)</font><br/>'
                '<font color="#9999bb" size="6">Cerebro Creator | chrisim.net</font>',
                ParagraphStyle('SigName', fontSize=7, fontName='Helvetica',
                               textColor=CEREBRO_GRAY_TEXT, alignment=TA_RIGHT, leading=10)
            ),
            sig_img,
        ]]
        sig_block = Table(sig_block_data, colWidths=[6*cm, 3.8*cm])
        sig_block.setStyle(TableStyle([
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ]))

        footer_data = [[
            Paragraph(
                '<font color="#9999bb" size="7">Cerebro 2026 — Université Officielle de Bukavu (UOB) — IGAF</font>',
                styles['CerebroSmall']
            ),
            sig_block,
        ]]
        footer_table = Table(footer_data, colWidths=[8.2*cm, 10*cm])
    else:
        footer_data = [[
            Paragraph(
                '<font color="#9999bb" size="7">Cerebro 2026 — Université Officielle de Bukavu (UOB) — IGAF</font>',
                styles['CerebroSmall']
            ),
            Paragraph(
                '<font color="#9999bb" size="7">Siméon Birindwa (Chrisim) — Cerebro Creator | chrisim.net</font>',
                ParagraphStyle('FooterR', fontSize=7, fontName='Helvetica',
                               textColor=CEREBRO_GRAY_TEXT, alignment=TA_RIGHT)
            ),
        ]]
        footer_table = Table(footer_data, colWidths=[9*cm, 9*cm])

    footer_table.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
    ]))
    elements.append(footer_table)


def _risque_style(niveau):
    if niveau == 'critique':
        return CEREBRO_RED, 'CRITIQUE'
    elif niveau == 'eleve':
        return CEREBRO_ORANGE, 'ÉLEVÉ'
    else:
        return CEREBRO_GREEN, 'STABLE'


def _score_bar(score, max_score=100, width=5*cm):
    pct = min(100, max(0, score)) / 100
    color = CEREBRO_GREEN if score < 35 else (CEREBRO_ORANGE if score < 60 else CEREBRO_RED)
    bar_data = [['']]
    bar_bg = Table(bar_data, colWidths=[width])
    bar_bg.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CEREBRO_BORDER),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('ROWHEIGHT', (0,0), (-1,-1), 6),
    ]))
    bar_fill_data = [['']]
    bar_fill = Table(bar_fill_data, colWidths=[width * pct if pct > 0 else 0.01*cm])
    bar_fill.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), color),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('ROWHEIGHT', (0,0), (-1,-1), 6),
    ]))
    return bar_bg


def generer_pdf_revision(session, planning, recommandations):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=2*cm,
        title=f'Plan de révision — {session.cours.intitule}',
        author='Cerebro'
    )

    styles = _build_styles()
    elements = []

    user = session.utilisateur
    nom = user.get_full_name() or user.username
    date_gen = timezone.now().strftime('%d/%m/%Y à %H:%M')

    _add_page_header(elements, styles, 'Plan de Révision Personnalisé', nom, date_gen)

    niveau_risque = session.get_niveau_risque()
    score_priorite = session.get_score_priorite()
    color_risque, label_risque = _risque_style(niveau_risque)
    ecart = max(0, session.note_cible - session.note_actuelle)

    info_data = [
        ['Cours', session.cours.intitule, 'Crédits', f"{session.cours.credits} cr"],
        ['Note actuelle', f"{session.note_actuelle}/20", 'Note cible', f"{session.note_cible}/20"],
        ['Difficulté', f"{session.difficulte}/5", 'Urgence', f"{session.urgence}/5"],
        ['Heures dispo/sem.', f"{session.heures_par_semaine}h", 'Écart à combler', f"{ecart:.1f} pts"],
    ]
    info_table = Table(info_data, colWidths=[4*cm, 5.5*cm, 4*cm, 4.5*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), CEREBRO_CARD),
        ('BACKGROUND', (2, 0), (2, -1), CEREBRO_CARD),
        ('BACKGROUND', (1, 0), (1, -1), CEREBRO_CARD2),
        ('BACKGROUND', (3, 0), (3, -1), CEREBRO_CARD2),
        ('TEXTCOLOR', (0, 0), (-1, -1), CEREBRO_WHITE),
        ('TEXTCOLOR', (0, 0), (0, -1), CEREBRO_GRAY_TEXT),
        ('TEXTCOLOR', (2, 0), (2, -1), CEREBRO_GRAY_TEXT),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, CEREBRO_BORDER),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.4*cm))

    risque_data = [[
        Paragraph(f'Score de priorité : <b>{score_priorite}/100</b>', styles['CerebroBody']),
        Paragraph(f'Niveau de risque : <font color="#{color_risque.hexval()[2:]}"><b>{label_risque}</b></font>', styles['CerebroBody']),
        Paragraph(f'Heures recommandées : <b>{session.get_heures_recommandees_par_semaine()}h/sem</b>', styles['CerebroBody']),
    ]]
    risque_table = Table(risque_data, colWidths=[6*cm, 6*cm, 6*cm])
    risque_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), CEREBRO_NAVY),
        ('TEXTCOLOR', (0, 0), (-1, -1), CEREBRO_WHITE),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, CEREBRO_BLUE),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(risque_table)
    elements.append(Spacer(1, 0.4*cm))

    elements.append(Paragraph('Planning Hebdomadaire Recommandé', styles['CerebroSection']))
    plan_data = [['Jour', 'Matière', 'Durée', 'Focus pédagogique']]
    for p in planning:
        plan_data.append([
            Paragraph(f'<b>{p["jour"]}</b>', styles['CerebroBody']),
            Paragraph(p['cours'][:35], styles['CerebroBody']),
            Paragraph(f'<b>{p["heures"]}h</b>', styles['CerebroCenter']),
            Paragraph(p['focus'], styles['CerebroBody']),
        ])
    plan_table = Table(plan_data, colWidths=[2.2*cm, 5*cm, 1.8*cm, 9*cm])
    plan_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), CEREBRO_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), CEREBRO_WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [CEREBRO_CARD2, CEREBRO_CARD]),
        ('TEXTCOLOR', (0, 1), (-1, -1), CEREBRO_WHITE),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.3, CEREBRO_BORDER),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(plan_table)
    elements.append(Spacer(1, 0.4*cm))

    elements.append(Paragraph('Recommandations Personnalisées', styles['CerebroSection']))
    for i, rec in enumerate(recommandations, 1):
        rec_para = Paragraph(
            f'<font color="#1e90ff"><b>{i}.</b></font>  {rec}',
            styles['CerebroBody']
        )
        elements.append(rec_para)
        elements.append(Spacer(1, 0.1*cm))

    _add_footer(elements, styles)

    doc.build(elements)
    buffer.seek(0)
    return buffer


def generer_pdf_multi_revision(user, sessions, planning_multi, recommandations):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=2*cm,
        title='Analyse Multi-Cours — Cerebro',
        author='Cerebro'
    )

    styles = _build_styles()
    elements = []

    nom = user.get_full_name() or user.username
    date_gen = timezone.now().strftime('%d/%m/%Y à %H:%M')
    _add_page_header(elements, styles, f'Analyse Multi-Cours — {len(sessions)} matières', nom, date_gen)

    elements.append(Paragraph('Tableau de priorités', styles['CerebroSection']))
    prio_data = [['#', 'Cours', 'Crédits', 'Actuelle', 'Cible', 'Difficulté', 'H/sem', 'Score', 'Risque']]
    for i, s in enumerate(sessions, 1):
        color_r, label_r = _risque_style(s.get_niveau_risque())
        prio_data.append([
            str(i),
            Paragraph(s.cours.intitule[:28], styles['CerebroBody']),
            str(s.cours.credits),
            f"{s.note_actuelle}/20",
            f"{s.note_cible}/20",
            f"{s.difficulte}/5",
            f"{s.get_heures_recommandees_par_semaine()}h",
            f"{s.get_score_priorite()}",
            Paragraph(f'<font color="#{color_r.hexval()[2:]}"><b>{label_r}</b></font>', styles['CerebroBody']),
        ])

    prio_table = Table(prio_data, colWidths=[0.6*cm, 4.5*cm, 1.2*cm, 1.6*cm, 1.2*cm, 1.6*cm, 1.2*cm, 1.2*cm, 2*cm])
    prio_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), CEREBRO_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), CEREBRO_WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [CEREBRO_CARD2, CEREBRO_CARD]),
        ('TEXTCOLOR', (0, 1), (-1, -1), CEREBRO_WHITE),
        ('FONTSIZE', (0, 1), (-1, -1), 7.5),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.3, CEREBRO_BORDER),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(prio_table)
    elements.append(Spacer(1, 0.4*cm))

    elements.append(Paragraph('Planning Hebdomadaire Consolidé', styles['CerebroSection']))
    jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']
    timeline_data = [['Jour', 'Matières & Durées']]
    for jour in jours:
        entrees = planning_multi.get(jour, [])
        if entrees:
            contenu = '\n'.join([f"• {e['cours'][:30]} ({e['heures']}h)" for e in entrees])
        else:
            contenu = '—'
        timeline_data.append([
            Paragraph(f'<b>{jour}</b>', styles['CerebroBody']),
            Paragraph(contenu.replace('\n', '<br/>'), styles['CerebroBody']),
        ])
    timeline_table = Table(timeline_data, colWidths=[3*cm, 15*cm])
    timeline_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), CEREBRO_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), CEREBRO_WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [CEREBRO_CARD2, CEREBRO_CARD]),
        ('TEXTCOLOR', (0, 1), (-1, -1), CEREBRO_WHITE),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.3, CEREBRO_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(timeline_table)
    elements.append(Spacer(1, 0.4*cm))

    elements.append(Paragraph('Recommandations', styles['CerebroSection']))
    for i, rec in enumerate(recommandations, 1):
        rec_para = Paragraph(f'<font color="#1e90ff"><b>{i}.</b></font>  {rec}', styles['CerebroBody'])
        elements.append(rec_para)
        elements.append(Spacer(1, 0.1*cm))

    _add_footer(elements, styles)

    doc.build(elements)
    buffer.seek(0)
    return buffer


def generer_pdf_examens(session, cours_examens, timeline, recommandations):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=2*cm,
        title=f'Planning Examens — {session.nom_session}',
        author='Cerebro'
    )

    styles = _build_styles()
    elements = []

    user = session.utilisateur
    nom = user.get_full_name() or user.username
    date_gen = timezone.now().strftime('%d/%m/%Y à %H:%M')
    _add_page_header(elements, styles, f'Planning d\'Examens — {session.nom_session}', nom, date_gen)

    meta_data = [
        ['Session', session.nom_session, 'Heures disponibles', f"{session.heures_par_semaine}h/sem"],
        ['Nombre d\'examens', str(cours_examens.count()), 'Généré le', date_gen],
    ]
    meta_table = Table(meta_data, colWidths=[4*cm, 6*cm, 4*cm, 4*cm])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), CEREBRO_CARD),
        ('BACKGROUND', (2, 0), (2, -1), CEREBRO_CARD),
        ('BACKGROUND', (1, 0), (1, -1), CEREBRO_CARD2),
        ('BACKGROUND', (3, 0), (3, -1), CEREBRO_CARD2),
        ('TEXTCOLOR', (0, 0), (-1, -1), CEREBRO_WHITE),
        ('TEXTCOLOR', (0, 0), (0, -1), CEREBRO_GRAY_TEXT),
        ('TEXTCOLOR', (2, 0), (2, -1), CEREBRO_GRAY_TEXT),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, CEREBRO_BORDER),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 0.4*cm))

    elements.append(Paragraph('Calendrier des Examens', styles['CerebroSection']))
    exam_headers = [['Cours', 'Date', 'J-restants', 'Act.', 'Cible', 'Maîtrise', 'H/sem', 'Risque']]
    exam_rows = exam_headers
    for ce in cours_examens:
        color_r, label_r = _risque_style(ce.get_niveau_risque())
        exam_rows.append([
            Paragraph(ce.cours.intitule[:28], styles['CerebroBody']),
            ce.date_examen.strftime('%d/%m/%Y'),
            f"J-{ce.jours_restants()}",
            f"{ce.note_actuelle}/20",
            f"{ce.note_cible}/20",
            f"{ce.maitrise}/5",
            f"{ce.get_heures_par_semaine()}h",
            Paragraph(f'<font color="#{color_r.hexval()[2:]}"><b>{label_r}</b></font>', styles['CerebroBody']),
        ])

    col_widths = [4.5*cm, 2.3*cm, 1.8*cm, 1.6*cm, 1.5*cm, 1.8*cm, 1.5*cm, 2*cm]
    exam_table = Table(exam_rows, colWidths=col_widths)
    exam_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), CEREBRO_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), CEREBRO_WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [CEREBRO_CARD2, CEREBRO_CARD]),
        ('TEXTCOLOR', (0, 1), (-1, -1), CEREBRO_WHITE),
        ('FONTSIZE', (0, 1), (-1, -1), 7.5),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.3, CEREBRO_BORDER),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(exam_table)
    elements.append(Spacer(1, 0.4*cm))

    elements.append(Paragraph('Planning Hebdomadaire', styles['CerebroSection']))
    jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']
    timeline_data = [['Jour', 'Matières à réviser']]
    for jour in jours:
        entrees = timeline.get(jour, [])
        if entrees:
            contenu = '\n'.join([f"• {e['cours'][:28]} ({e['heures']}h) — J-{e['jours_restants']}" for e in entrees])
        else:
            contenu = 'Repos / révision libre'
        timeline_data.append([
            Paragraph(f'<b>{jour}</b>', styles['CerebroBody']),
            Paragraph(contenu.replace('\n', '<br/>'), styles['CerebroBody']),
        ])
    tl_table = Table(timeline_data, colWidths=[3*cm, 15*cm])
    tl_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), CEREBRO_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), CEREBRO_WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [CEREBRO_CARD2, CEREBRO_CARD]),
        ('TEXTCOLOR', (0, 1), (-1, -1), CEREBRO_WHITE),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.3, CEREBRO_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(tl_table)
    elements.append(Spacer(1, 0.4*cm))

    elements.append(Paragraph('Recommandations', styles['CerebroSection']))
    for i, rec in enumerate(recommandations, 1):
        rec_para = Paragraph(f'<font color="#1e90ff"><b>{i}.</b></font>  {rec}', styles['CerebroBody'])
        elements.append(rec_para)
        elements.append(Spacer(1, 0.1*cm))

    _add_footer(elements, styles)
    doc.build(elements)
    buffer.seek(0)
    return buffer
