# Vértice Consulting

**Transformación Tecnológica LATAM**

Sitio web de Vértice Consulting, consultora tecnológica independiente: estrategia y transformación, plataformas core y SAP, gobierno de programas, datos e IA, infraestructura y seguridad.

## Sitio en vivo

[https://uncas16.github.io/vertice-consulting/](https://uncas16.github.io/vertice-consulting/) — en español, inglés (`/en/`) y portugués (`/pt/`), con modo claro y oscuro.

## Páginas

- **Inicio** (`index.html`): propuesta de valor, cifras, clientes, resumen de los 5 frentes y resultados.
- **Servicios** (`servicios.html`): las 14 líneas de servicio y cómo trabajamos.
- **Nosotros** (`nosotros.html`): quiénes somos, misión, visión y valores, equipo, trayectoria y credenciales.
- **Contacto** (`contacto.html`): formulario (Google Apps Script → Google Sheets + email). Los botones "Cotizar" llegan con el servicio preseleccionado (`contacto.html?servicio=...`).

## Cómo editar

Todo el contenido vive en **una sola fuente**: `_fuente/sitio.html` (español). Las páginas publicadas se generan:

```
python3 i18n/construir.py
```

1. Editar el texto en `_fuente/sitio.html`.
2. Si es un texto nuevo o cambiado, agregar su traducción en `i18n/traducciones.py` (`"español": ("inglés", "portugués")`).
3. Ejecutar el script: regenera `index.html`, `servicios.html`, `nosotros.html`, `contacto.html` y sus copias en `en/` y `pt/`. Al final indica si quedó algún texto sin traducir.

Qué sección va en qué página se define en `PAGES`, y los títulos y descripciones de cada página en `META`, ambos al inicio de `i18n/construir.py`. No editar a mano los `.html` generados.

## Estructura

```
vertice-consulting/
├── _fuente/sitio.html   ← fuente única (no se publica)
├── i18n/construir.py    ← genera las páginas
├── i18n/traducciones.py ← tabla español → inglés, portugués
├── index.html, servicios.html, nosotros.html, contacto.html  (generados)
├── en/, pt/             (generados)
└── img/                 ← fotos del equipo y fondos
```
