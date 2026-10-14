import os
import zipfile
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTREGABLES_DIR = os.path.join(BASE_DIR, "ENTREGABLES_TUTORIAL_04")


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))

        # Header (páginas > 1)
        if self._pageNumber > 1:
            self.drawString(54, 755, "Tutorial 04: Dockerización y Despliegue en AWS — Infraestructura Inmutable")
            self.drawRightString(612 - 54, 755, "TEIS / AdS 2026 | Prof. Nicolás Ramírez Vélez")
            self.setStrokeColor(colors.HexColor("#CBD5E0"))
            self.setLineWidth(0.5)
            self.line(54, 747, 612 - 54, 747)

        # Footer
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(54, 45, 612 - 54, 45)
        self.drawString(54, 32, "Estudiante: Adyuer de Jesús Ojeda Badel — Universidad de Córdoba")
        self.drawRightString(612 - 54, 32, f"Página {self._pageNumber} de {page_count}")
        self.restoreState()


def build_pdf(filename):
    pdf = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    primary_color = colors.HexColor("#1A365D")
    secondary_color = colors.HexColor("#2B6CB0")
    dark_text = colors.HexColor("#2D3748")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=17,
        leading=21,
        textColor=primary_color,
        spaceAfter=3
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=secondary_color,
        spaceAfter=8
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=primary_color,
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=secondary_color,
        spaceBefore=5,
        spaceAfter=2,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.3,
        leading=11.5,
        textColor=dark_text,
        spaceAfter=4
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.8,
        leading=10,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=dark_text
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=dark_text
    )

    elements = []

    # Encabezado
    elements.append(Paragraph("TUTORIAL 04: DOCKERIZACIÓN Y DESPLIEGUE EN AWS", title_style))
    elements.append(Paragraph("De Localhost a la Nube: Infraestructura Inmutable con Docker Compose y EC2", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=1, spaceAfter=6))

    # Ficha de Metadatos
    info_data = [
        [
            Paragraph("<b>Estudiante:</b>", table_cell_bold),
            Paragraph("Adyuer de Jesús Ojeda Badel", table_cell_style),
            Paragraph("<b>Docente:</b>", table_cell_bold),
            Paragraph("Prof. Nicolás Ramírez Vélez", table_cell_style)
        ],
        [
            Paragraph("<b>Curso / Programa:</b>", table_cell_bold),
            Paragraph("Arquitectura de Software / TEIS 2026", table_cell_style),
            Paragraph("<b>Institución:</b>", table_cell_bold),
            Paragraph("Universidad de Córdoba", table_cell_style)
        ],
        [
            Paragraph("<b>Repositorio GitHub:</b>", table_cell_bold),
            Paragraph('<font color="#2B6CB0"><u>https://github.com/AdyuerHack/tutorial04-docker-aws</u></font>', table_cell_style),
            Paragraph("<b>Instancia AWS EC2:</b>", table_cell_bold),
            Paragraph("i-030ef8332d1155af6 (Servidor-Django)", table_cell_style)
        ],
        [
            Paragraph("<b>IP Pública EC2:</b>", table_cell_bold),
            Paragraph("<b>18.212.146.223</b> (Puerto 8000)", table_cell_style),
            Paragraph("<b>Endpoint Validado:</b>", table_cell_bold),
            Paragraph('<font color="#2B6CB0"><u>http://18.212.146.223:8000/api/v1/comprar/</u></font>', table_cell_style)
        ]
    ]

    t_info = Table(info_data, colWidths=[90, 162, 90, 162])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#EDF2F7")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(t_info)
    elements.append(Spacer(1, 7))

    # Resumen Arquitectónico
    elements.append(Paragraph("1. Arquitectura de la Solución e Infraestructura Inmutable", h1_style))
    elements.append(Paragraph(
        "En este laboratorio se elevó la arquitectura de la aplicación <b>Tienda API</b> (creada con Django REST Framework y Service Layer en el Tutorial 03) a un esquema de infraestructura contenerizada e inmutable. El sistema fue orquestado con <b>Docker Compose</b> y desplegado en una máquina virtual <b>AWS EC2 (Amazon Linux 2023 AMI, t2.micro)</b> provista en AWS Academy Learner Lab.",
        body_style
    ))

    arch_data = [
        [
            Paragraph("Componente", table_header_style),
            Paragraph("Tecnología / Imagen", table_header_style),
            Paragraph("Rol y Especificación Técnica", table_header_style)
        ],
        [
            Paragraph("<b>Backend Web</b>", table_cell_bold),
            Paragraph("python:3.11-slim", table_cell_style),
            Paragraph("API REST Django + DRF, expuesta en puerto 0.0.0.0:8000. Desacoplada de credenciales mediante variables de entorno (12-Factor App).", table_cell_style)
        ],
        [
            Paragraph("<b>Base de Datos</b>", table_cell_bold),
            Paragraph("postgres:15", table_cell_style),
            Paragraph("Motor relacional PostgreSQL aislado en red interna, persistido mediante volumen nominal <i>postgres_data</i>.", table_cell_style)
        ],
        [
            Paragraph("<b>Orquestación</b>", table_cell_bold),
            Paragraph("Docker Compose", table_cell_style),
            Paragraph("Red bridge privada, dependencias entre servicios (<i>depends_on: db</i>) y mapeo de puerto 8000:8000 al exterior.", table_cell_style)
        ],
        [
            Paragraph("<b>Seguridad Cloud</b>", table_cell_bold),
            Paragraph("AWS Security Group", table_cell_style),
            Paragraph("Regla de entrada Custom TCP 8000 (0.0.0.0/0) para habilitar el consumo del API desde Internet.", table_cell_style)
        ]
    ]

    t_arch = Table(arch_data, colWidths=[100, 110, 294])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(t_arch)
    elements.append(Spacer(1, 7))

    # Sección de Validación: Captura 1
    elements.append(Paragraph("2. Evidencias de Validación en la Nube (AWS EC2)", h1_style))
    elements.append(Paragraph("<b>Evidencia 1: Consumo del Endpoint API en Navegador (Browsable API DRF - HTTP 200 OK)</b>", h2_style))
    elements.append(Paragraph(
        "Acceso directo a la URL pública: <code>http://18.212.146.223:8000/api/v1/comprar/</code> servida por el contenedor de Django en AWS:",
        body_style
    ))

    img1_path = os.path.join(ENTREGABLES_DIR, "captura_aws_ec2_browsable.png")
    if os.path.exists(img1_path):
        elements.append(RLImage(img1_path, width=504, height=230))
        elements.append(Spacer(1, 4))

    elements.append(PageBreak())

    # Página 2: Evidencias 2 y 3 + Conclusiones
    elements.append(Paragraph("<b>Evidencia 2: Respuesta JSON Cruda (?format=json)</b>", h2_style))
    elements.append(Paragraph(
        "Validación de payload JSON devuelto directamente por la API REST en <code>http://18.212.146.223:8000/api/v1/comprar/?format=json</code>:",
        body_style
    ))

    img2_path = os.path.join(ENTREGABLES_DIR, "captura_aws_ec2_json.png")
    if os.path.exists(img2_path):
        elements.append(RLImage(img2_path, width=504, height=140))
        elements.append(Spacer(1, 6))

    elements.append(Paragraph("<b>Evidencia 3: Configuración de Red en AWS (Security Group - Puerto 8000 Abierto)</b>", h2_style))
    elements.append(Paragraph(
        "Regla de entrada configurada en la consola de AWS EC2 (puerto TCP 8000 expuesto al mundo 0.0.0.0/0):",
        body_style
    ))

    img3_path = os.path.join(ENTREGABLES_DIR, "captura_aws_security_groups.png")
    if os.path.exists(img3_path):
        elements.append(RLImage(img3_path, width=504, height=140))
        elements.append(Spacer(1, 8))

    # Conclusiones Técnicas
    elements.append(Paragraph("3. Reflexión y Respuestas Técnicas de Arquitectura", h1_style))
    conclusiones = [
        "<b>1. Infraestructura Inmutable y Paridad Dev/Prod:</b> Gracias a Docker, el entorno de ejecución es exactamente idéntico en la laptop de desarrollo y en la máquina virtual de AWS EC2. Se elimina por completo el antipatrón '<i>en mi máquina sí funciona</i>'.",
        "<b>2. Principios Twelve-Factor App:</b> La refactorización de <code>settings.py</code> para consumir variables de entorno (<code>DB_NAME</code>, <code>DB_USER</code>, <code>DB_PASSWORD</code>, <code>DB_HOST</code>, <code>DB_PORT</code>) desacopla la configuración del código fuente, permitiendo desplegar la misma imagen en múltiples entornos sin modificar código.",
        "<b>3. Persistencia vs. Estado Efímero:</b> La base de datos PostgreSQL almacena sus tablas y datos en el volumen nominal persistente <code>postgres_data</code>. Aunque los contenedores se reinicien, destruyan o actualicen, la información no se pierde.",
        "<b>4. Seguridad en Capas:</b> La base de datos PostgreSQL no se expone a Internet en el Security Group de AWS; solo vive dentro de la red interna de Docker, comunicándose exclusivamente con el servicio <code>web</code> mediante DNS interno."
    ]

    for item in conclusiones:
        elements.append(Paragraph(f"• {item}", body_style))

    pdf.build(elements, canvasmaker=NumberedCanvas)
    print(f"[OK] PDF generado: {filename}")


