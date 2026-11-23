"""Banco de pruebas del agente Liferay Architect.

Nivel 1  Estructura: frontmatter, routing agente <-> skills, referencias cruzadas, prefijo "Liferay DXP.".
Nivel 2  Coherencia: los ejemplos cumplen las restricciones críticas del agente y la metodología.
Nivel 3  Sintaxis: Java (parser de javac), YAML, JSON, XML, properties y .config.
Nivel 4  Hechos y metodología: afirmaciones contrastadas con la documentación oficial y reglas
         de la metodología que el agente debe contener.

Uso: python3 validation/run_tests.py <ruta-del-agente>
Requiere JDK 17+ (javac) y PyYAML. Compila validation/ParseJava.java automáticamente.
"""
import json
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
HERE = Path(__file__).resolve().parent
BUILD = Path(tempfile.gettempdir()) / "liferay-agent-parsejava"
AGENT = ROOT / ".github/agents/Liferay Architect.agent.md"
SKILLS = ROOT / ".github/skills"
results = []


def check(level, tid, ok, detail=""):
    results.append((level, tid, ok, detail))


def blocks(text):
    return [(m.group(1), m.group(2), text[: m.start()].count("\n") + 1)
            for m in re.finditer(r"```(\w*)\n(.*?)```", text, re.S)]


agent = AGENT.read_text(encoding="utf-8")
names = sorted(p.name for p in SKILLS.iterdir() if p.is_dir())
texts = {n: (SKILLS / n / "SKILL.md").read_text(encoding="utf-8") for n in names}
ALL = list(texts.items()) + [("AGENT", agent)]

# ------------------------------------------------------------------ Nivel 1
check(1, "agent.frontmatter", re.match(r"^---\nname: Liferay Architect\n", agent) is not None)
for n, t in texts.items():
    m = re.search(r"^description:\s*'(.*)'$", t, re.M)
    desc = m.group(1) if m else ""
    check(1, f"{n}.name==folder", re.search(rf"^name: {n}$", t, re.M) is not None)
    check(1, f"{n}.description<=1024", 0 < len(desc) <= 1024, f"{len(desc)}")
    check(1, f"{n}.description-trigger", "Usar cuando" in desc)
    check(1, f"{n}.description-prefix", desc.startswith("Liferay DXP."))
routed = set(re.findall(r"skill `(liferay-[a-z0-9-]+)`", agent))
check(1, f"routing ({len(names)} skills)", routed == set(names),
      f"sin ruta {sorted(set(names) - routed)} | ruta sin skill {sorted(routed - set(names))}")
NOT_SKILLS = {"liferay-portal", "liferay-default", "liferay-ui"}  # repositorio, Helm chart y taglib
for n, t in ALL:
    refs = set(re.findall(r"`(liferay-[a-z0-9]+(?:-[a-z0-9]+)*)`", t)) - NOT_SKILLS
    check(1, f"{n}.cross-refs", refs <= set(names), f"rotas {sorted(refs - set(names))}")

# ------------------------------------------------------------------ Nivel 2
CX_TYPES = {
    "customElement", "iframe", "globalCSS", "globalJS", "themeCSS", "themeFavicon", "themeSpritemap",
    "jsImportMapsEntry", "fdsCellRenderer", "fdsFilter", "editorConfigContributor", "staticContent",
    "instanceSettings", "oAuthApplicationHeadlessServer", "oAuthApplicationUserAgent",
    "objectAction", "workflowAction", "notificationType", "batch", "siteInitializer",
    "commercePaymentIntegration", "commerceCheckoutStep", "commerceShippingEngine",
}
FRONTEND = {"customElement", "iframe", "globalCSS", "globalJS", "themeCSS", "themeFavicon", "themeSpritemap",
            "jsImportMapsEntry", "fdsCellRenderer", "fdsFilter", "editorConfigContributor", "staticContent"}
MICRO = {"objectAction", "workflowAction", "notificationType", "commercePaymentIntegration",
         "commerceCheckoutStep", "commerceShippingEngine"}
