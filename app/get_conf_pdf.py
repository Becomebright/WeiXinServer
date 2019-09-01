from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph,SimpleDocTemplate
from reportlab.lib import  colors
import os
from app import app


pdfmetrics.registerFont(TTFont('song', 'simsun.ttc'))
Style = getSampleStyleSheet()

def get_conf_pdf(conf):
    content = []

    title = Style['Title']
    title.fontName = 'song'

    info = Style['Normal']
    info.fontName = 'song'
    info.alignment = 1
    
    heading = Style['Normal']
    heading.fontName = 'song'
    heading.fontSize = 13
    heading.leading = 20
    
    bodytext = Style['BodyText']
    bodytext.fontName = 'song'
    bodytext.wordWrap = 'CJK'
    bodytext.firstLineIndent = 32

    content.append( Paragraph(conf.name, title) )

    start_date = conf.date
    end_date = start_date + conf.duration
    info_text = str(start_date.date()) + '    ' + str(start_date.time()) + ' ~ ' + str(end_date.time()) + "\n" + conf.host
    content.append( Paragraph(info_text, info ) )

    if conf.introduction is not None:
        content.append( Paragraph('会议简介', heading) )
        content.append( Paragraph(conf.introduction, bodytext) )

    if conf.guest_intro is not None:
        content.append( Paragraph('嘉宾介绍', heading) )
        content.append( Paragraph(conf.guest_intro, bodytext) )

    if conf.remark is not None:
        content.append( Paragraph('备注', heading) )
        content.append( Paragraph(conf.remark, bodytext) )
    
    filename = 'static/pdfs/' + str(conf.id) + '_' + conf.name + '.pdf'
    filename = os.path.join(app.root_path, filename)
    pdf = SimpleDocTemplate(filename)
    pdf.multiBuild(content)

    return filename