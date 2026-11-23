"""Selección de skills por descripción (aproximación al mecanismo de Copilot).
Uso: python3 validation/scenarios.py <ruta-del-agente>"""
import re
import sys
import unicodedata
from pathlib import Path

STOP = set("de la el los las un una y o en con para que se por al del mi me lo le es este esta cuando usar cubre liferay dxp".split())


def roots(t):
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return {w[:5] for w in re.findall(r"[a-z0-9]+", t) if len(w) > 2 and w not in STOP}


S = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve() / ".github/skills"
desc = {d.name: roots(re.search(r"^description:\s*'(.*)'$", (d / "SKILL.md").read_text(), re.M).group(1))
        for d in S.iterdir() if d.is_dir()}
CASES = [
    ("Qué versión de Liferay usa este proyecto y cómo creo un módulo con Blade", {"workspace"}),
    ("Dockeriza Liferay y despliégalo en AKS con Kubernetes", {"deployment"}),
    ("Montar un clúster de dos nodos con sesiones persistentes", {"deployment"}),
    ("Configurar el LCP.json del servicio liferay en Liferay Cloud", {"cloud"}),
    ("Esto se puede hacer en SaaS o necesito un módulo OSGi", {"cloud", "client-extensions"}),
    ("Cambiar una propiedad del portal-ext.properties solo en producción", {"configuration"}),
    ("Exportar la configuración de System Settings a un fichero .config", {"configuration"}),
    ("Crear un portlet MVC con un comando de acción", {"osgi"}),
    ("Un componente OSGi no se activa porque una referencia no se satisface", {"osgi", "troubleshooting"}),
    ("Añadir una columna a una entidad de Service Builder", {"service-builder", "upgrades"}),
    ("Crear una entidad de solicitudes con campos, relaciones y permisos sin código", {"objects"}),
    ("Ejecutar lógica en un microservicio al crear un registro de un Object", {"objects", "client-extensions"}),
    ("Crear un widget con Angular como custom element", {"client-extensions"}),
    ("Añadir un JavaScript global a todas las páginas del site", {"client-extensions"}),
    ("Crear una estructura y una plantilla FreeMarker de contenido web para noticias", {"content"}),
    ("Configurar Adaptive Media para las imágenes", {"content"}),
    ("Crear un fragment con elementos editables para la página de inicio", {"fragments"}),
    ("Cambiar colores y tipografías del site con el style book", {"fragments"}),
    ("Consumir las APIs headless desde un ERP con OAuth2", {"headless"}),
    ("Crear un endpoint REST propio con REST Builder", {"headless"}),
    ("Importar miles de registros de forma masiva", {"headless", "objects"}),
    ("Comprobar permisos antes de devolver un pedido en un servicio", {"security"}),
    ("Configurar SSO con SAML y autenticación multifactor", {"security"}),
    ("Los resultados de búsqueda están desactualizados, hay que reindexar", {"search", "troubleshooting"}),
    ("Configurar Elasticsearch remoto para producción", {"search"}),
    ("Crear un flujo de aprobación de contenidos con dos revisores", {"workflow"}),
    ("Montar una tienda B2B con precios por cliente", {"commerce"}),
    ("Integrar una pasarela de pago en el checkout", {"commerce"}),
    ("Mostrar contenido distinto a cada tipo de usuario con segmentos", {"personalization"}),
    ("Hacer un A/B test de la página de campaña", {"personalization"}),
    ("Conectar Liferay con Analytics Cloud y medir visitas", {"analytics"}),
    ("Registrar eventos personalizados de clics en Analytics Cloud", {"analytics"}),
    ("Crear un site completo desde el repositorio con un site initializer", {"sites"}),
    ("Configurar staging remoto para publicar en producción", {"sites"}),
    ("Gestionar varias marcas aisladas con instancias virtuales", {"sites"}),
    ("Pasar de 2025.Q1 a 2025.Q3 y actualizar la base de datos", {"upgrades"}),
    ("Migrar portlets heredados y Service Builder a Objects y client extensions", {"upgrades", "service-builder"}),
    ("Escribir tests de integración con Arquillian para un servicio", {"testing"}),
    ("Las previsualizaciones de documentos con LibreOffice fallan en producción", {"troubleshooting"}),
    ("El servidor va lento, analizar thread dumps", {"troubleshooting"}),
    ("Pasar Source Formatter y corregir avisos de SonarQube antes del PR", {"quality"}),
    # Metodología
    ("Crear la clase de constantes del portlet con los bloques de render y action", {"osgi"}),
    ("El portlet tiene que avisar si no se ha configurado la carpeta en las preferencias", {"osgi"}),
    ("Crear una utilidad reutilizable para varios módulos", {"osgi"}),
    ("Serializar un objeto a JSON con Jackson", {"osgi"}),
    ("Usar Lombok para los getters y setters del modelo", {"osgi"}),
    ("Necesito llamar a un servicio desde una plantilla FreeMarker", {"content"}),
    ("Hacer un ADT que reutilice la plantilla de resumen de la estructura", {"content"}),
    ("Obtener el id de un vocabulario por su nombre desde una plantilla", {"content"}),
    ("Usar el API de envío de emails desde otro módulo del workspace", {"workspace"}),
    ("Crear un API y su implementación para la integración con SAP", {"osgi", "workspace"}),
    ("Dudo entre Objects y Service Builder porque no nos dejan usar microservicios", {"service-builder"}),
    ("Añadir traducciones en castellano y catalán a un portlet", {"osgi"}),
    ("Sobrescribir textos del portal con un resource bundle", {"osgi"}),
    ("La aplicación del panel de control solo debe verse en sus sites", {"osgi"}),
]
hits = 0
for prompt, exp in CASES:
    exp = {"liferay-" + e for e in exp}
    p = roots(prompt)
    top3 = sorted(desc, key=lambda s: -len(p & desc[s]))[:3]
    ok = bool(exp & set(top3))
    hits += ok
    print(f"{'OK ' if ok else 'MISS'} {prompt[:76]:76} -> {', '.join(x.replace('liferay-', '') for x in top3)}")
print(f"\nSelección correcta en top-3: {hits}/{len(CASES)} (skills: {len(desc)})")