JAVA_RULES = {
    "System.out": r"System\.(out|err)\.",
    "printStackTrace": r"\.printStackTrace\(",
    "util-estatica-de-servicio": r"\b\w+(Local)?ServiceUtil\.",
    "util-estatica-portal": r"\b(PortalUtil|LanguageUtil)\.",
    "new-de-servicio": r"new \w+(LocalService|Service)Impl\(",
}
SECRET_LITERAL = re.compile(r"(?i)(password|secret|token)[^\s=:\"]*\s*[=:]\s*\"?(?!\$\{|\"|<|$)[^\s\"]+")

viol = []
for n, t in texts.items():
    for lang, code, start in blocks(t):
        lines = code.splitlines()
        # Metodología: sin mavenLocal ni plugin maven en ningún bloque
        for i, ln in enumerate(lines):
            if re.search(r"mavenLocal\(\)|apply plugin:\s*[\"']maven[\"']", ln):
                viol.append(f"{n}:{start + i + 1} [mavenLocal/plugin-maven] {ln.strip()[:80]}")
            if re.search(r"\b\w*(SUFIX|METHOS)\b", ln):
                viol.append(f"{n}:{start + i + 1} [errata-en-constante] {ln.strip()[:80]}")
        if lang == "java":
            for i, ln in enumerate(lines):
                part = ln.split("//")[0]
                for rule, pat in JAVA_RULES.items():
                    if re.search(pat, part):
                        viol.append(f"{n}:{start + i + 1} [{rule}] {ln.strip()[:80]}")
            if "jakarta.portlet" in code and "javax.portlet" in code:
                viol.append(f"{n}:{start} [mezcla-javax-jakarta]")
            for fm in re.finditer(r"@Reference[^\n]*\n\s*private (?!static)[\w<>, ]+ (\w+);", code):
                if not fm.group(1).startswith("_"):
                    viol.append(f"{n}:{start} [referencia-sin-prefijo-_] {fm.group(1)}")
            # Componentes OSGi con sufijo Util/UtilImpl (deben ser Helper/HelperImpl)
            for cm in re.finditer(r"@Component\([^)]*\)\s*public class (\w+)", code, re.S):
                if re.search(r"Util(Impl)?$", cm.group(1)):
                    viol.append(f"{n}:{start} [componente-con-sufijo-Util] {cm.group(1)}")
        if lang == "jsp":
            first = lines[0] if lines else ""
            constants_file = "init.jsp" in first or "configuration.jsp" in first
            for i, ln in enumerate(lines):
                if re.search(r"<%(?![@=-])", ln):  # bloque <% %> o declaración <%! %>
                    viol.append(f"{n}:{start + i + 1} [bloque-scriptlet] {ln.strip()[:80]}")
                elif "<%=" in ln:
                    if not constants_file:
                        viol.append(f"{n}:{start + i + 1} [scriptlet-fuera-de-init] {ln.strip()[:80]}")
                    elif not re.match(r'\s*<c:set\s+var="\w+"\s+value="<%=[^%]+%>"\s*/>\s*$', ln):
                        viol.append(f"{n}:{start + i + 1} [expresion-no-asigna-constante] {ln.strip()[:80]}")
        if lang in ("ftl", "html"):
            for i, ln in enumerate(lines):
                if re.search(r"\b(serviceLocator|staticUtil|objectUtil)\b", ln):
                    viol.append(f"{n}:{start + i + 1} [variable-restringida-ftl] {ln.strip()[:80]}")
                for om in re.finditer(r"\$\{([^}]*getData\(\)[^}]*)\}", ln):
                    if not om.group(1).startswith("htmlUtil") and "src=" not in ln:
                        viol.append(f"{n}:{start + i + 1} [salida-sin-escapar] {ln.strip()[:80]}")
        if lang == "yaml":
            try:
                doc = yaml.safe_load(code) or {}
            except yaml.YAMLError:
                doc = {}
            if isinstance(doc, dict):
                types = {v.get("type") for v in doc.values() if isinstance(v, dict) and "type" in v}
                for ty in types:
                    if ty not in CX_TYPES:
                        viol.append(f"{n}:{start} [tipo-de-client-extension-desconocido] {ty}")
                if types & FRONTEND and types & MICRO:
                    viol.append(f"{n}:{start} [frontend-y-microservicio-en-el-mismo-proyecto]")
        if lang in ("properties", "config", "bash", "json", "yaml"):
            for i, ln in enumerate(lines):
                if ln.strip().startswith("#"):
                    continue
                if SECRET_LITERAL.search(ln):
                    viol.append(f"{n}:{start + i + 1} [secreto-literal] {ln.strip()[:80]}")
    if any(lang == "java" and "@Component" in code for lang, code, _ in blocks(t)) and "SaaS" not in t:
        viol.append(f"{n} [modulo-osgi-sin-advertencia-saas]")
