// Hook PostToolUse: formatea el .java editado con Spotless, solo si el proyecto lo tiene configurado.
// Sin Spotless (o sin build Maven/Gradle) no hace nada y no bloquea.
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
const abs = path.resolve(filePath);
const rel = path.relative(root, abs).split(path.sep).join("/");

const ignored = ["..", "target/", "build/", ".gradle/", ".idea/", ".claude/", "node_modules/"];
if (path.isAbsolute(rel) || ignored.some((p) => rel === p || rel.startsWith(p.endsWith("/") ? p : p + "/"))) {
  process.exit(0);
}
if (!/\.java$/.test(abs) || !existsSync(abs)) process.exit(0);

// Build más cercano hacia arriba (sin salir de la raíz del proyecto)
const findBuild = () => {
  let dir = path.dirname(abs);
  for (;;) {
    for (const f of ["pom.xml", "build.gradle.kts", "build.gradle"]) {
      if (existsSync(path.join(dir, f))) return { dir, file: f };
    }
    if (dir === root) return null;
    const parent = path.dirname(dir);
    if (parent === dir || path.relative(root, parent).startsWith("..")) return null;
    dir = parent;
  }
};
const build = findBuild();
if (!build) process.exit(0);

const win = process.platform === "win32";
const text = readFileSync(path.join(build.dir, build.file), "utf8");

// Wrapper del propio proyecto (en el módulo o en la raíz); si no, mvn/gradle del PATH
const tool = (wrapper, wrapperWin, fallback) => {
  for (const dir of [build.dir, root]) {
    const w = path.join(dir, win ? wrapperWin : wrapper);
    if (existsSync(w)) return win ? `"${w}"` : `sh "${w}"`;
  }
  return fallback;
};

let cmd;
if (build.file === "pom.xml") {
  if (!text.includes("spotless-maven-plugin")) process.exit(0);
  // spotlessFiles: regex (String#matches) contra la ruta absoluta
  const regex = abs.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  cmd = `${tool("mvnw", "mvnw.cmd", "mvn")} spotless:apply "-DspotlessFiles=${regex}" -q`;
} else {
  if (!text.includes("com.diffplug.spotless")) process.exit(0);
  // spotlessIdeHook: ruta absoluta del fichero
  cmd = `${tool("gradlew", "gradlew.bat", "gradle")} spotlessApply "-PspotlessIdeHook=${abs}" -q`;
}

const res = spawnSync(cmd, { cwd: build.dir, encoding: "utf8", shell: true });
if (res.status !== 0) {
  console.error(res.stderr || res.stdout || "Spotless falló");
  process.exit(2);
}
process.exit(0);
