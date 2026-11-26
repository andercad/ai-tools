// Hook Stop: bloquea el cierre si las rutas nuevas o modificadas incumplen la convención del plugin:
//  - rutas siempre lazy (`loadComponent` / `loadChildren`), nunca `component:` ni `children: <identificador>` importado;
//  - `loadComponent` apunta a una página en `pages/` y sin `.then` (páginas con `export default`);
//  - un `<funcionalidad>.routes.ts` con una sola ruta sobra: la ruta va en `app.routes.ts`;
//  - los componentes de `pages/` se exportan con `export default class`.
// Se desactiva con `routes: free` en el CLAUDE.md del proyecto.
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
if (existsSync(claudeMd) && /^\s*[-*]?\s*routes:\s*free\b/im.test(readFileSync(claudeMd, "utf8"))) {
  process.exit(0);
}

const git = spawnSync("git", ["status", "--porcelain", "--untracked-files=all"], {
  cwd: root,
  encoding: "utf8",
});
if (git.status !== 0) process.exit(0);

const stripComments = (s) => s.replace(/\/\*[\s\S]*?\*\//g, "").replace(/^\s*\/\/.*$/gm, "");
const offenders = [];
const add = (file, msg) => offenders.push(`- ${file}: ${msg}`);

for (const line of git.stdout.split("\n")) {
  if (!line.trim()) continue;
  if (line.slice(0, 2).includes("D")) continue;
  const rel = line.slice(3).replace(/^"|"$/g, "").split(" -> ").pop().replace(/\\/g, "/");
  if (!/\.ts$/.test(rel) || /\.(spec|d|stories)\.ts$/.test(rel)) continue;
  const abs = path.join(root, rel);
  if (!existsSync(abs)) continue;
  const raw = readFileSync(abs, "utf8");

  // Páginas: `export default class`
  if (/(^|\/)pages\//.test(rel) && /@Component\s*\(/.test(raw) && !/export\s+default\s+class\b/.test(raw)) {
    add(rel, "las páginas (`pages/`) se exportan con `export default class`");
  }

  if (!/\.routes\.ts$/.test(rel)) continue;
  const text = stripComments(raw);
  const isApp = /(^|\/)app\.routes\.ts$/.test(rel);

  if (/\bcomponent\s*:/.test(text)) {
    add(rel, "usa `component:` (carga eager); usa `loadComponent: () => import('@<funcionalidad>/pages/...')`");
  }
  for (const m of text.matchAll(/loadComponent\s*:\s*\(\s*\)\s*=>\s*import\(\s*['"]([^'"]+)['"]\s*\)(\s*\.then)?/g)) {
    if (!/\/pages\//.test(m[1])) add(rel, `\`loadComponent\` carga ${m[1]}, que no está en \`pages/\``);
    if (m[2]) add(rel, `\`loadComponent\` con \`.then\` (${m[1]}); la página usa \`export default\` y se importa sin \`.then\``);
  }
  if (/\bchildren\s*:\s*[A-Za-z_$]/.test(text)) {
    add(rel, "`children:` con un identificador importado estáticamente; usa `loadChildren: () => import(...)`");
  }
  if (!isApp) {
    // Rutas reales (sin contar redirects): una sola ruta no justifica un fichero de segundo nivel
    const paths = (text.match(/\bpath\s*:/g) || []).length;
    const redirects = (text.match(/\bredirectTo\s*:/g) || []).length;
    if (paths - redirects === 1) {
      add(rel, "tiene una sola ruta: no crees router de segundo nivel; registra la página con `loadComponent` en `app.routes.ts` y borra este fichero");
    }
  }
}

if (offenders.length) {
  console.error(
    "Convención de rutas del plugin (skill angular-conventions §Rutas). Revisa:\n" +
      offenders.join("\n") +
      "\nCorrige y vuelve a terminar. Si el proyecto no quiere esta regla, `routes: free` en su CLAUDE.md."
  );
  process.exit(2);
}
process.exit(0);
