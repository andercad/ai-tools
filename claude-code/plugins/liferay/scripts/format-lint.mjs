// Hook PostToolUse: ejecuta Source Formatter (formatSource) del módulo del fichero editado,
// solo si el CLAUDE.md del proyecto declara `format: source-formatter`. En cualquier otro caso no hace nada.
// formatSource trabaja por proyecto Gradle: formatea el módulo entero, no solo el fichero.
import { existsSync, readFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
import path from "node:path";

let input = {};
try {
  input = JSON.parse(readFileSync(0, "utf8"));
} catch {
  process.exit(0);
}
const filePath = input?.tool_input?.file_path;
if (!filePath) process.exit(0);

const root = process.env.CLAUDE_PROJECT_DIR || process.cwd();
const claudeMd = path.join(root, "CLAUDE.md");
if (!existsSync(claudeMd)) process.exit(0);
if (!/^\s*[-*]?\s*format:\s*source-formatter\b/im.test(readFileSync(claudeMd, "utf8"))) process.exit(0);

const abs = path.resolve(filePath);
const rel = path.relative(root, abs).split(path.sep).join("/");

const ignored = ["..", "build/", "bin/", ".gradle/", ".idea/", ".claude/", "node_modules/", "bundles/", "configs/", "dist/"];
if (path.isAbsolute(rel) || ignored.some((p) => rel === p || rel.startsWith(p.endsWith("/") ? p : p + "/"))) {
  process.exit(0);
}
// Solo módulos del workspace (modules/ y themes/); las client extensions usan su propio formateador
if (!/^(modules|themes)\//.test(rel)) process.exit(0);
if (!/\.(java|jsp|jspf|ftl|scss|css|js)$/.test(abs) || !existsSync(abs)) process.exit(0);
if (rel.split("/").some((s) => s === "node_modules" || s === "build" || s === "classes")) process.exit(0);

// Proyecto Gradle más cercano hacia arriba (bnd.bnd o build.gradle), sin salir de la raíz
const findProject = () => {
  let dir = path.dirname(abs);
  for (;;) {
    if (dir !== root && ["bnd.bnd", "build.gradle", "build.gradle.kts"].some((f) => existsSync(path.join(dir, f)))) return dir;
    if (dir === root) return null;
    const parent = path.dirname(dir);
    if (parent === dir || path.relative(root, parent).startsWith("..")) return null;
    dir = parent;
  }
};
const project = findProject();
if (!project) process.exit(0);
if (!existsSync(path.join(root, "settings.gradle")) && !existsSync(path.join(root, "settings.gradle.kts"))) process.exit(0);

const gradlePath = ":" + path.relative(root, project).split(path.sep).join(":");
const win = process.platform === "win32";
const wrapper = path.join(root, win ? "gradlew.bat" : "gradlew");
const tool = existsSync(wrapper) ? (win ? `"${wrapper}"` : `sh "${wrapper}"`) : "gradle";

const res = spawnSync(`${tool} ${gradlePath}:formatSource -q`, {
  cwd: root,
  encoding: "utf8",
  shell: true,
  timeout: 110000,
});
if (res.status !== 0) {
  console.error(res.stderr || res.stdout || "formatSource falló");
  process.exit(2);
}
process.exit(0);