check(2, "examples-obey-critical-restrictions", not viol, "\n      ".join(viol))

for tid, pat in [
    ("agent.extension-order", r"## Cómo extender Liferay[\s\S]*1\. \*\*Funcionalidad[\s\S]*3\. \*\*Client extensions[\s\S]*4\. \*\*Módulos OSGi[\s\S]*5\. \*\*Overrides"),
    ("agent.no-ext-plugins", r"\*\*Nunca\*\*: plugins Ext"),
    ("agent.min-version", r"Mínimo soportado: 2025\.Q1"),
    ("agent.saas-restriction", r"en \*\*SaaS\*\* solo client extensions"),
    ("agent.git-restriction", r"\*\*Git\*\*: no ejecutes operaciones que modifiquen el repositorio"),
    ("agent.template-context-contributor", r"\*\*Template Context Contributor\*\*"),
    ("agent.no-mavenLocal", r"Nunca `mavenLocal\(\)`"),
    ("agent.helper-naming", r"`\[Funcionalidad\]Helper` y `\[Funcionalidad\]HelperImpl`"),
    ("agent.values-by-name", r"por nombre o clave, nunca por ID"),
    ("agent.jsp-restriction", r"\*\*JSP\*\*: scriptlets solo como expresiones"),
]:
    check(2, tid, re.search(pat, agent) is not None)

# ------------------------------------------------------------------ Nivel 3
fails = []


def clean_java(c):
    c = re.sub(r"\{\s*\.\.\.\s*\}", "{}", c)
    c = re.sub(r"\(\s*\.\.\.\s*\)", "()", c)
    return re.sub(r"^\s*\.\.\.\s*$", "", c, flags=re.M)


def segments(code):
    segs, cur, depth = [], [], 0
    for ln in code.split("\n"):
        s = re.sub(r"//.*$", "", re.sub(r'"[^"]*"', "", ln))
        if ln.strip() == "" and depth == 0 and cur:
            segs.append("\n".join(cur))
            cur = []
            continue
        cur.append(ln)
        depth += s.count("{") + s.count("(") - s.count("}") - s.count(")")
    if cur:
        segs.append("\n".join(cur))
    return segs


WRAPS = [lambda c: c, lambda c: f"class D__ {{\n{c}\n}}",
         lambda c: f"class D__ {{ void m__() throws Exception {{\n{c}\n}} }}"]
