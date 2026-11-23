// Hook Stop: si el CLAUDE.md del proyecto declara `tests: required`, bloquea el cierre
// cuando hay controladores/servicios/resolvers/guards/pipes/interceptores/filtros nuevos o modificados sin .spec.ts.
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

// Piezas con lógica: providers, controladores, resolvers y filtros (@Catch). Guards, pipes e interceptores son @Injectable.
const ARTIFACT = /@(Injectable|Controller|Resolver|Catch)\s*\(/;
const SKIP = /\.(spec|e2e-spec|d|module|dto|entity|model|input|args|interface|constants|config)\.ts$|(^|\/)(main|index)\.ts$|(^|\/)(migrations|test|e2e)\//;
const missing = [];
for (const line of git.stdout.split("\n")) {
  if (!line.trim()) continue;
  const status = line.slice(0, 2);
  if (status.includes("D")) continue;
  const rel = line.slice(3).replace(/^"|"$/g, "").split(" -> ").pop();
  if (!/\.ts$/.test(rel) || SKIP.test(rel)) continue;
  const abs = path.join(root, rel);
  if (!existsSync(abs)) continue;
  if (!ARTIFACT.test(readFileSync(abs, "utf8"))) continue;
  const spec = abs.replace(/\.ts$/, ".spec.ts");
  if (!existsSync(spec)) missing.push(rel);
}

if (missing.length) {
  console.error(
    "La política del proyecto exige tests (tests: required). Faltan specs para:\n" +
      missing.map((f) => `- ${f}`).join("\n") +
      "\nCrea el .spec.ts de cada fichero, ejecuta los tests y vuelve a terminar."
  );
  process.exit(2);
}
process.exit(0);
