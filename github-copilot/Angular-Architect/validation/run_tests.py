"""Banco de pruebas de los agentes Angular Architect y NestJS Architect.

Nivel 1  Estructura: frontmatter, routing agente <-> skills, referencias cruzadas.
Nivel 2  Coherencia: los ejemplos cumplen las restricciones críticas del propio agente,
         incluidas las reglas de monorepo.
Nivel 3  Sintaxis: cada bloque TypeScript se parsea con el compilador de TypeScript;
         los bloques YAML, con PyYAML.
Nivel 4  Hechos: afirmaciones contrastadas con documentación oficial que el agente
         debe contener o no debe contradecir.

Uso: python3 run_tests.py <angular|nestjs> <ruta-del-agente>
Requiere Node, el paquete `typescript` (variable TS_PATH si no está en la ruta de módulos) y PyYAML.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

PROFILE = sys.argv[1]
ROOT = Path(sys.argv[2] if len(sys.argv) > 2 else "..").resolve()
KIT = Path(__file__).resolve().parent
PREFIX = {"angular": "angular-", "nestjs": "nestjs-"}[PROFILE]
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
        if "❌" in ln or "Evitar" in ln or "nunca hacer" in ln:
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
    check(1, f"{name}.name-format", bool(re.fullmatch(r"[a-z0-9-]{1,64}", sfm.get("name", ""))))
    desc = sfm.get("description", "")
    check(1, f"{name}.description<=1024", 0 < len(desc) <= 1024, f"{len(desc)} chars")
    check(1, f"{name}.has-trigger-words", "Usar cuando" in desc)
    # Ambigüedad en repos con varios agentes: la descripción nombra la tecnología
    side = "Frontend Angular" if PROFILE == "angular" else "Backend NestJS"
    check(1, f"{name}.description-starts-with-side", desc.startswith(side))

routed = set(re.findall(rf"skill `({PREFIX}[a-z0-9-]+)`", agent_text))
check(1, "routing.all-skills-routed", routed == skill_names,
      f"sin ruta: {sorted(skill_names - routed)} | ruta sin skill: {sorted(routed - skill_names)}")
NOT_SKILLS = {"angular-eslint", "nestjs-pino", "nestjs-cls"}  # paquetes npm, no skills
for name, text in ALL_TEXTS:
    refs = {r for r in re.findall(rf"`({PREFIX}[a-z0-9]+(?:-[a-z0-9]+)*)`", text)} - NOT_SKILLS
    broken = sorted(refs - skill_names)
    check(1, f"{name}.cross-refs", not broken, f"rotas: {broken}")

# ------------------------------------------------------------------ Nivel 2
violations = []


def flag(name, start, i, rule, line):
    violations.append(f"{name}:{start + i + 1} [{rule}] {line.strip()[:95]}")


# Reglas de monorepo comunes a los dos perfiles (solo en bloques TypeScript)
MONOREPO_RULES = {
    "deep-import": r"from '@[\w-]+/[\w/-]*/src/",
    "cross-project-relative": r"from '(\.\./){2,}(libs|apps|projects)/",
}

if PROFILE == "angular":
    TS_RULES = {
        "any": r"(:\s*any\b|<any>|\bas any\b)",
        "decorator-io": r"@(Input|Output)\(",
        "host-decorators": r"@(HostBinding|HostListener)\b",
        "standalone-true": r"standalone:\s*true",
        "mutate": r"\.mutate\(",
        "console.log": r"console\.log\(",
        "ctor-injection": r"constructor\s*\(\s*(private|public|protected|readonly)",
        "writable-signal-not-private": r"^\s*(public |protected )?readonly \w+ = (signal|linkedSignal)[<(]",
        "front-imports-backend": r"from '@[\w-]+/api[/']|from '@nestjs/",
        **MONOREPO_RULES,
    }
    HTML_RULES = {
        "legacy-control-flow": r"\*ng(If|For|Switch)\b",
        "ngClass/ngStyle": r"\[(ngClass|ngStyle)\]",
        "template-new-Date": r"\{\{[^}]*new Date",
        "template-writes-signal": r"\(\w[\w.]*\)=\"[^\"]*\.(set|update)\(",
    }
else:
    TS_RULES = {
        "any": r"(:\s*any\b|<any>|\bas any\b)",
        "console.log": r"console\.log\(",
        "res-sin-passthrough": r"@Res\(\)",
        "useGlobalGuards": r"app\.useGlobalGuards\(",
        "synchronize-true": r"synchronize:\s*true",
        "wildcard-express4": r"forRoutes\(\s*'\*'\s*\)|@(Get|Post|All)\('[^']*/\*'\)",
        **MONOREPO_RULES,
    }
    HTML_RULES = {}

for name, text in skill_texts.items():
    for lang, code, start in code_blocks(text):
        lines = code.splitlines()
        ts = lang in ("typescript", "ts")
        rules = {**TS_RULES, **HTML_RULES} if ts else (HTML_RULES if lang == "html" else {})
        for i, ln in enumerate(lines):
            if re.match(r"\s*(<!--|\*|/\*)", ln):
                continue
            code_part = ln.split("//")[0] if ts else ln
            if is_counterexample(lines, i):
                continue
            for rule, pat in rules.items():
                if re.search(pat, code_part):
                    flag(name, start, i, rule, ln)
            if PROFILE == "nestjs" and ts:
                if "process.env" in code_part and name != "nestjs-config":
                    flag(name, start, i, "process.env-fuera-de-config", ln)
                if re.search(r"throw new Error\(", code_part) and name != "nestjs-config":
                    flag(name, start, i, "throw-Error-generico", ln)
        # Contratos compartidos: solo tipos, sin decoradores ni dependencias de servidor
        if ts and lines and "api-contracts" in lines[0]:
            for i, ln in enumerate(lines):
                if re.match(r"\s*@\w+", ln) or "from '@nestjs" in ln or "class-validator" in ln:
                    flag(name, start, i, "contrato-con-dependencias-de-servidor", ln)
        if PROFILE == "nestjs" and ts:
            for i, ln in enumerate(lines):
                if re.match(r"\s+(readonly\s+)?\w+:\s*[^=;(]+;\s*(//.*)?$", ln) and i > 0 \
                        and lines[i - 1].strip().startswith("@") and not is_counterexample(lines, i):
                    flag(name, start, i, "propiedad-sin-!", ln)
        if lang in ("html", "typescript", "ts"):
            joined = "\n".join(lines)
            for m in re.finditer(r"<button\b([^>]*)>", joined, re.S):
                if "type=" not in m.group(1):
                    violations.append(f"{name}:{start + joined[: m.start()].count(chr(10)) + 1} [button-sin-type]")
            for m in re.finditer(r"@for\s*\(([^\n]*)", joined):
                idx = joined[: m.start()].count("\n")
                if "track" not in m.group(1) and not is_counterexample(lines, idx):
                    violations.append(f"{name}:{start + idx + 1} [for-sin-track]")
check(2, "examples-obey-critical-restrictions", not violations, "\n      ".join(violations))

if PROFILE == "angular":
    ORDER = [
        ("inject", r"=\s*inject\("),
        ("input", r"=\s*input(\.required)?[<(]"),
        ("output", r"=\s*output[<(]"),
        ("model", r"=\s*model[<(]"),
        ("query", r"=\s*(viewChild|viewChildren|contentChild|contentChildren)(\.required)?[<(]"),
        ("signal", r"=\s*(signal|linkedSignal)[<(]|asReadonly\(\)"),
        ("form", r"=\s*this\.fb\."),
        ("computed", r"=\s*computed\(|=\s*toSignal\(|=\s*(rxResource|httpResource|resource)\("),
        ("effect", r"=\s*effect\(|=\s*afterNextRender\("),
        ("other-prop", r"^\s*(private |protected |public )?(readonly |static )*[\w$]+[?!]?\s*(:[^=(]+)?(=|;)"),
        ("lifecycle", r"^\s*ng(OnInit|OnDestroy|OnChanges|AfterViewInit|AfterContentInit)\("),
        ("public-method", r"^\s*(public\s+|protected\s+)?(async\s+)?[a-z]\w*\s*\([^)]*\)\s*(:[^{]+)?\{"),
        ("private-method", r"^\s*private\s+(async\s+)?[a-z]\w*\s*\([^)]*\)\s*(:[^{]+)?\{"),
    ]
    RANK = {k: i for i, (k, _) in enumerate(ORDER)}
    order_issues, missing_onpush = [], []
    for name, text in skill_texts.items():
        for lang, code, start in code_blocks(text):
            if lang not in ("typescript", "ts"):
                continue
            for cm in re.finditer(r"@(Component|Directive)\(\{(.*?)\}\)\s*export (default )?class (\w+)[^{]*\{(.*?)\n\}", code, re.S):
                kind_dec, meta, cls, body = cm.group(1), cm.group(2), cm.group(4), cm.group(5)
                if kind_dec == "Component" and "..." not in meta and "changeDetection" not in meta:
                    missing_onpush.append(f"{name}::{cls}")
                depth, last = 0, -1
                for raw in body.splitlines():
                    s = raw.strip()
                    if depth == 0 and s and not s.startswith(("//", "*", "/*", "@")):
                        kind = next((k for k, pat in ORDER if re.search(pat, raw)), None)
                        if kind:
                            if RANK[kind] < last:
                                order_issues.append(f"{name}::{cls} '{kind}' después de '{ORDER[last][0]}' -> {s[:70]}")
                            last = max(last, RANK[kind])
                    depth = max(depth + raw.count("{") - raw.count("}"), 0)
    check(2, "examples-follow-member-order", not order_issues, "\n      ".join(order_issues))
    check(2, "full-components-declare-OnPush(v21)", not missing_onpush, ", ".join(missing_onpush))
else:
    order_issues = []
    for name, text in skill_texts.items():
        for lang, code, start in code_blocks(text):
            if lang not in ("typescript", "ts"):
                continue
            for cm in re.finditer(r"@(Controller|Resolver)\([^)]*\)\s*export class (\w+).*?\n\}", code, re.S):
                seen_write = False
                for dm in re.finditer(r"@(Get|Post|Put|Patch|Delete|Query|Mutation|ResolveField)\(", cm.group(0)):
                    if dm.group(1) in ("Post", "Put", "Patch", "Delete", "Mutation", "ResolveField"):
                        seen_write = True
                    elif seen_write:
                        order_issues.append(f"{name}::{cm.group(2)} lectura '@{dm.group(1)}' después de escritura")
    check(2, "examples-follow-member-order", not order_issues, "\n      ".join(order_issues))

# ------------------------------------------------------------------ Nivel 3
ts_blocks = [{"skill": n, "line": s, "code": c} for n, t in ALL_TEXTS
             for lang, c, s in code_blocks(t) if lang in ("typescript", "ts")]
proc = subprocess.run(["node", str(KIT / "parse_ts.js")], input=json.dumps(ts_blocks),
                      capture_output=True, text=True)
syntax_fails = []
if proc.returncode != 0 or not proc.stdout:
    syntax_fails.append(proc.stderr[:300])
else:
    syntax_fails += [f"{p['skill']}:{p['line']} -> {p['error']}" for p in json.loads(proc.stdout) if not p["ok"]]
yaml_blocks = [(n, s, c) for n, t in ALL_TEXTS for lang, c, s in code_blocks(t) if lang == "yaml"]
for n, s, c in yaml_blocks:
    try:
        yaml.safe_load(c)
    except yaml.YAMLError as e:
        syntax_fails.append(f"{n}:{s} [yaml] {str(e).splitlines()[0]}")
check(3, f"syntax ({len(ts_blocks)} TS + {len(yaml_blocks)} YAML bloques)", not syntax_fails, "\n      ".join(syntax_fails))

# ------------------------------------------------------------------ Nivel 4
# (descripción, skill o None = cualquiera, patrón, debe_aparecer)
FACTS = {
    "angular": [
        ("En Nx se actualiza con nx migrate, no con ng update", "angular-environment", r"nx migrate", True),
        ("Con Angular en Nx, una versión mayor cada vez es obligatorio", "angular-monorepo", r"una versión mayor cada vez es obligatorio", True),
        ("Nx enlaza proyectos con aliases de TS o con workspaces + referencias de proyecto", "angular-monorepo", r"Workspaces del gestor de paquetes", True),
        ("Las librerías de workspace de Nx se compilan con la aplicación (no buildable por defecto)", "angular-monorepo", r"se compila junto con la aplicación", True),
        ("ng new --no-create-application crea un workspace vacío", "angular-monorepo", r"ng new \S+ --no-create-application", True),
        ("Hidratación incremental por defecto desde v22", "angular-ssr", r"activada por defecto con `provideClientHydration\(\)` desde v22", True),
        ("En un monorepo Nx no se usa ng update como comando", "angular-monorepo", r"^ng update", False),
        ("En un monorepo Nx se usa nx, no ng, para las tareas", "angular-monorepo", r"^ng (build|test|serve|lint) [\w-]+\s*$(?![\s\S]*## Monorepo Nx)", False),
    ],
    "nestjs": [
        ("ClientProxy.emit() es caliente; solo send() es frío", None,
         r"`send\(\)` y `emit\(\)` devuelven Observables \*\*fríos\*\*|\(`send`, `emit`\)[^.]*si no se suscriben", False),
        ("Express 5 (Nest 11+) exige comodines con nombre", None, r"forRoutes\(\s*'\*'\s*\)", False),
        ("Fastify 5: CORS solo métodos simples por defecto", None, r"enableCors\(\{(?:(?!methods)[^}])*credentials: true,\s*\}\)", False),
        ("Modo monorepo del Nest CLI: \"monorepo\": true en nest-cli.json", "nestjs-monorepo", r'"monorepo": true', True),
        ("Generadores de @nx/nest: indicar --project", "nestjs-monorepo", r"--project", True),
        ("Docker en Nx: generatePackageJson o flujo de poda según el modelo de enlace", "nestjs-monorepo", r"generatePackageJson.*\n.*poda|generatePackageJson[^\n]*poda", True),
    ],
}[PROFILE]
fact_fails = []
for desc, skill, pat, must in FACTS:
    texts = [(skill, skill_texts[skill])] if skill else ALL_TEXTS
    hits = [n for n, t in texts if re.search(pat, t, re.M)]
    if must and not hits:
        fact_fails.append(f"FALTA: {desc} (en {skill})")
    if not must and hits:
        fact_fails.append(f"CONTRADICHO: {desc} -> {hits}")
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
