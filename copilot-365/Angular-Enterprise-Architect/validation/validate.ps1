# Uso:  powershell -NoProfile -ExecutionPolicy Bypass -File validation\validate.ps1 [-Build]
# -Build regenera los ZIP de skill-packages/ desde skills/ antes de validar.
param([switch]$Build)

Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$utf8 = New-Object System.Text.UTF8Encoding($false)
$errors = New-Object System.Collections.Generic.List[string]
$checks = 0
$mojibake = [string][char]0xC3 + '|' + [char]0xE2 + [char]0x20AC
function Check($ok, $msg) { $script:checks++; if (-not $ok) { $script:errors.Add($msg) } }
function Read-Text($p) { [IO.File]::ReadAllText($p, $utf8) }

# ---------- Configuración específica de este agente ----------
$prefix = 'angular-'
$sharedResources = 'decision_matrix.py', 'eu-regulatory-map.md'
$required = @{
    'angular-architecture-assessment'   = @('hechos', 'evidencia', 'deuda', 'descubrimiento', 'blocker', 'roadmap')
    'angular-architecture'              = @('feature', 'microfrontends', 'monorepo', 'lazy', 'límites', 'i18n', 'design system', 'fitness function')
    'angular-reactivity-state'          = @('signals', 'rxjs', 'computed', 'linkedsignal', 'effect', 'switchmap', 'fuente de verdad', 'zoneless', 'formularios')
    'angular-rendering-performance'     = @('ssr', 'ssg', 'hydration', 'lcp', 'inp', 'baseline', 'cdn', 'build once', 'rollback')
    'angular-quality-security'          = @('wcag', 'xss', 'csp', 'trusted types', 'contrato', 'sbom', 'el frontend no autoriza', 'quality gates', 'contenido generado por ia', 'eu-regulatory-map.md')
    'angular-backend-integration'       = @('bff', 'pkce', 'openapi', 'idempotencia', 'problem details', 'interceptores', 'cors', 'timeouts', 'ia generativa', 'streaming')
    'angular-liferay-integration'       = @('custom element', 'client extension', 'headless', 'oauth2', 'instancias', 'iframe', 'csp', 'client-extension.yaml')
    'angular-modernization-governance'  = @('ng update', 'adr', 'strangler', 'standalone', 'zoneless', 'fitness functions', 'rollback', 'caracterización', 'decision_matrix.py')
}
# Escenarios de enrutamiento: la skill esperada debe contener el disparador en su descripción
$scenarios = @(
    @('Revisa la arquitectura de mi aplicación Angular y su deuda técnica', 'angular-architecture-assessment', 'deuda técnica'),
    @('Tenemos un problema recurrente que parece de diseño', 'angular-architecture-assessment', 'incidente recurrente'),
    @('¿Monorepo o microfrontends para 4 equipos?', 'angular-architecture', 'microfrontends'),
    @('¿Qué estrategia de i18n usamos?', 'angular-architecture', 'i18n'),
    @('¿Cómo hacemos cumplir los límites entre features?', 'angular-architecture', 'límites'),
    @('¿Necesitamos un store global?', 'angular-reactivity-state', 'store'),
    @('¿Signals o RxJS para una búsqueda cancelable?', 'angular-reactivity-state', 'rxjs'),
    @('¿Qué tipo de formularios usamos?', 'angular-reactivity-state', 'formularios'),
    @('¿SSR o SSG para la web pública?', 'angular-rendering-performance', 'ssr'),
    @('La aplicación tiene mal LCP', 'angular-rendering-performance', 'lcp'),
    @('¿Cómo promovemos el mismo build entre entornos?', 'angular-rendering-performance', 'mismo build'),
    @('¿Qué nivel de accesibilidad exigimos?', 'angular-quality-security', 'accesibilidad'),
    @('Define la estrategia de pruebas', 'angular-quality-security', 'estrategia de pruebas'),
    @('¿BFF o PKCE con Entra ID?', 'angular-backend-integration', 'pkce'),
    @('¿Cómo gobernamos el contrato OpenAPI?', 'angular-backend-integration', 'openapi'),
    @('Llevar un widget Angular a Liferay', 'angular-liferay-integration', 'liferay'),
    @('Varias aplicaciones Angular en una página de Liferay', 'angular-liferay-integration', 'varias instancias'),
    @('Plan de upgrade de Angular', 'angular-modernization-governance', 'upgrade'),
    @('Migrar desde AngularJS', 'angular-modernization-governance', 'angularjs'),
    @('Redacta un ADR para adoptar zoneless', 'angular-modernization-governance', 'adr'),
    @('Calcula una matriz de decisión', 'angular-modernization-governance', 'matriz de decisión'),
    @('¿Llamamos al modelo de IA desde Angular?', 'angular-backend-integration', 'ia generativa'),
    @('¿Cómo mostramos respuestas de un LLM de forma segura?', 'angular-quality-security', 'llm'),
    @('¿Qué normativa UE afecta al frontend?', 'angular-quality-security', 'normativa')
)
# ---------- Fin de la configuración ----------

