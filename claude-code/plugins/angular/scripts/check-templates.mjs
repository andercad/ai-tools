// Hook Stop: bloquea el cierre si un componente nuevo o modificado usa `template:` inline
// en lugar de `templateUrl`. Se desactiva con `templates: inline` en el CLAUDE.md del proyecto.
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
if (existsSync(claudeMd) && /^\s*[-*]?\s*templates:\s*inline\b/im.test(readFileSync(claudeMd, "utf8"))) {
  process.exit(0);
}

const git = spawnSync("git", ["status", "--porcelain", "--untracked-files=all"], {
  cwd: root,
  encoding: "utf8",
});
if (git.status !== 0) process.exit(0);

// Propiedad `template:` de primer nivel en el decorador (no `templateUrl`, no dentro de strings)
const INLINE = /^\s*template\s*:/m;
const offenders = [];
for (const line of git.stdout.split("\n")) {
  if (!line.trim()) continue;
  if (line.slice(0, 2).includes("D")) continue;
  const rel = line.slice(3).replace(/^"|"$/g, "").split(" -> ").pop();
  if (!/\.ts$/.test(rel) || /\.(spec|d|stories)\.ts$/.test(rel)) continue;
  const abs = path.join(root, rel);
  if (!existsSync(abs)) continue;
  const text = readFileSync(abs, "utf8");
  if (!/@Component\s*\(/.test(text)) continue;
  if (INLINE.test(text)) offenders.push(rel);
}

if (offenders.length) {
  console.error(
    "Convención del plugin: los componentes usan fichero .html (templateUrl), no template inline. Revisa:\n" +
      offenders.map((f) => `- ${f}`).join("\n") +
      "\nMueve el template a un .html junto al componente, usa templateUrl y vuelve a terminar."
  );
  process.exit(2);
}
process.exit(0);
