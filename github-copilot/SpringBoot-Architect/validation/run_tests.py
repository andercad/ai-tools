"""Banco de pruebas de agentes de desarrollo (perfiles: nestjs, spring).

Nivel 1  Estructura: frontmatter, routing agente <-> skills, referencias cruzadas.
Nivel 2  Coherencia: los ejemplos cumplen las restricciones críticas del propio agente
         y el orden de miembros que define.
Nivel 3  Sintaxis: TypeScript (compilador TS), Java (parser de javac), YAML (PyYAML).
Nivel 4  Hechos: afirmaciones contrastadas con documentación oficial que el agente
         no debe contradecir.

Uso: python3 run_tests.py <nestjs|spring> <ruta-del-agente>
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

PROFILE = sys.argv[1]
ROOT = Path(sys.argv[2] if len(sys.argv) > 2 else "..").resolve()
KIT = Path(__file__).resolve().parent
PREFIX = {"nestjs": "nestjs-", "spring": "spring-"}[PROFILE]
AGENT = next((ROOT / ".github/agents").glob("*.agent.md"))
SKILLS = ROOT / ".github/skills"
results = []


def check(level, tid, ok, detail=""):
    results.append((level, tid, ok, detail))


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip("'\"")
    return fm


def code_blocks(text):
    return [(m.group(1), m.group(2), text[: m.start()].count("\n") + 1)
            for m in re.finditer(r"```(\w*)\n(.*?)```", text, re.S)]


def is_counterexample(lines, idx):
    """Una línea es contraejemplo si el último marcador anterior es ❌/Evitar (y no ✅)."""
    marker = None
    for ln in lines[: idx + 1]:
        if "❌" in ln or "Evitar" in ln:
            marker = "bad"
        if "✅" in ln:
            marker = "good"
    return marker == "bad"


agent_text = AGENT.read_text(encoding="utf-8")
skill_names = {p.name for p in SKILLS.iterdir() if p.is_dir()}
skill_texts = {n: (SKILLS / n / "SKILL.md").read_text(encoding="utf-8") for n in sorted(skill_names)}
ALL_TEXTS = list(skill_texts.items()) + [("AGENT", agent_text)]

# ------------------------------------------------------------------ Nivel 1
fm = frontmatter(agent_text)
check(1, "agent.frontmatter", fm is not None and all(k in fm for k in ("name", "description", "tools")))
for name, text in skill_texts.items():
    sfm = frontmatter(text)
    check(1, f"{name}.frontmatter", sfm is not None)
    if not sfm:
        continue
    check(1, f"{name}.name==folder", sfm.get("name") == name, sfm.get("name", ""))
    desc = sfm.get("description", "")
    check(1, f"{name}.description<=1024", 0 < len(desc) <= 1024, f"{len(desc)} chars")
    check(1, f"{name}.has-trigger-words", "Usar cuando" in desc)

routed = set(re.findall(rf"skill `({PREFIX}[a-z0-9-]+)`", agent_text))
check(1, "routing.all-skills-routed", routed == skill_names,
      f"sin ruta: {sorted(skill_names - routed)} | ruta sin skill: {sorted(routed - skill_names)}")

NOT_SKILLS = re.compile(r"^(spring-boot|spring-modulith|spring-security-(test|crypto)|nestjs-(cls|pino))")
for name, text in ALL_TEXTS:
    refs = {r for r in re.findall(rf"`({PREFIX}[a-z0-9]+(?:-[a-z0-9]+)*)`", text) if not NOT_SKILLS.match(r)}
    broken = sorted(refs - skill_names)
    check(1, f"{name}.cross-refs", not broken, f"rotas: {broken}")

# ------------------------------------------------------------------ Nivel 2
violations = []


def flag(name, start, i, rule, line):
    violations.append(f"{name}:{start + i + 1} [{rule}] {line.strip()[:95]}")


if PROFILE == "nestjs":
    RULES = {
        "any": r"(:\s*any\b|<any>|\bas any\b)",
        "console.log": r"console\.log\(",
        "res-sin-passthrough": r"@Res\(\)",
        "useGlobalGuards": r"app\.useGlobalGuards\(",
        "synchronize-true": r"synchronize:\s*true",
        "wildcard-express4": r"forRoutes\(\s*'\*'\s*\)|@(Get|Post|All)\('[^']*/\*'\)",
    }
    for name, text in skill_texts.items():
        for lang, code, start in code_blocks(text):
            if lang not in ("typescript", "ts"):
                continue
            lines = code.splitlines()
            for i, ln in enumerate(lines):
                code_part = ln.split("//")[0]
                if is_counterexample(lines, i):
                    continue
                for rule, pat in RULES.items():
                    if re.search(pat, code_part):
                        flag(name, start, i, rule, ln)
                if "process.env" in code_part and name != "nestjs-config":
                    flag(name, start, i, "process.env-fuera-de-config", ln)
                if re.search(r"throw new Error\(", code_part) and name != "nestjs-config":
                    flag(name, start, i, "throw-Error-generico", ln)
                if "forwardRef(" in code_part and not any("//" in p for p in lines[max(0, i - 3): i]):
                    flag(name, start, i, "forwardRef-sin-documentar", ln)
            # propiedades decoradas sin `!`, `?` ni inicializador
            for i, ln in enumerate(lines):
                if re.match(r"\s+(readonly\s+)?\w+:\s*[^=;(]+;\s*(//.*)?$", ln) and i > 0 \
                        and lines[i - 1].strip().startswith("@") and not is_counterexample(lines, i):
                    flag(name, start, i, "propiedad-sin-!", ln)
            # orden: en controladores, GET antes que escrituras; en resolvers Query < Mutation < ResolveField
            joined = "\n".join(lines)
            for cm in re.finditer(r"@(Controller|Resolver)\([^)]*\)\s*export class (\w+).*?\n\}", joined, re.S):
                seen_write = False
                for dm in re.finditer(r"@(Get|Post|Put|Patch|Delete|Query|Mutation|ResolveField)\(", cm.group(0)):
                    kind = dm.group(1)
                    if kind in ("Post", "Put", "Patch", "Delete", "Mutation", "ResolveField"):
                        seen_write = True
                    elif seen_write:
                        violations.append(f"{name}::{cm.group(2)} [orden] lectura '@{kind}' después de escritura")
else:  # spring
    RULES = {
        "System.out": r"System\.(out|err)\.",
        "printStackTrace": r"\.printStackTrace\(",
        "javax": r"\bjavax\.(persistence|validation|servlet)",
        "security-legacy": r"WebSecurityConfigurerAdapter|authorizeRequests\(|\)\s*\.and\(\)",
        "MockBean": r"@MockBean\b",
        "RestTemplate": r"(?<!Test)\bRestTemplate\b",
        "entity-as-request": r"@(RequestBody|ModelAttribute)\s+\w*Entity\b",
        "optional-param": r"\(\s*[^)]*\bOptional<[^>]+>\s+\w+\s*[,)]",
    }
    for name, text in skill_texts.items():
        for lang, code, start in code_blocks(text):
            lines = code.splitlines()
            if lang == "java":
                is_test = "@Test" in code
                for i, ln in enumerate(lines):
                    code_part = ln.split("//")[0]
                    if is_counterexample(lines, i):
                        continue
                    for rule, pat in RULES.items():
                        if rule == "optional-param" and not re.search(r"^\s*(public|protected|private|\w+<|[A-Z]\w*\s+\w+\()", ln):
                            continue
                        if re.search(pat, code_part):
                            flag(name, start, i, rule, ln)
                    if not is_test and re.match(r"\s*@Autowired\s*$", ln):
                        flag(name, start, i, "field-injection", ln)
                    if re.search(r"(public\s+)?class\s+\w+(Request|Response)\b", code_part):
                        flag(name, start, i, "dto-no-record", ln)
                joined = "\n".join(lines)
                for cm in re.finditer(r"@(RestController|Controller)\b.*?class (\w+).*?\n\}", joined, re.S):
                    body = cm.group(0)
                    if "@Transactional" in body:
                        violations.append(f"{name}::{cm.group(2)} [transactional-en-controlador]")
                    if cm.group(1) == "RestController":
                        for pm in re.finditer(r"^\s*(public\s+)?Page<\w+>\s+\w+\(", body, re.M):
                            violations.append(f"{name}::{cm.group(2)} [devuelve-Page-de-Spring-Data] {pm.group(0).strip()}")
                if re.search(r"@Data\b", joined) and "@Entity" in joined:
                    violations.append(f"{name} [lombok-data-en-entidad]")
            if lang == "yaml":
                for i, ln in enumerate(lines):
                    if re.search(r"ddl-auto:\s*(update|create)", ln) or re.search(r"open-in-view:\s*true", ln) \
                            or re.search(r"include:\s*['\"]?\*", ln):
                        flag(name, start, i, "config-insegura", ln)

check(2, "examples-obey-critical-restrictions", not violations, "\n      ".join(violations))

# ------------------------------------------------------------------ Nivel 3
syntax_fails = []
if PROFILE == "nestjs":
    ts_blocks = [{"skill": n, "line": s, "code": c} for n, t in ALL_TEXTS
                 for lang, c, s in code_blocks(t) if lang in ("typescript", "ts")]
    proc = subprocess.run(["node", str(KIT / "parse_ts.js")], input=json.dumps(ts_blocks),
                          capture_output=True, text=True)
    if proc.returncode != 0 or not proc.stdout:
        syntax_fails.append(proc.stderr[:300])
    else:
        parsed = json.loads(proc.stdout)
        syntax_fails += [f"{p['skill']}:{p['line']} -> {p['error']}" for p in parsed if not p["ok"]]
    n_blocks = len(ts_blocks)
else:
    def clean_java(c):
        c = re.sub(r"\{\s*\.\.\.\s*\}", "{}", c)
        c = re.sub(r",\s*\.\.\.\s*\)", ")", c)
        c = re.sub(r"\(\s*\.\.\.\s*\)", "()", c)
        return re.sub(r"^\s*\.\.\.\s*$", "", c, flags=re.M)

    WRAPS = [lambda c: c, lambda c: f"class D__ {{\n{c}\n}}",
             lambda c: f"class D__ {{ void m__() throws Exception {{\n{c}\n}} }}"]

    def segments(code):
        segs, cur, depth = [], [], 0
        for ln in code.split("\n"):
            s = re.sub(r"//.*$", "", ln)
            s = re.sub(r'"[^"]*"', "", s)
            if ln.strip() == "" and depth == 0 and cur:
                segs.append("\n".join(cur))
                cur = []
                continue
            cur.append(ln)
            depth += s.count("{") + s.count("(") - s.count("}") - s.count(")")
        if cur:
            segs.append("\n".join(cur))
        return segs

    tmp = Path(tempfile.mkdtemp())
    units = []  # (block_id, segment_id, wrapper_id, path)
    blocks = [(n, s, clean_java(c)) for n, t in ALL_TEXTS for lang, c, s in code_blocks(t) if lang == "java"]
    for bi, (_, _, code) in enumerate(blocks):
        for si, seg in enumerate([code] + segments(code)):
            for wi, wrap in enumerate(WRAPS):
                p = tmp / f"b{bi}_s{si}_w{wi}.java"
                p.write_text(wrap(seg), encoding="utf-8")
                units.append((bi, si, wi, p))
    listing = tmp / "files.txt"
    listing.write_text("\n".join(str(u[3]) for u in units))
    out = subprocess.run(["java", "-cp", str(KIT), "ParseJava", str(listing)], capture_output=True, text=True).stdout
    status = dict(line.split("\t", 1) for line in out.splitlines() if "\t" in line)
    for bi, (n, s, code) in enumerate(blocks):
        ok_by_seg = {}
        for (b, si, wi, p) in units:
            if b == bi:
                ok_by_seg.setdefault(si, []).append(status.get(str(p), "missing"))
        if any(x == "OK" for x in ok_by_seg[0]):
            continue
        bad = [f"segmento {si}: {v[0]}" for si, v in ok_by_seg.items() if si > 0 and not any(x == "OK" for x in v)]
        if bad:
            syntax_fails.append(f"{n}:{s} -> " + " | ".join(bad))
    yaml_blocks = [(n, s, c) for n, t in ALL_TEXTS for lang, c, s in code_blocks(t) if lang == "yaml"]
    for n, s, c in yaml_blocks:
        try:
            yaml.safe_load(c)
        except yaml.YAMLError as e:
            syntax_fails.append(f"{n}:{s} [yaml] {str(e).splitlines()[0]}")
    n_blocks = f"{len(blocks)} Java + {len(yaml_blocks)} YAML"
check(3, f"syntax ({n_blocks} bloques)", not syntax_fails, "\n      ".join(syntax_fails))

# ------------------------------------------------------------------ Nivel 4
# Afirmaciones verificadas en documentación oficial: el agente no debe contradecirlas.
FACTS = {
    "nestjs": [
        ("ClientProxy.emit() devuelve un Observable caliente (se publica aunque nadie se suscriba); solo send() es frío",
         r"`send\(\)` y `emit\(\)` devuelven Observables \*\*fríos\*\*|\(`send`, `emit`\)[^.]*si no se suscriben"),
        ("Express 5 (Nest 11+) exige comodines con nombre: '{*splat}' en lugar de '*'",
         r"forRoutes\(\s*'\*'\s*\)"),
        ("Con Fastify 5 (Nest 11+) CORS solo permite por defecto los métodos simples: hay que declarar PUT/PATCH/DELETE",
         r"enableCors\(\{(?:(?!methods)[^}])*credentials: true,\s*\}\)"),
    ],
    "spring": [
        ("@MockBean se eliminó en Spring Boot 4 (deprecado en 3.4)", r"@MockBean\s+private"),
        ("El apagado ordenado está activo por defecto desde Spring Boot 3.4", r"shutdown: graceful\s+# por defecto en versiones recientes; compruébalo"),
        ("Desde Boot 3.4, la validación de @ConfigurationProperties solo cascada a objetos anidados con @Valid",
         r"@Validated\` \+ Bean Validation: el arranque falla con un mensaje claro si la configuración es inválida\.$"),
    ],
}[PROFILE]
fact_fails = []
for desc, pat in FACTS:
    hits = [n for n, t in ALL_TEXTS if re.search(pat, t, re.M)]
    if hits:
        fact_fails.append(f"{desc} -> contradicho/impreciso en {hits}")
check(4, f"facts ({len(FACTS)} afirmaciones verificadas)", not fact_fails, "\n      ".join(fact_fails))

# ------------------------------------------------------------------ Informe
total, passed = len(results), sum(1 for r in results if r[2])
for level in (1, 2, 3, 4):
    rows = [r for r in results if r[0] == level]
    print(f"\n=== Nivel {level}: {sum(1 for r in rows if r[2])}/{len(rows)} OK ===")
    for _, tid, good, detail in rows:
        if not good:
            print(f"  FAIL {tid}\n      {detail}")
print(f"\nTOTAL {passed}/{total} comprobaciones superadas")