def make_zip(zip_filename, pdf_filename):
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as z:
        # Añadir PDF
        if os.path.exists(pdf_filename):
            z.write(pdf_filename, os.path.basename(pdf_filename))
        
        # Añadir capturas
        for f in os.listdir(ENTREGABLES_DIR):
            if f.endswith('.png'):
                full_p = os.path.join(ENTREGABLES_DIR, f)
                z.write(full_p, os.path.join("capturas", f))
                
        # Añadir código clave
        z.write(os.path.join(BASE_DIR, "Dockerfile"), "Dockerfile")
        z.write(os.path.join(BASE_DIR, "docker-compose.yml"), "docker-compose.yml")
        z.write(os.path.join(BASE_DIR, "requirements.txt"), "requirements.txt")
        z.write(os.path.join(BASE_DIR, "deploy_aws.sh"), "deploy_aws.sh")
        z.write(os.path.join(BASE_DIR, "README.md"), "README.md")
        z.write(os.path.join(BASE_DIR, "Tienda", "settings.py"), os.path.join("Tienda", "settings.py"))

    print(f"[OK] ZIP generado: {zip_filename}")


if __name__ == "__main__":
    pdf_out = os.path.join(ENTREGABLES_DIR, "Entrega_Tutorial_04_Adyuer_Ojeda.pdf")
    root_pdf_out = os.path.join(BASE_DIR, "Entrega_Tutorial_04_Adyuer_Ojeda.pdf")
    zip_out = os.path.join(ENTREGABLES_DIR, "Entrega_Tutorial_04_Adyuer_Ojeda.zip")
    root_zip_out = os.path.join(BASE_DIR, "entrega_tutorial04_Adyuer_Ojeda.zip")

    build_pdf(pdf_out)
    # Copiar a raiz tambien para facilidad de acceso
    import shutil
    shutil.copy2(pdf_out, root_pdf_out)

    make_zip(zip_out, pdf_out)
    shutil.copy2(zip_out, root_zip_out)
