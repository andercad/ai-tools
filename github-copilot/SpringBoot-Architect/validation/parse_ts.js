// Parsea cada bloque TypeScript con el compilador real (solo sintaxis).
// Ruta de TypeScript: variable TS_PATH o el paquete 'typescript' resoluble.
const ts = require(process.env.TS_PATH || 'typescript');
let input = '';
process.stdin.on('data', (d) => (input += d));
process.stdin.on('end', () => {
  const clean = (c) => c
    .replace(/\{\s*\.\.\.\s*\}/g, '{}').replace(/\[\s*\.\.\.\s*\]/g, '[]')
    .replace(/\(\s*\.\.\.\s*\)/g, '()').replace(/^\s*\.\.\.\s*$/gm, '')
    .replace(/\(\.\.\.\)/g, '()');
  const wrappers = [(c) => c, (c) => `class __D {\n${c}\n}`, (c) => `function __f() {\n${c}\n}`,
    (c) => `const __o = [\n${c}\n];`, (c) => `${c}\nclass __Decorated {}`];
  const parses = (c) => wrappers.some((w) =>
    ts.createSourceFile('x.ts', w(c), ts.ScriptTarget.Latest, true, ts.ScriptKind.TS).parseDiagnostics.length === 0);
  const out = JSON.parse(input).map((b) => {
    const code = clean(b.code);
    if (parses(code)) return { skill: b.skill, line: b.line, ok: true };
    const segs = []; let cur = [], depth = 0;
    for (const ln of code.split('\n')) {
      const s = ln.replace(/\/\/.*$/, '').replace(/'[^']*'|`[^`]*`|"[^"]*"/g, '');
      if (ln.trim() === '' && depth === 0 && cur.length) { segs.push(cur.join('\n')); cur = []; continue; }
      cur.push(ln);
      depth += (s.match(/[{(\[]/g) || []).length - (s.match(/[})\]]/g) || []).length;
    }
    if (cur.length) segs.push(cur.join('\n'));
    const bad = segs.filter((s) => s.trim() && !parses(s)).map((s) => s.trim().split('\n')[0].slice(0, 70));
    return bad.length ? { skill: b.skill, line: b.line, ok: false, error: bad.join(' | ') }
                      : { skill: b.skill, line: b.line, ok: true };
  });
  process.stdout.write(JSON.stringify(out));
});
