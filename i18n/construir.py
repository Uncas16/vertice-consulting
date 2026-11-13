# Construye el sitio publicado a partir de la fuente única _fuente/sitio.html (español).
#
#   python3 i18n/construir.py
#
# Genera 4 páginas (index, servicios, nosotros, contacto) en español en la raíz,
# y sus versiones en en/ y pt/ usando la tabla i18n/traducciones.py (T = {es: (en, pt)}).
# Para cambiar un texto: editar _fuente/sitio.html, agregar la traducción en traducciones.py
# y volver a ejecutar este script. No editar a mano los .html generados.
import re, sys, os, html
from urllib.parse import quote
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from traducciones import T
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://uncas16.github.io/vertice-consulting/'
LANGS = ['es', 'en', 'pt']

# Páginas: archivo -> bloques de la fuente (por su comentario <!-- NOMBRE -->), en orden
PAGES = [
    ('index.html',     ['HERO', 'CLIENTES', 'RESUMEN', 'RESULTADOS', 'CTA']),
    ('servicios.html', ['SERVICIOS', 'COMO TRABAJAMOS', 'CTA']),
    ('nosotros.html',  ['NOSOTROS', 'MISIÓN, VISIÓN Y VALORES', 'EQUIPO', 'TRAYECTORIA', 'CREDENCIALES', 'CTA']),
    ('contacto.html',  ['CONTACTO']),
]
META = {  # título y descripción por página (index usa los de la fuente)
    'servicios.html': {
        'es': ('Servicios', 'Catorce servicios en cinco frentes: estrategia y transformación, plataformas core y SAP, gobierno de programas, datos e IA, infraestructura y seguridad.'),
        'en': ('Services', 'Fourteen services across five fronts: strategy and transformation, core platforms and SAP, program governance, data and AI, infrastructure and security.'),
        'pt': ('Serviços', 'Catorze serviços em cinco frentes: estratégia e transformação, plataformas core e SAP, governança de programas, dados e IA, infraestrutura e segurança.')},
    'nosotros.html': {
        'es': ('Nosotros y equipo', 'Quiénes somos, misión, visión y valores, el equipo de Vértice Consulting, su trayectoria y credenciales.'),
        'en': ('About us and team', 'Who we are, mission, vision and values, the Vértice Consulting team, its track record and credentials.'),
        'pt': ('Sobre nós e equipe', 'Quem somos, missão, visão e valores, a equipe da Vértice Consulting, sua trajetória e credenciais.')},
    'contacto.html': {
        'es': ('Contacto', 'Contanos el desafío que estás enfrentando. Te respondemos en menos de 24 horas con una perspectiva inicial sin costo.'),
        'en': ('Contact', "Tell us about the challenge you're facing. We reply within 24 hours with an initial perspective at no cost."),
        'pt': ('Contato', 'Conte-nos o desafio que você está enfrentando. Respondemos em menos de 24 horas com uma perspectiva inicial sem custo.')},
}
WA = {'es': 'Hola%2C%20me%20interesa%20conocer%20m%C3%A1s%20sobre%20sus%20servicios%20de%20consultor%C3%ADa.',
      'en': 'Hi%2C%20I%27d%20like%20to%20learn%20more%20about%20your%20consulting%20services.',
      'pt': 'Ol%C3%A1%2C%20gostaria%20de%20saber%20mais%20sobre%20seus%20servi%C3%A7os%20de%20consultoria.'}

SRC = open(f'{ROOT}/_fuente/sitio.html', encoding='utf-8').read()

def ws(s):  # regex que tolera espacios/saltos de línea entre palabras
    return r'\s+'.join(re.escape(w) for w in s.split())

def translate(s, idx):
    if idx == 0:
        return s
    body_start = s.index('<body')
    keys = sorted(T, key=len, reverse=True)
    body = s[body_start:]
    stash = []
    def keep(m):
        stash.append(m.group(0)); return f'\x00{len(stash)-1}\x00'
    body = re.sub(r'<script.*?</script>|<svg.*?</svg>', keep, body, flags=re.S)
    for k in keys:
        v = T[k][idx-1]
        body = re.sub(r'(>\s*)' + ws(k) + r'(\s*<)', lambda m: m.group(1) + v + m.group(2), body)
        for attr in ('placeholder', 'aria-label', 'alt', 'data-servicio', 'title'):
            body = body.replace(f'{attr}="{k}"', f'{attr}="{v}"')
            body = body.replace(f'{attr}="{html.escape(k, quote=False)}"', f'{attr}="{html.escape(v, quote=False)}"')
    body = re.sub(r'\x00(\d+)\x00', lambda m: stash[int(m.group(1))], body)
    for k in keys:
        v = T[k][idx-1].replace("'", "\\'")
        body = body.replace(f"'{k}'", f"'{v}'")
    head = s[:body_start]
    for k in keys:
        v = T[k][idx-1]
        head = head.replace(f'<title>{k}</title>', f'<title>{v}</title>').replace(f'content="{k}"', f'content="{v}"')
        head = head.replace(f"content: '{k}'", f"content: '{v}'")
    return head + body

def split(s):
    a = s.index('<!-- HERO -->'); b = s.index('<!-- FOOTER -->')
    header, middle, tail = s[:a], s[a:b], s[b:]
    parts = re.split(r'^<!-- (.+?) -->\n', middle, flags=re.M)
    blocks = {parts[i]: parts[i+1] for i in range(1, len(parts), 2)}
    return header, blocks, tail