jblocks = [(n, s, clean_java(c)) for n, t in ALL for lang, c, s in blocks(t) if lang == "java"]
if jblocks:
    if not (BUILD / "ParseJava.class").exists():
        BUILD.mkdir(parents=True, exist_ok=True)
        subprocess.run(["javac", "-encoding", "UTF-8", "-d", str(BUILD), str(HERE / "ParseJava.java")], check=True)
    tmp = Path(tempfile.mkdtemp())
    units = []
    for bi, (_, _, code) in enumerate(jblocks):
        for si, seg in enumerate([code] + segments(code)):
            for wi, wrap in enumerate(WRAPS):
                p = tmp / f"b{bi}_s{si}_w{wi}.java"
                p.write_text(wrap(seg), encoding="utf-8")
                units.append((bi, si, p))
    listing = tmp / "files.txt"
    listing.write_text("\n".join(str(u[2]) for u in units))
    out = subprocess.run(["java", "-cp", str(BUILD), "ParseJava", str(listing)], capture_output=True, text=True).stdout
    status = dict(line.split("\t", 1) for line in out.splitlines() if "\t" in line)
    for bi, (n, s, _) in enumerate(jblocks):
        by = {}
        for b, si, p in units:
            if b == bi:
                by.setdefault(si, []).append(status.get(str(p), "missing"))
        if any(x == "OK" for x in by[0]):
            continue
        bad = [f"segmento {si}: {v[0]}" for si, v in by.items() if si > 0 and not any(x == "OK" for x in v)]
        if bad:
            fails.append(f"{n}:{s} [java] " + " | ".join(bad))

counts = {"java": len(jblocks), "yaml": 0, "json": 0, "xml": 0, "properties": 0, "config": 0}
for n, t in ALL:
    for lang, c, s in blocks(t):
        if lang == "yaml":
            counts["yaml"] += 1
            try:
                yaml.safe_load(c)
            except yaml.YAMLError as e:
                fails.append(f"{n}:{s} [yaml] {str(e).splitlines()[0]}")
        elif lang == "json":
            counts["json"] += 1
            try:
                json.loads(c)
            except json.JSONDecodeError as e:
                fails.append(f"{n}:{s} [json] {e}")
        elif lang == "xml":
            counts["xml"] += 1
            body = re.sub(r"<!DOCTYPE[^>]*>", "", c)
            try:
                ET.fromstring(body.strip())
            except ET.ParseError as e:
                fails.append(f"{n}:{s} [xml] {e}")
        elif lang in ("properties", "config"):
            counts[lang] += 1
            for i, ln in enumerate(c.splitlines()):
                st = ln.strip()
                if not st or st.startswith("#"):
                    continue
                if lang == "properties" and not re.match(r"^[\w.\-]+\s*[=:]", st):
                    fails.append(f"{n}:{s + i + 1} [properties] {st[:60]}")
                if lang == "config" and not re.match(r'^[\w.\-]+=([ILBDFSCXT]?"[^"]*"|\[.*\])$', st):
                    fails.append(f"{n}:{s + i + 1} [config] {st[:60]}")
summary = " + ".join(f"{v} {k}" for k, v in counts.items())
check(3, f"syntax ({summary})", not fails, "\n      ".join(fails))

