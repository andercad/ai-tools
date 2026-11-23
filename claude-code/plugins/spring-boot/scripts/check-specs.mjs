// Hook Stop: si el CLAUDE.md del proyecto declara `tests: required`, bloquea el cierre
// cuando hay controladores/servicios/componentes/listeners/advices Java nuevos o modificados sin XTest.java.
import { existsSync, readFileSync } from "node:fs";
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

// Piezas con lógica: controladores, servicios, componentes, advices y listeners de mensajes.
const ARTIFACT = /@(RestController|Controller|Service|Component|RestControllerAdvice|ControllerAdvice|KafkaListener|RabbitListener)\b/;
const REPOSITORY = /@Repository\b/;
// Sin lógica propia: arranque, configuración, entidades, records y tipos de datos
const SKIP_FILE = /(^|\/)(package-info|module-info)\.java$|Application\.java$|(Request|Response|Dto|Properties|Entity|Exception|Config)\.java$/;
const SKIP_CONTENT = /@(Configuration|Entity)\b|^\s*(public\s+)?record\s+\w+/m;
const MAIN = "/src/main/java/";

const stripComments = (s) => s.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/.*$/gm, "");

const missing = [];
for (const line of git.stdout.split("\n")) {
  if (!line.trim()) continue;
  const status = line.slice(0, 2);
  if (status.includes("D")) continue;
  const rel = line.slice(3).replace(/^"|"$/g, "").split(" -> ").pop();
  if (!/\.java$/.test(rel) || SKIP_FILE.test(rel)) continue;
  const relSlash = "/" + rel.split(path.sep).join("/");
  if (!relSlash.includes(MAIN)) continue;
  const abs = path.join(root, rel);
  if (!existsSync(abs)) continue;
  const src = stripComments(readFileSync(abs, "utf8"));
  if (SKIP_CONTENT.test(src)) continue;
  // @Repository solo cuenta si es clase (las interfaces Spring Data no llevan lógica)
  const isRepoClass = REPOSITORY.test(src) && /\bclass\s+\w+/.test(src) && !/\binterface\s+\w+/.test(src);
  if (!ARTIFACT.test(src) && !isRepoClass) continue;
  const base = abs.replace(/\.java$/, "");
  const testBase = base.split(path.sep).join("/").replace(MAIN, "/src/test/java/");
  const found = ["Test", "Tests", "IT"].some((suffix) => existsSync(path.normalize(testBase + suffix + ".java")));
  if (!found) missing.push(rel);
}

if (missing.length) {
  console.error(
    "La política del proyecto exige tests (tests: required). Faltan tests para:\n" +
      missing.map((f) => `- ${f}`).join("\n") +
      "\nCrea el XTest.java de cada clase (en src/test/java, mismo paquete), ejecuta los tests y vuelve a terminar."
  );
  process.exit(2);
}
process.exit(0);
