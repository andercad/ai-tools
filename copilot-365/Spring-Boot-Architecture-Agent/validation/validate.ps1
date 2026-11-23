# Valida el paquete y regenera los ZIP desde skills/.
# Uso: powershell -File validation\validate.ps1 [-NoPackage]
param([switch]$NoPackage)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression, System.IO.Compression.FileSystem
$root = Split-Path -Parent $PSScriptRoot
$errors = New-Object System.Collections.Generic.List[string]
$utf8 = New-Object System.Text.UTF8Encoding($false)

function Read-Text($p) { [IO.File]::ReadAllText($p, $utf8) }

$agentPath = Join-Path $root 'AGENT_INSTRUCTIONS.md'
$agent = Read-Text $agentPath
if ($agent.Length -gt 8000) { $errors.Add("AGENT_INSTRUCTIONS.md supera 8000 caracteres ($($agent.Length))") }
if ($agent -notmatch 'como máximo 3 preguntas aclaratorias') { $errors.Add('AGENT_INSTRUCTIONS.md: el máximo de preguntas aclaratorias debe ser 3, como en los demás agentes') }

$folders = Get-ChildItem (Join-Path $root 'skills') -Directory | Sort-Object Name
if ($folders.Count -gt 8) { $errors.Add("Máximo 8 skills en Microsoft 365 Copilot; hay $($folders.Count)") }
if ($folders.Count -ne 8) { $errors.Add("Se esperaban 8 skills; hay $($folders.Count)") }