# ------------------------------------------------------------------ Nivel 4
FACTS = [
    # Documentación oficial
    ("liferay-workspace", r"liferay\.workspace\.product", True, "La versión se lee de liferay.workspace.product"),
    ("liferay-workspace", r"JDK 17 y 21", True, "JDK 17 y 21 desde 2024.Q3"),
    ("liferay-workspace", r"se eliminó en Gradle 7", True, "Plugin maven de Gradle eliminado"),
    ("liferay-deployment", r"_PERIOD_", True, "Codificación de variables LIFERAY_*"),
    ("liferay-deployment", r"/mnt/liferay/files", True, "Carpetas montadas del contenedor"),
    ("liferay-deployment", r"liferay-default", True, "Helm chart oficial liferay-default"),
    ("liferay-cloud", r"\*\*Solo client extensions\*\*", True, "SaaS: solo client extensions"),
    ("liferay-cloud", r"entorno DR[^\n]*\*\*responsabilidad del cliente\*\*", True, "SaaS DR responsabilidad del cliente"),
    ("liferay-configuration", r"eliminados en 7\.3", True, "Sin ficheros portal-<companyId>.properties"),
    ("liferay-client-extensions", r"\*\*No\*\* se puede mezclar frontend con microservicio", True, "Agrupación prohibida"),
    ("liferay-upgrades", r"db_upgrade_client\.sh", True, "Herramienta db_upgrade_client"),
    ("liferay-upgrades", r"^\s*\./db_upgrade\.sh", False, "No recomendar db_upgrade.sh"),
    ("liferay-personalization", r"\*\*No está soportado con staging activado\.\*\*", True, "A/B testing sin staging"),
    ("liferay-analytics", r"\*\*Un token por entorno\*\*", True, "Un token por entorno"),
    ("liferay-commerce", r"no almacena datos de tarjetas", True, "Commerce no almacena tarjetas"),
    ("liferay-search", r"\*\*no\*\* es para producción", True, "Modo de desarrollo de búsqueda no para producción"),
    ("liferay-content", r"TemplateContextContributor\.TYPE_GLOBAL", True, "Template Context Contributor global"),
    ("liferay-osgi", r"lombok\.experimental", True, "@UtilityClass es experimental en Lombok"),
    ("liferay-osgi", r"tools\.jackson", True, "Jackson 3 cambia de paquete"),
    # Metodología
    ("liferay-osgi", r"PORTLET_PREFERENCE_SUFFIX", True, "Constante PORTLET_PREFERENCE_SUFFIX"),
    ("liferay-osgi", r"RESOURCE_METHODS", True, "Bloque RESOURCE_METHODS"),
    ("liferay-osgi", r"\"mvc\.command\.name=/\"", True, "Render por defecto en MVCRenderCommand"),
    ("liferay-osgi", r"Comprueba siempre en el render que las preferencias obligatorias", True, "Configuración obligatoria comprobada"),
    ("liferay-osgi", r"isShow", True, "isShow en PanelApp"),
    ("liferay-osgi", r"\*\*`portletNamespace` siempre\*\*", True, "portletNamespace siempre"),
    ("liferay-osgi", r"\*\*Scriptlets solo para pasar constantes a JSTL\*\*", True, "Scriptlets solo para constantes"),
    ("liferay-osgi", r"Ningún bloque `<% \.\.\. %>`", True, "Sin bloques de scriptlet"),
    ("liferay-osgi", r"No crees `Language\.properties`", True, "Resource bundle sin Language.properties"),
    ("liferay-osgi", r"\*\*idioma por defecto del proyecto\*\*", True, "Portlet: Language.properties en el idioma por defecto"),
    ("liferay-content", r"como mínimo dos plantillas", True, "Plantillas de resumen y detalle"),
    ("liferay-content", r"\*\*Variables\*\* \|[\s\S]*\*\*Template\*\* \|[\s\S]*\*\*Macros\*\* \|[\s\S]*\*\*Functions\*\*", True, "Bloques Variables, Template, Macros, Functions"),
    ("liferay-content", r"embebe la \*\*plantilla de resumen\*\*", True, "ADT embebe la plantilla de resumen"),
    ("liferay-content", r"no\*\* parsees el XML con `SAXReader`", True, "Campos de estructura sin SAXReader"),
    ("liferay-content", r"\*\*Services\*\* \|", False, "Sin bloque Services en plantillas"),
    ("liferay-service-builder", r"disponibles en \*\*todos\*\* los modelos de despliegue", True, "Microservicios en todos los modelos"),
]
ff = []
for skill, pat, must, desc in FACTS:
    hit = re.search(pat, texts.get(skill, ""), re.M) is not None
    if must and not hit:
        ff.append(f"FALTA {desc} ({skill})")
    if not must and hit:
        ff.append(f"CONTRADICHO {desc} ({skill})")
check(4, f"facts ({len(FACTS)})", not ff, "\n      ".join(ff))

total, ok = len(results), sum(1 for r in results if r[2])
for lvl in (1, 2, 3, 4):
    rows = [r for r in results if r[0] == lvl]
    extra = f"  {rows[0][1]}" if lvl in (3, 4) else ""
    print(f"=== Nivel {lvl}: {sum(1 for r in rows if r[2])}/{len(rows)} OK{extra}")
    for _, tid, good, d in rows:
        if not good:
            print(f"  FAIL {tid}\n      {d}")
print(f"TOTAL {ok}/{total} comprobaciones superadas")
