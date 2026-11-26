// Hook SessionStart: inyecta la skill `angular-conventions` como contexto en proyectos Angular,
// para que apliquen en cualquier flujo (incluidos /spec y /spec-impl), no solo en `angular-dev`.
// Siempre se inyecta en proyectos Angular; si el CLAUDE.md del proyecto define otra cosa, manda el proyecto
// (la propia skill lo indica).
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";

let input = {};
try {
  input = JSON.parse(readFileSync(0, "utf8"));
} catch {
  // sin entrada: sigue con valores por defecto
}

const root = process.env.CLAUDE_PROJECT_DIR || input.cwd || process.cwd();

const isAngular = () => {
  if (existsSync(path.join(root, "angular.json")) || existsSync(path.join(root, "nx.json"))) return true;
  const pkg = path.join(root, "package.json");
  if (!existsSync(pkg)) return false;
  try {
    const j = JSON.parse(readFileSync(pkg, "utf8"));
    return Boolean({ ...j.dependencies, ...j.devDependencies }["@angular/core"]);
  } catch {
    return false;
  }
};
if (!isAngular()) process.exit(0);

const skill = path.join(process.env.CLAUDE_PLUGIN_ROOT || path.resolve(import.meta.dirname, ".."), "skills", "angular-conventions", "SKILL.md");
if (!existsSync(skill)) process.exit(0);
const body = readFileSync(skill, "utf8").replace(/\r\n/g, "\n").replace(/^---\n[\s\S]*?\n---\n/, "").trim();

process.stdout.write(
  JSON.stringify({
    hookSpecificOutput: {
      hookEventName: "SessionStart",
      additionalContext: `Plugin Angular: convenciones de código por defecto (aplícalas al implementar y al redactar specs).\n\n${body}`,
    },
  })
);
