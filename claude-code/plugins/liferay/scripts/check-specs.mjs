// Hook Stop: si el CLAUDE.md del proyecto declara `tests: required`, bloquea el cierre
// cuando hay componentes Java con lógica (@Component) nuevos o modificados sin XTest.java.
import { existsSync, readFileSync, readdirSync } from "node:fs";
import { spawnSync } from "node:child_process";
import path from "node:path";

let input = {};
try {
  input = JSON.parse(readFileSync(0, "utf8"));
} catch {
  process.exit(0);
}
// Una sola oportunidad por parada para evitar bucles
if (input.stop_hook_active) process.exit(0);

const root = process.env.CLAUDE_PROJECT_DIR || input.cwd || process.cwd();
const claudeMd = path.join(root, "CLAUDE.md");
if (!existsSync(claudeMd)) process.exit(0);
const policy = readFileSync(claudeMd, "utf8");
if (!/^\s*[-*]?\s*tests:\s*required\b/im.test(policy)) process.exit(0);

const git = spawnSync("git", ["status", "--porcelain", "--untracked-files=all"], {
  cwd: root,
  encoding: "utf8",
});
if (git.status !== 0) process.exit(0);

const MAIN = "/src/main/java/";
// Sin lógica propia: constantes, claves de portlet, configuración tipada, package-info
// y código generado por Service Builder (base, persistence, http, ModelImpl, CacheModel, entidades *Impl)
const SKIP_FILE =
  /(^|\/)(package-info|module-info)\.java$|PortletKeys\.java$|Constants\.java$|Configuration\.java$|(BaseImpl|ModelImpl|CacheModel)\.java$/;
const SKIP_PATH = /\/(service\/base|service\/persistence|service\/http|model\/impl)\//;
const SKIP_CONTENT = /@Meta\.OCD\b/;
const COMPONENT = /@Component\b/;
// Hay que ignorar lo que no es una clase (interfaces, anotaciones, enums)
const IS_CLASS = /\b(?:public\s+|abstract\s+|final\s+)*class\s+\w+/;

const stripComments = (s) => s.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/.*$/gm, "");

// Índice perezoso de tests del workspace (por nombre), para módulos `-test` separados
const IGNORED_DIRS = new Set(["node_modules", "build", "bin", ".gradle", ".git", "bundles", "dist", "target", ".idea", ".claude"]);
let testIndex = null;
const buildIndex = () => {
  const names = new Set();
  const walk = (dir) => {
    let entries = [];
    try {
      entries = readdirSync(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const e of entries) {
      if (e.isDirectory()) {
        if (!IGNORED_DIRS.has(e.name)) walk(path.join(dir, e.name));
      } else if (/(Test|Tests|IT)\.java$/.test(e.name)) {
        names.add(e.name);
      }
    }
  };
  walk(root);
  return names;
};

const missing = [];
for (const line of git.stdout.split("\n")) {
  if (!line.trim()) continue;
  const status = line.slice(0, 2);
  if (status.includes("D")) continue;
  const rel = line.slice(3).replace(/^"|"$/g, "").split(" -> ").pop();
  if (!/\.java$/.test(rel) || SKIP_FILE.test(rel)) continue;
  const relSlash = "/" + rel.split(path.sep).join("/");
  if (!relSlash.includes(MAIN) || SKIP_PATH.test(relSlash)) continue;
  const abs = path.join(root, rel);
  if (!existsSync(abs)) continue;
  const src = stripComments(readFileSync(abs, "utf8"));
  if (SKIP_CONTENT.test(src) || !COMPONENT.test(src) || !IS_CLASS.test(src)) continue;
  const base = abs.replace(/\.java$/, "");
  const baseSlash = base.split(path.sep).join("/");
  const stem = path.basename(base);
  // 1) mismo módulo: src/test/java o src/testIntegration/java con la misma ruta de paquete
  const sameModule = ["test", "testIntegration"].some((dir) =>
    ["Test", "Tests", "IT"].some((suffix) =>
      existsSync(path.normalize(baseSlash.replace(MAIN, `/src/${dir}/java/`) + suffix + ".java"))
    )
  );
  if (sameModule) continue;
  // 2) cualquier módulo del workspace (p. ej. un módulo `-test`) con el mismo nombre de test
  testIndex ??= buildIndex();
  if (["Test", "Tests", "IT"].some((suffix) => testIndex.has(stem + suffix + ".java"))) continue;
  missing.push(rel);
}

if (missing.length) {
  console.error(
    "La política del proyecto exige tests (tests: required). Faltan tests para:\n" +
      missing.map((f) => `- ${f}`).join("\n") +
      "\nCrea el XTest.java de cada componente (src/test/java, mismo paquete, o en el módulo -test del proyecto), ejecuta los tests y vuelve a terminar."
  );
  process.exit(2);
}
process.exit(0);
