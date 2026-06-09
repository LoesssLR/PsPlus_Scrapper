# Rastreador de Ofertas de PSN Plus

---

## Estructura del Proyecto

```text
psn_plus_tracker/
├── src/                      # Código de producción (Source)
│   ├── config.py             # Carga y validación de variables de entorno (.env)
│   ├── main.py               # Punto de entrada y orquestador del ciclo de vida
│   ├── notifier.py           # Módulo de envío de alertas por correo SMTP
│   └── scraper.py            # Robot de extracción usando Playwright Asíncrono
├── requirements.txt          # Manifiesto de dependencias de Python
└── .env                      # Variables de entorno secretas (Se debe crear manualmente)
```

* **`src/`:** Capa de lógica principal extraída del raíz. Mantener cada módulo con una sola responsabilidad (Scraping, Notificación, Configuración) permite escalar y dar mantenimiento al proyecto sin acoplamiento no deseado.
* **`requirements.txt`:** Lista las librerías necesarias externas al estándar de Python (`playwright`, `python-dotenv`).

---

## Configuración del Entorno

```bash
# 1. Crear el entorno virtual aislado (.venv)
python -m venv .venv

# 2. Activar el entorno virtual (En Windows / PowerShell)
.venv\Scripts\activate

# 3. Instalar las dependencias y frameworks listados en requirements
pip install -r requirements.txt

# 4. Instalar los ejecutables del Navegador Web utilizados por Playwright
playwright install chromium
```

### Archivo de Variables de Entorno (`.env`)
Debes crear un archivo `.env` en la raíz de tu proyecto para proveer las credenciales de envío de correo, siguiendo este formato obligatorio:

```text
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=tucorreo.bot@gmail.com
SENDER_PASSWORD=tu_app_password_o_contraseña_secreta
RECEIVER_EMAIL=tucorreo_personal@gmail.com
PS_PLUS_URL=https://www.playstation.com/es-cr/ps-plus/#subscriptions
```
> ⚠️ **Seguridad:** Usa "Contraseñas de Aplicación" si estás integrando Gmail. Tu contraseña regular no funcionará debido a protecciones modernas de 2 pasos.

---

## Ejecución y Parámetros

### 1. Ejecución Básica
Para arrancar el motor de rastreo asíncrono y evaluar los precios al momento, corremos el módulo principal aseguradonos de estar de pie sobre la estructura general del proyecto.
```bash
python -m src.main
```

### Explicación del Flujo Subyacente:
* **`python -m src.main`:** Ejecuta el archivo `main.py` de la carpeta `src` como módulo, facilitando las importaciones relativas dentro del paquete.
* El scraper levantará un navegador invisible (*Headless Chromium*).
* Ingresará directamente a la URL de suscripciones proporcionada vía `config.py`.
* Si detecta modificaciones u ofertas basadas en tu lógica interna, delegará la salida a `notifier.py` para construir un reporte HTML y enviarlo por correo.

---

## Consideraciones Estratégicas y Resultados

Al ejecutar la herramienta de scraping, el flujo es documentado sutilmente hasta la salida final en consola:

| Fases de Ejecución | Significado del Paso o Solución Técnica |
| :--- | :--- |
| **Conexión Headless** | Levanta Chromium silenciando la GUI pero falsificando un *User-Agent* humano convencional para evitar bloqueos Cloudflare o Datadome por parte de la plataforma PlayStation. |
| **Interacción Reactiva** | Puesto que el sitio se renderiza en cliente, `wait_for_selector` es vital. Asegura que los precios existan físicamente en el DOM antes de que Python intente parsearlos.|
| **Eventos Inyectados** | El bloqueador de Cookies y *bars* fijos corrompen eventos físicos de mouse. El script inyecta JavaScript puro mediante `.evaluate("el => el.click()")` para accionar las tarjetas (Essential, Extra, Deluxe). |

---

## Ejemplo Práctico de Análisis

Supongamos la siguiente salida natural del script por consola tras lograr una ejecución exitosa:

```text
Conectando a la plataforma de PlayStation...
Esperando a que carguen los elementos de la tienda...
Correo de notificación enviado con éxito.
```

### Interpretación de la Extracción:

1. **Extracción por Plan (`#essential`, `#extra`, `#deluxe`):**
   * **Diagnóstico:** Se procesan 3 pestañas dinámicas donde la información de cada una carga solo al instante que se selecciona (Lazy Load de los precios y texto legal).
   * **Razón Técnica:** Se interpone un `await page.wait_for_timeout(1500)` simulado para darle la ventana exacta al framework visual en la web ajena a reemplazar el contenido. 

2. **Orquestación de Envío:**
   * **Diagnóstico:** La alerta no bloquea el hilo sino que procesa sincrónicamente un volcado del diccionario extraído hacia el protocolo `SMTP_SERVER`.
   * **Razón:** El formato del correo viaja como clase `MIMEText(html, 'html')`, armando tabulaciones atractivas en tu app de Gmail/Outlook basadas en la data cruda robada del grid de Sony.
