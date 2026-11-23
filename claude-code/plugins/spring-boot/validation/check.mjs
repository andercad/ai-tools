// Validación estática del plugin (sin dependencias). Uso: node validation/check.mjs
import { readdirSync, readFileSync, existsSync, statSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
let fails = 0;
let checks = 0;
const check = (ok, msg) => {
  checks++;
  if (!ok) {
    fails++;
    console.error(`FAIL: ${msg}`);
  }
};

const frontmatter = (text) => {
  const m = text.replace(/\r\n/g, "\n").match(/^---\n([\s\S]*?)\n---\n/);
  if (!m) return null;
  const out = {};
  for (const line of m[1].split("\n")) {
    const k = line.match(/^([A-Za-z_-]+):\s*(.*)$/);
    if (k) out[k[1]] = k[2].replace(/^['"]|['"]$/g, "");
  }
  return out;
};
const mojibake = /Ã[¡-¿]|â€|�/;
const skillsDir = path.join(root, "skills");
const agentsDir = path.join(root, "agents");
// Nombres válidos que no son skills: agentes, starters y librerías de Spring
const nonSkills = [
  "spring-boot-dev",
  "spring-boot-architect",
  "spring-boot",
  "spring-modulith",
  "spring-security-test",
  "spring-security-crypto",
  "spring-cloud",
];
const isKnown = (n) => existsSync(path.join(skillsDir, n)) || nonSkills.includes(n);

const walk = (dir) =>
  readdirSync(dir).flatMap((f) => {
    const p = path.join(dir, f);
    return statSync(p).isDirectory() ? walk(p) : [p];
  });

// Skills
for (const name of readdirSync(skillsDir)) {
  const dir = path.join(skillsDir, name);
  if (!statSync(dir).isDirectory()) continue;
  const file = path.join(dir, "SKILL.md");
  check(existsSync(file), `${name}: falta SKILL.md`);
  if (!existsSync(file)) continue;
  const text = readFileSync(file, "utf8");
  const fm = frontmatter(text);
  check(fm, `${name}: sin frontmatter`);
  if (!fm) continue;
  check(fm.name === name, `${name}: name '${fm.name}' != carpeta`);
  check(fm.description && fm.description.length > 40, `${name}: description vacía o corta`);
  check((fm.description || "").length <= 1024, `${name}: description > 1024 caracteres`);
  if (!fm["disable-model-invocation"]) {
    check(/Usar /.test(fm.description), `${name}: description sin disparador "Usar ..."`);
  }
  check(text.split("\n").length <= 500, `${name}: SKILL.md > 500 líneas`);
  // enlaces relativos
  for (const m of text.matchAll(/\]\(((?:references|reference|templates|scripts)\/[^)]+)\)/g)) {
    check(existsSync(path.join(dir, m[1])), `${name}: enlace roto ${m[1]}`);
  }
  // todos los ficheros de la skill: mojibake, restos de Copilot y referencias a skills inexistentes
  for (const f of walk(dir).filter((p) => p.endsWith(".md"))) {
    const t = readFileSync(f, "utf8");
    const rel = path.relative(root, f);
    check(!mojibake.test(t), `${rel}: mojibake`);
    check(!/guidelines\/coding-guidelines|applyTo|GitHub Copilot|\.github\//.test(t), `${rel}: resto de Copilot`);
    for (const m of t.matchAll(/`(spring-[a-z-]+)`/g)) {
      check(isKnown(m[1]), `${rel}: skill inexistente ${m[1]}`);
    }
  }
}

// Agentes
for (const f of readdirSync(agentsDir)) {
  const text = readFileSync(path.join(agentsDir, f), "utf8");
  const fm = frontmatter(text);
  check(fm && fm.name && fm.description, `agente ${f}: falta name/description`);
  if (!fm) continue;
  check(fm.name === f.replace(/\.md$/, ""), `agente ${f}: name != fichero`);
  check(!mojibake.test(text), `agente ${f}: mojibake`);
  if (fm.name === "spring-boot-architect") {
    check(!/\b(Bash|Edit|Write)\b/.test(fm.tools || ""), "spring-boot-architect debe ser solo lectura");
  }
  for (const m of text.matchAll(/`(spring-[a-z-]+)`/g)) {
    check(isKnown(m[1]), `agente ${f}: skill inexistente ${m[1]}`);
  }
  const block = text.match(/^skills:\s*\n((?:\s+-\s+.+\n)+)/m);
  for (const m of block ? block[1].matchAll(/-\s+(\S+)/g) : []) {
    check(existsSync(path.join(skillsDir, m[1])), `agente ${f}: skill precargada inexistente ${m[1]}`);
  }
}

// Hooks
const hooks = JSON.parse(readFileSync(path.join(root, "hooks", "hooks.json"), "utf8"));
check(hooks.hooks && hooks.hooks.PostToolUse, "hooks.json: falta wrapper hooks/PostToolUse");
check(hooks.hooks && hooks.hooks.Stop, "hooks.json: falta hook Stop");
for (const s of ["format-lint.mjs", "check-specs.mjs"]) {
  check(existsSync(path.join(root, "scripts", s)), `falta scripts/${s}`);
}

// Marketplace
const plugin = JSON.parse(readFileSync(path.join(root, ".claude-plugin", "plugin.json"), "utf8"));
const market = JSON.parse(readFileSync(path.join(root, "..", "..", ".claude-plugin", "marketplace.json"), "utf8"));
const names = new Set(market.plugins.map((p) => p.name));
check(names.has(plugin.name), `plugin '${plugin.name}' no está en marketplace.json`);
for (const d of plugin.dependencies || []) {
  const n = typeof d === "string" ? d : d.name;
  check(names.has(n), `dependencia '${n}' no está en marketplace.json`);
}

console.log(fails ? `${fails} fallos de ${checks} comprobaciones` : `OK: ${checks} comprobaciones superadas`);
process.exit(fails ? 1 : 0);