def page_url(lang, f):
    return BASE + ('' if lang == 'es' else lang + '/') + ('' if f == 'index.html' else f)

def build(lang):
    idx = LANGS.index(lang)
    s = translate(SRC, idx)
    header, blocks, tail = split(s)
    used = {n for _, ns in PAGES for n in ns}
    missing = set(blocks) - used
    assert not missing, f'bloques sin página: {missing}'
    # qué id vive en qué página, y cuál es el primero de cada página
    owner, first = {}, {}
    for f, names in PAGES:
        for n in names:
            if n == 'CTA':
                continue
            for i in re.findall(r'\sid="([^"]+)"', blocks[n]):
                owner.setdefault(i, f)
        first[f] = re.search(r'<section id="([^"]+)"', blocks[names[0]]).group(1)
    up = '' if lang == 'es' else '../'
    outs = {}
    for f, names in PAGES:
        body = ''.join(f'<!-- {n} -->\n' + blocks[n] for n in names)
        if f != 'index.html':
            body = re.sub(r'<section id="([^"]+)">', r'<section id="\1" class="page-first">', body, count=1)
        doc = header + body + tail
        # "Cotizar" -> contacto.html?servicio=...
        doc = re.sub(r'href="#contacto" class="service-quote" data-servicio="([^"]*)"',
                     lambda m: f'href="contacto.html?servicio={quote(html.unescape(m.group(1)))}" class="service-quote" data-servicio="{m.group(1)}"', doc)
        def link(m, nav=False):
            i = m.group(1); tgt = owner.get(i)
            if tgt is None:
                return m.group(0)
            if tgt == f:
                href = '#' + i
                cur = nav and i == first[f]
            else:
                href = ('./' if tgt == 'index.html' else tgt) + ('' if i == first[tgt] else '#' + i)
                cur = False
            return f'href="{href}"' + (' aria-current="page"' if cur else '')
        nav_a = doc.index('<ul class="nav-links"'); nav_b = doc.index('</ul>', nav_a)
        nav = re.sub(r'href="#([\w-]+)"', lambda m: link(m, True), doc[nav_a:nav_b])
        doc = doc[:nav_a] + nav + doc[nav_b:]
        doc = re.sub(r'href="#([\w-]+)"', link, doc)
        # metadatos por página
        if f in META:
            title, desc = META[f][lang]
            full = f'{title} · Vértice Consulting'
            doc = re.sub(r'<title>.*?</title>', f'<title>{full}</title>', doc, count=1)
            doc = re.sub(r'<meta property="og:title" content="[^"]*"/>', f'<meta property="og:title" content="{full}"/>', doc, count=1)
            doc = re.sub(r'<meta name="description" content="[^"]*"/>', f'<meta name="description" content="{desc}"/>', doc, count=1)
            doc = re.sub(r'<meta property="og:description" content="[^"]*"/>', f'<meta property="og:description" content="{desc}"/>', doc, count=1)
        doc = re.sub(r'<meta property="og:url" content="[^"]*"/>', f'<meta property="og:url" content="{page_url(lang, f)}"/>', doc, count=1)
        doc = re.sub(r'<link rel="alternate" hreflang="([\w-]+)" href="[^"]*"/>',
                     lambda m: f'<link rel="alternate" hreflang="{m.group(1)}" href="{page_url("es" if m.group(1) == "x-default" else m.group(1), f)}"/>', doc)
        fname = '' if f == 'index.html' else f
        def sw(m):
            items = []
            for L in LANGS:
                href = up + ('' if L == 'es' else L + '/') + fname
                href = href or './'
                items.append(f'<a href="{href}" lang="{L}"' + (' aria-current="page"' if L == lang else '') + f'>{L.upper()}</a>')
            return m.group(1) + ''.join(items) + '</div>'
        doc = re.sub(r'(<div class="lang" role="group" aria-label="[^"]*">).*?</div>', sw, doc, count=1, flags=re.S)
        if lang != 'es':
            doc = doc.replace('<html lang="es">', f'<html lang="{lang}">', 1)
            doc = doc.replace('content="es_CL"', 'content="' + {'en': 'en_US', 'pt': 'pt_BR'}[lang] + '"', 1)
            doc = doc.replace('src="img/', 'src="../img/').replace('url("img/', 'url("../img/')
            doc = doc.replace('text=' + WA['es'], 'text=' + WA[lang])
        d = ROOT if lang == 'es' else f'{ROOT}/{lang}'
        os.makedirs(d, exist_ok=True)
        open(f'{d}/{f}', 'w', encoding='utf-8').write(
            '<!-- Generado por i18n/construir.py desde _fuente/sitio.html; no editar a mano. -->\n' + doc)
        outs[f] = doc
    return outs

for lang in LANGS:
    outs = build(lang)
    if lang != 'es':
        i = LANGS.index(lang)
        left = sorted({k for k in T if T[k][i-1] != k for d in outs.values()
                       if re.search(r'>\s*' + ws(k) + r'\s*<', d[d.index('<body'):])})
        print(lang, 'sin traducir:', left[:20])
print('ok:', ', '.join(f for f, _ in PAGES))