$descriptions = @{}
$bodies = @{}
foreach ($d in $folders) {
    $f = Join-Path $d.FullName 'SKILL.md'
    if (-not (Test-Path $f)) { $errors.Add("Falta SKILL.md: $($d.Name)"); continue }
    $s = (Read-Text $f) -replace "`r`n", "`n"
    $bodies[$d.Name] = $s.ToLowerInvariant()

    $m = [regex]::Match($s, "^---\nname: (?<n>[^\n]+)\ndescription: '(?<d>.*)'\n---\n", 'Singleline')
    if (-not $m.Success) { $errors.Add("Frontmatter inválido: $($d.Name)"); continue }
    $name = $m.Groups['n'].Value.Trim()
    $desc = $m.Groups['d'].Value
    if ($name -ne $d.Name) { $errors.Add("name '$name' no coincide con la carpeta '$($d.Name)'") }
    if ($name.Length -gt 64) { $errors.Add("name > 64 caracteres: $name") }
    if ($desc.Length -gt 1024) { $errors.Add("description > 1024 caracteres: $name ($($desc.Length))") }
    if ($desc -notmatch 'Usar cuando') { $errors.Add("description sin 'Usar cuando': $name") }
    if ($desc -match 'relacionado con este ámbito') { $errors.Add("description genérica: $name") }
    if ($desc -match "(?<!')'(?!')" ) { $errors.Add("description contiene comilla simple sin escapar: $name") }
    $descriptions[$name] = $desc

    foreach ($sec in '## Objetivo', '## Salida', '## Autoevaluación') {
        if ($s -notmatch [regex]::Escape($sec)) { $errors.Add("Falta sección '$sec': $name") }
    }
    if (($s -split "`n").Count -lt 30) { $errors.Add("Skill demasiado escueta (<30 líneas): $name") }
    if (($s -split "`n").Count -gt 500) { $errors.Add("Skill > 500 líneas: $name") }
    if ($agent -notmatch ('`' + [regex]::Escape($name) + '`')) { $errors.Add("Sin routing en instrucciones: $name") }

    # Recursos: al menos uno por skill, referenciado desde SKILL.md y con tipo y profundidad admitidos
    $resources = @(Get-ChildItem $d.FullName -Recurse -File | Where-Object { $_.Name -ne 'SKILL.md' })
    if ($resources.Count -lt 1) { $errors.Add("Sin plantilla ni checklist en templates/ o reference/: $name") }
    foreach ($r in $resources) {
        $rel = $r.FullName.Substring($d.FullName.Length + 1).Replace('\', '/')
        if (-not $s.Contains($rel)) { $errors.Add("Recurso no referenciado en SKILL.md: $name/$rel") }
        if ('.md', '.txt', '.json', '.yaml', '.yml', '.csv', '.py' -notcontains $r.Extension.ToLower()) { $errors.Add("Tipo de archivo no soportado: $name/$rel") }
        if ($rel.Split('/').Count -gt 3) { $errors.Add("Profundidad mayor de 3: $name/$rel") }
    }
    foreach ($ref in [regex]::Matches($s, '`((?:templates|reference|scripts)/[^`]+)`')) {
        if (-not (Test-Path (Join-Path $d.FullName $ref.Groups[1].Value))) { $errors.Add("Referencia a recurso inexistente: $name/$($ref.Groups[1].Value)") }
    }
}

# Descripciones distintas entre sí
$dup = $descriptions.GetEnumerator() | Group-Object Value | Where-Object Count -gt 1
foreach ($g in $dup) { $errors.Add('Descripciones duplicadas: ' + (($g.Group | % Key) -join ', ')) }

# Cobertura de contenido obligatoria
$mod = $bodies['spring-modularity-domain']; $api = $bodies['spring-api-integration']
foreach ($t in 'puertos de entrada', 'puertos de salida', 'adaptadores de entrada', 'adaptadores de salida', 'microservicios', 'spring modulith', 'verify()') {
    if ($mod -and -not $mod.Contains($t)) { $errors.Add("modularity: falta '$t'") }
}
foreach ($t in 'rest frente a graphql', 'n+1', 'paginación', 'autorización', 'complejidad', 'federación', 'problemdetail', 'kafka', 'dlq', 'idempotentes', 'versionado', 'rag', 'ia generativa') {
    if ($api -and -not $api.Contains($t)) { $errors.Add("api: falta '$t'") }
}
$required = @{
    'spring-data-transactions'          = @('outbox', 'idempotente', 'expand/contract', '@transactional')
    'spring-security-identity'          = @('bff', 'resource server', 'stride', 'secretos', 'inyección de prompts', 'eu-regulatory-map.md')
    'spring-cloud-runtime'              = @('native', 'liveness', 'graceful', 'rollback')
    'spring-observability-resilience'   = @('slo', 'timeout', 'circuit breaker', 'cardinalidad', 'dueña de la política', 'tokens')
    'spring-modernization-governance'   = @('adr', 'strangler', 'archunit', 'jakarta', 'testcontainers', 'caracterización', 'nestjs', 'decision_matrix.py')
    'spring-architecture-assessment'    = @('hechos', 'deuda', 'descubrimiento')
}
foreach ($k in $required.Keys) {
    foreach ($t in $required[$k]) { if ($bodies[$k] -and -not $bodies[$k].Contains($t)) { $errors.Add("${k}: falta '$t'") } }
}

# Recursos compartidos: deben existir en este agente y ser idénticos en todos los agentes que los incluyen
foreach ($shared in 'decision_matrix.py', 'eu-regulatory-map.md', 'backend-technology-selection.md') {
    if (@(Get-ChildItem (Join-Path $root 'skills') -Recurse -File -Filter $shared).Count -lt 1) { $errors.Add("Falta el recurso compartido '$shared'") }
    $copies = @(Get-ChildItem (Split-Path $root -Parent) -Recurse -File -Filter $shared | Where-Object { $_.FullName -match '[\\/]skills[\\/]' })
    if (@($copies | ForEach-Object { (Get-FileHash $_.FullName).Hash } | Select-Object -Unique).Count -gt 1) { $errors.Add("El recurso compartido '$shared' difiere entre agentes") }
}

# Prueba de humo de decision_matrix.py si hay un Python real disponible
$py = Get-Command python, python3 -ErrorAction SilentlyContinue | Where-Object { $_.Source -notmatch 'WindowsApps' } | Select-Object -First 1
$dm = Get-ChildItem (Join-Path $root 'skills') -Recurse -File -Filter 'decision_matrix.py' | Select-Object -First 1
if ($py -and $dm) {
    $tmp = [IO.Path]::GetTempFileName()
    [IO.File]::WriteAllText($tmp, '{"criteria":[{"name":"A","weight":3},{"name":"B","weight":1}],"alternatives":[{"name":"X","scores":{"A":5,"B":1}},{"name":"Y","scores":{"A":2,"B":5}}]}', $utf8)
    $res = try { (& $py.Source $dm.FullName $tmp 2>&1) -join "`n" } catch { "$_" }
    Remove-Item $tmp
    if ($res -notmatch 'gana \*\*X\*\*') { $errors.Add('decision_matrix.py: la prueba de humo no devuelve el ganador esperado') }
}

# Empaquetado: un ZIP por skill con SKILL.md en la raíz (documentación de Agent Builder) y separadores '/'
if (-not $NoPackage -and $errors.Count -eq 0) {
    $pkgDir = Join-Path $root 'skill-packages'
    New-Item -ItemType Directory -Force $pkgDir | Out-Null
    foreach ($d in $folders) {
        $zipPath = Join-Path $pkgDir ($d.Name + '.zip')
        if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
        $zip = [IO.Compression.ZipFile]::Open($zipPath, 'Create')
        try {
            foreach ($file in Get-ChildItem $d.FullName -Recurse -File) {
                $rel = $file.FullName.Substring($d.FullName.Length).TrimStart('\', '/') -replace '\\', '/'
                [void][IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $file.FullName, $rel)
            }
        } finally { $zip.Dispose() }
    }
    # Verificar que cada ZIP coincide con la fuente
    foreach ($d in $folders) {
        $zip = [IO.Compression.ZipFile]::OpenRead((Join-Path $pkgDir ($d.Name + '.zip')))
        try {
            $e = $zip.GetEntry('SKILL.md')
            if (-not $e) { $errors.Add("ZIP sin SKILL.md: $($d.Name)"); continue }
            $sr = New-Object IO.StreamReader($e.Open(), $utf8)
            $zt = $sr.ReadToEnd(); $sr.Dispose()
            if ($zt -ne (Read-Text (Join-Path $d.FullName 'SKILL.md'))) { $errors.Add("ZIP desincronizado: $($d.Name)") }
            if ($zip.Entries.Count -ne @(Get-ChildItem $d.FullName -Recurse -File).Count) { $errors.Add("ZIP con archivos distintos a skills/: $($d.Name)") }
        } finally { $zip.Dispose() }
    }
}

if ($errors.Count -eq 0) { Write-Host "OK: $($folders.Count) skills, instrucciones $($agent.Length) caracteres" ; exit 0 }
$errors | ForEach-Object { Write-Host "ERROR: $_" }
exit 1
