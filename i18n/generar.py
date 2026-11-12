# Genera en/index.html y pt/index.html a partir de index.html (español).
# Uso: python3 i18n/generar.py  — después de cambiar textos en español, agregar la traducción en traducciones.py.
import re, sys, os, html as H
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from traducciones import T
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://uncas16.github.io/vertice-consulting/'

src = open(f'{ROOT}/index.html', encoding='utf-8').read()

# 1) Spanish source: language switcher + hreflang (idempotent)
if 'class="lang"' not in src:
    sw = '<div class="lang" role="group" aria-label="Idioma"><a href="./" lang="es" aria-current="page">ES</a><a href="en/" lang="en">EN</a><a href="pt/" lang="pt">PT</a></div>'
    a = '<div class="social">'
    assert src.count(a) == 1
    src = src.replace(a, '<div class="topbar-right">' + sw + a, 1)
    a = '</svg></button></div>\n</div>\n<nav id="nav">'
    assert src.count(a) == 1, 'toggle anchor'
    src = src.replace(a, '</svg></button></div></div>\n</div>\n<nav id="nav">', 1)
    src = src.replace('<meta property="og:locale" content="es_CL"/>',
        '<meta property="og:locale" content="es_CL"/>\n'
        f'<link rel="alternate" hreflang="es" href="{BASE}"/>\n'
        f'<link rel="alternate" hreflang="en" href="{BASE}en/"/>\n'
        f'<link rel="alternate" hreflang="pt" href="{BASE}pt/"/>\n'
        f'<link rel="alternate" hreflang="x-default" href="{BASE}"/>', 1)
    css = '''  .topbar-right { display: flex; align-items: center; gap: 1.25rem; }
  .lang { display: flex; gap: 0.15rem; font-size: 0.8rem; font-weight: 600; letter-spacing: 0.06em; }
  .lang a { color: rgba(255, 255, 255, 0.65); text-decoration: none; padding: 0.3rem 0.45rem; border-radius: 2px; }
  .lang a:hover { color: #FFFFFF; }
  .lang a[aria-current="page"] { color: #FFFFFF; box-shadow: inset 0 -2px 0 var(--accent-lt); }
  .theme-toggle {'''
    src = src.replace('  .theme-toggle {', css, 1)
    # phone: keep only the number visible on very small screens
    src = src.replace('  @media (max-width: 768px) {', '''  @media (max-width: 420px) {
    .topbar-right { gap: 0.6rem; }
    .lang a { padding: 0.3rem 0.3rem; }
    .social { gap: 0.35rem; }
  }
  @media (max-width: 768px) {''', 1)
    open(f'{ROOT}/index.html', 'w', encoding='utf-8').write(src)

def ws(s):  # regex that tolerates whitespace/newlines between words
    return r'\s+'.join(re.escape(w) for w in s.split())

def build(lang, idx):
    s = src
    head_end = s.index('</head>')
    body_start = s.index('<body')
    keys = sorted(T, key=len, reverse=True)
    out_body = s[body_start:]
    # protect scripts/svgs from text-node replacement
    scripts = []
    def stash(m):
        scripts.append(m.group(0)); return f'\x00{len(scripts)-1}\x00'
    out_body = re.sub(r'<script.*?</script>|<svg.*?</svg>', stash, out_body, flags=re.S)
    for k in keys:
        v = T[k][idx-1]
        # whole text node
        out_body = re.sub(r'(>\s*)' + ws(k) + r'(\s*<)', lambda m: m.group(1) + v + m.group(2), out_body)
        # attributes
        for attr in ('placeholder', 'aria-label', 'alt', 'data-servicio', 'title'):
            out_body = out_body.replace(f'{attr}="{k}"', f'{attr}="{v}"')
    out_body = re.sub(r'\x00(\d+)\x00', lambda m: scripts[int(m.group(1))], out_body)
    # scripts: quoted JS strings
    for k in keys:
        v = T[k][idx-1].replace("'", "\\'")
        out_body = out_body.replace(f"'{k}'", f"'{v}'")
    head = s[:body_start]
    for k in keys:
        v = T[k][idx-1]
        head = head.replace(f'<title>{k}</title>', f'<title>{v}</title>').replace(f'content="{k}"', f'content="{v}"')
        head = head.replace(f"content: '{k}'", f"content: '{v}'")
    s = head + out_body
    code = ['es', 'en', 'pt'][idx]
    s = s.replace('<html lang="es">', f'<html lang="{code}">', 1)
    s = s.replace('content="es_CL"', 'content="' + {'en': 'en_US', 'pt': 'pt_BR'}[code] + '"', 1)
    s = s.replace(f'<meta property="og:url" content="{BASE}"/>', f'<meta property="og:url" content="{BASE}{code}/"/>', 1)
    s = s.replace('src="img/', 'src="../img/')
    s = s.replace('<a href="./" lang="es" aria-current="page">ES</a><a href="en/" lang="en">EN</a><a href="pt/" lang="pt">PT</a>',
        '<a href="../" lang="es">ES</a><a href="../en/" lang="en"' + (' aria-current="page"' if code == 'en' else '') + '>EN</a><a href="../pt/" lang="pt"' + (' aria-current="page"' if code == 'pt' else '') + '>PT</a>')
    wa = {'en': 'Hi%2C%20I%27d%20like%20to%20learn%20more%20about%20your%20consulting%20services.',
          'pt': 'Ol%C3%A1%2C%20gostaria%20de%20saber%20mais%20sobre%20seus%20servi%C3%A7os%20de%20consultoria.'}[code]
    s = s.replace('text=Hola%2C%20me%20interesa%20conocer%20m%C3%A1s%20sobre%20sus%20servicios%20de%20consultor%C3%ADa.', 'text=' + wa)
    os.makedirs(f'{ROOT}/{code}', exist_ok=True)
    open(f'{ROOT}/{code}/index.html', 'w', encoding='utf-8').write(
        '<!-- Generado desde ../index.html con la tabla de traducción; no editar a mano. -->\n' + s)
    return s

for i in (1, 2):
    out = build(None, i)
    # leftover Spanish check: any key still present as a whole text node
    left = [k for k in T if T[k][i-1] != k and re.search(r'>\s*' + ws(k) + r'\s*<', out[out.index('<body'):])]
    print(['', 'en', 'pt'][i], 'leftover:', left[:20])