$skillsDir = Join-Path $root 'skills'
$pkgDir = Join-Path $root 'skill-packages'

if ($Build) {
    New-Item -ItemType Directory -Force $pkgDir | Out-Null
    foreach ($d in Get-ChildItem $skillsDir -Directory) {
        $zip = Join-Path $pkgDir ($d.Name + '.zip')
        if (Test-Path $zip) { Remove-Item $zip }
        $fs = [IO.File]::Open($zip, 'Create')
        $archive = New-Object IO.Compression.ZipArchive($fs, [IO.Compression.ZipArchiveMode]::Create)
        # SKILL.md y sus recursos en la raíz del ZIP, como indica la documentación de Agent Builder
        foreach ($f in Get-ChildItem $d.FullName -Recurse -File) {
            $rel = $f.FullName.Substring($d.FullName.Length + 1).Replace('\', '/')
            $entry = $archive.CreateEntry($rel)
            $bytes = [IO.File]::ReadAllBytes($f.FullName)
            $es = $entry.Open(); $es.Write($bytes, 0, $bytes.Length); $es.Dispose()
        }
        $archive.Dispose(); $fs.Dispose()
    }
}

# Instrucciones del agente
$agent = Read-Text (Join-Path $root 'AGENT_INSTRUCTIONS.md')
$agentLower = $agent.ToLower()
Check ($agent.Length -le 8000) "Instrucciones del agente: $($agent.Length) caracteres (máximo 8000 en Agent Builder)"
Check ($agent -notmatch $mojibake) 'Instrucciones del agente: posible codificación corrupta'
foreach ($term in 'No eres un agente de implementación', 'Rápido', 'Estándar', 'Completo', 'como máximo 3 preguntas aclaratorias', 'supuestos', 'Pendiente de verificar', 'Matriz de decisión', 'ADR', 'Autoevaluación', 'No realices commits') {
    Check ($agentLower.Contains($term.ToLower())) "Instrucciones del agente: falta '$term'"
}
# Orientación a decisión de arquitectura, no a desarrollo
$devPhrases = 'archivos completos', 'copiables', 'árbol de archivos', 'entrega código'
foreach ($p in $devPhrases) { Check (-not $agentLower.Contains($p)) "Instrucciones del agente: orientación a desarrollo ('$p')" }

$folders = @(Get-ChildItem $skillsDir -Directory | Sort-Object Name)
Check ($folders.Count -le 8) "Número de skills: $($folders.Count) (máximo 8 en Agent Builder)"
Check ($folders.Count -eq 8) "Número de skills: $($folders.Count) (se esperaban 8)"

$desc = @{}
$bodies = @{}
$totalFiles = 0
$supportedExt = '.md', '.txt', '.json', '.yaml', '.yml', '.csv', '.html', '.htm', '.py'
foreach ($d in $folders) {
    $n = $d.Name
    $file = Join-Path $d.FullName 'SKILL.md'
    if (-not (Test-Path $file)) { Check $false "${n}: falta SKILL.md"; continue }
    $text = Read-Text $file
    $lower = $text.ToLower()
    $bodies[$n] = $text
    $m = [regex]::Match($text, "(?s)\A---\r?\nname: (?<n>[^\r\n]+)\r?\ndescription: '(?<d>.*?)'\r?\n---\r?\n")
    Check $m.Success "${n}: frontmatter inválido (name y description entre comillas simples)"
    if ($m.Success) {
        $name = $m.Groups['n'].Value
        $dsc = $m.Groups['d'].Value
        $desc[$n] = $dsc.ToLower()
        Check ($name -eq $n) "${n}: name no coincide con la carpeta"
        Check ($name -match '^[a-z0-9]+(-[a-z0-9]+)*$' -and $name.Length -le 64) "${n}: name no es kebab-case de 64 caracteres o menos"
        Check ($name.StartsWith($prefix)) "${n}: name sin el prefijo '$prefix'"
        Check ($dsc.Length -le 1024) "${n}: descripción de $($dsc.Length) caracteres (máximo 1024)"
        Check ($dsc.Contains('Usar cuando')) "${n}: falta 'Usar cuando' en la descripción"
        Check ($dsc.Contains('No usar')) "${n}: falta 'No usar' en la descripción"
        Check ($dsc.Contains('generador de')) "${n}: la descripción no limita el uso como generador"
        Check ($dsc -notmatch "(?<!')'(?!')") "${n}: comilla simple sin escapar en la descripción"
    }
    Check ($text -notmatch $mojibake) "${n}: posible codificación corrupta"
    foreach ($sec in '## Objetivo', '## Criterios de decisión', '## Antipatrones', '## Salida', '## Autoevaluación') {
        Check ($text.Contains($sec)) "${n}: falta la sección '$sec'"
    }
    Check ($text.Length -ge 3500) "${n}: contenido demasiado escaso ($($text.Length) caracteres)"
    Check ($text.Length -lt 20000) "${n}: SKILL.md de $($text.Length) caracteres (máximo 20000)"
    Check ($agent.Contains('`' + $n + '`')) "${n}: no aparece en el enrutamiento del agente"
    foreach ($p in $devPhrases) { Check (-not $lower.Contains($p)) "${n}: orientación a desarrollo ('$p')" }
    Check (-not $lower.Contains('verifica en fuentes oficiales cualquier hecho dependiente de versión')) "${n}: queda el bloque de reglas genérico duplicado"

    # Al menos un recurso por skill, referenciado desde SKILL.md y con tipo soportado
    $resources = @(Get-ChildItem $d.FullName -Recurse -File | Where-Object { $_.Name -ne 'SKILL.md' })
    Check ($resources.Count -ge 1) "${n}: sin plantilla ni checklist en templates/ o reference/"
    foreach ($r in $resources) {
        $rel = $r.FullName.Substring($d.FullName.Length + 1).Replace('\', '/')
        $rText = Read-Text $r.FullName
        Check ($text.Contains($rel)) "${n}: el recurso '$rel' no está referenciado en SKILL.md"
        Check ($supportedExt -contains $r.Extension.ToLower()) "${n}: tipo de archivo no soportado '$rel'"
        Check (($rel.Split('/').Count) -le 3) "${n}: '$rel' supera la profundidad máxima de 3"
        Check ($rText -notmatch $mojibake) "${n}: posible codificación corrupta en '$rel'"
        foreach ($p in $devPhrases) { Check (-not $rText.ToLower().Contains($p)) "${n}: orientación a desarrollo en '$rel' ('$p')" }
    }
    foreach ($ref in [regex]::Matches($text, '`((?:templates|reference|scripts)/[^`]+)`')) {
        Check (Test-Path (Join-Path $d.FullName $ref.Groups[1].Value)) "${n}: referencia a recurso inexistente '$($ref.Groups[1].Value)'"
    }
    $script:totalFiles += 1 + $resources.Count

    $zip = Join-Path $pkgDir ($n + '.zip')
    if (Test-Path $zip) {
        Check ((Get-Item $zip).Length -le 50MB) "${n}: ZIP mayor de 50 MB"
        $z = [IO.Compression.ZipFile]::OpenRead($zip)
        $names = @($z.Entries | ForEach-Object { $_.FullName })
        Check ($names -contains 'SKILL.md') "${n}: SKILL.md no está en la raíz del ZIP"
        Check ($names.Count -eq (1 + $resources.Count)) "${n}: el ZIP no contiene los mismos archivos que skills/ (ejecuta con -Build)"
        $skillEntry = $z.Entries | Where-Object { $_.FullName -eq 'SKILL.md' }
        if ($skillEntry) {
            $sr = New-Object IO.StreamReader($skillEntry.Open(), $utf8)
            $zt = $sr.ReadToEnd(); $sr.Dispose()
            Check ($zt -eq $text) "${n}: el ZIP no coincide con skills/ (ejecuta con -Build)"
        }
        $z.Dispose()
    } else { Check $false "${n}: falta el ZIP (ejecuta con -Build)" }
}
Check ($totalFiles -le 350) "Total de archivos en skills: $totalFiles (máximo 350)"

# Recursos compartidos: deben existir en este agente y ser idénticos en todos los agentes que los incluyen
foreach ($shared in $sharedResources) {
    Check (@(Get-ChildItem $skillsDir -Recurse -File -Filter $shared).Count -ge 1) "Falta el recurso compartido '$shared'"
    $copies = @(Get-ChildItem (Split-Path $root -Parent) -Recurse -File -Filter $shared | Where-Object { $_.FullName -match '[\\/]skills[\\/]' })
    Check (@($copies | ForEach-Object { (Get-FileHash $_.FullName).Hash } | Select-Object -Unique).Count -le 1) "El recurso compartido '$shared' difiere entre agentes"
}

# Prueba de humo de decision_matrix.py si hay un Python real disponible
$py = Get-Command python, python3 -ErrorAction SilentlyContinue | Where-Object { $_.Source -notmatch 'WindowsApps' } | Select-Object -First 1
$dm = Get-ChildItem $skillsDir -Recurse -File -Filter 'decision_matrix.py' | Select-Object -First 1
if ($py -and $dm) {
    $tmp = [IO.Path]::GetTempFileName()
    [IO.File]::WriteAllText($tmp, '{"criteria":[{"name":"A","weight":3},{"name":"B","weight":1}],"alternatives":[{"name":"X","scores":{"A":5,"B":1}},{"name":"Y","scores":{"A":2,"B":5}}]}', $utf8)
    $res = (& $py.Source $dm.FullName $tmp 2>&1) -join "`n"
    Remove-Item $tmp
    Check ($res -match 'gana \*\*X\*\*') 'decision_matrix.py: la prueba de humo no devuelve el ganador esperado'
}

# Las skills no deben ser plantillas duplicadas
$sections = @($bodies.Values | ForEach-Object { $i = $_.IndexOf('## Objetivo'); if ($i -ge 0) { $_.Substring($i) } else { $_ } })
Check (($sections | Select-Object -Unique).Count -eq $sections.Count) 'Hay skills con contenido duplicado'
$descValues = @($desc.Values)
Check (($descValues | Select-Object -Unique).Count -eq $descValues.Count) 'Hay descripciones duplicadas'

# Conceptos obligatorios por skill
foreach ($n in $required.Keys) {
    Check ($bodies.ContainsKey($n)) "Falta la skill esperada '$n'"
    if ($bodies.ContainsKey($n)) {
        $t = $bodies[$n].ToLower()
        foreach ($term in $required[$n]) { Check ($t.Contains($term)) "${n}: falta el concepto '$term'" }
    }
}

# Disparadores de enrutamiento
foreach ($s in $scenarios) {
    $ok = $desc.ContainsKey($s[1]) -and $desc[$s[1]].Contains($s[2])
    Check $ok "Enrutamiento: '$($s[0])' no tiene el disparador '$($s[2])' en $($s[1])"
}

# Prompts de prueba: mínimo 20 y al menos uno por skill
$tpPath = Join-Path $root 'validation\test-prompts.md'
Check (Test-Path $tpPath) 'Falta validation/test-prompts.md'
if (Test-Path $tpPath) {
    $tp = Read-Text $tpPath
    $rows = [regex]::Matches($tp, '(?m)^\|\s*\d+\s*\|').Count
    Check ($rows -ge 20) "test-prompts.md: $rows prompts (mínimo 20)"
    foreach ($d in $folders) {
        $short = $d.Name.Substring($prefix.Length)
        Check ($tp.Contains("| $short")) "test-prompts.md: ningún prompt para $($d.Name)"
    }
}

if ($errors.Count -eq 0) { Write-Output "OK: $checks comprobaciones superadas"; exit 0 }
Write-Output "FALLOS ($($errors.Count) de $checks comprobaciones):"
$errors | ForEach-Object { Write-Output " - $_" }
exit 1
