# Uso:  powershell -File validation\validate.ps1 [-Build]
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

$skillsDir = Join-Path $root 'skills'
$pkgDir = Join-Path $root 'skill-packages'
$sharedResources = 'decision_matrix.py', 'eu-regulatory-map.md', 'backend-technology-selection.md'

if ($Build) {
    New-Item -ItemType Directory -Force $pkgDir | Out-Null
    foreach ($d in Get-ChildItem $skillsDir -Directory) {
        $zip = Join-Path $pkgDir ($d.Name + '.zip')
        if (Test-Path $zip) { Remove-Item $zip }
        $fs = [IO.File]::Open($zip, 'Create')
        $archive = New-Object IO.Compression.ZipArchive($fs, [IO.Compression.ZipArchiveMode]::Create)
        # SKILL.md y los recursos van en la raíz del ZIP, como indica la documentación de Agent Builder
        foreach ($f in Get-ChildItem $d.FullName -Recurse -File) {
            $rel = $f.FullName.Substring($d.FullName.Length + 1).Replace('\', '/')
            $entry = $archive.CreateEntry($rel)
            $bytes = [IO.File]::ReadAllBytes($f.FullName)
            $es = $entry.Open(); $es.Write($bytes, 0, $bytes.Length); $es.Dispose()
        }
        $archive.Dispose(); $fs.Dispose()
    }
}

# Agente
$agentPath = Join-Path $root 'AGENT_INSTRUCTIONS.md'
$agent = [IO.File]::ReadAllText($agentPath, $utf8)
Check ($agent.Length -le 8000) "Instrucciones del agente: $($agent.Length) caracteres (máximo 8000 en Agent Builder)"
Check ($agent -notmatch $mojibake) 'Instrucciones del agente: posible codificación corrupta'
Check ($agent -notmatch '\.\.\.\s*$' -and $agent -notmatch 'Eres un asesor[^\n]*\.\.\.') 'Instrucciones del agente: texto truncado'
foreach ($term in 'Rápido', 'Estándar', 'Completo', 'como máximo 3 preguntas aclaratorias', 'sin acceso al repositorio', 'Autoevalúa') {
    Check ($agent.Contains($term)) "Instrucciones del agente: falta '$term'"
}

$folders = @(Get-ChildItem $skillsDir -Directory | Sort-Object Name)
Check ($folders.Count -le 8) "Número de skills: $($folders.Count) (máximo 8 en Agent Builder)"
Check ($folders.Count -eq 8) "Número de skills: $($folders.Count) (se esperaban 8)"

$desc = @{}
$totalFiles = 0
$supportedExt = '.md', '.txt', '.json', '.yaml', '.yml', '.csv', '.html', '.htm', '.py'
foreach ($d in $folders) {
    $n = $d.Name
    $file = Join-Path $d.FullName 'SKILL.md'
    $text = [IO.File]::ReadAllText($file, $utf8)
    $m = [regex]::Match($text, "(?s)\A---\r?\nname: (?<n>[^\r\n]+)\r?\ndescription: '(?<d>.*?)'\r?\n---\r?\n")
    Check $m.Success "${n}: frontmatter inválido"
    if ($m.Success) {
        Check ($m.Groups['n'].Value -eq $n) "${n}: name no coincide con la carpeta"
        $dsc = $m.Groups['d'].Value
        $desc[$n] = $dsc.ToLower()
        Check ($dsc.Length -le 1024) "${n}: descripción de $($dsc.Length) caracteres (máximo 1024)"
        Check ($dsc.Contains('Usar cuando')) "${n}: falta 'Usar cuando' en la descripción"
        Check ($dsc.Contains('No usar')) "${n}: falta 'No usar' en la descripción"
    }
    Check ($text -notmatch $mojibake) "${n}: posible codificación corrupta"
    Check ($text.Contains('## Autoevaluación')) "${n}: falta sección Autoevaluación"
    Check ($text.Contains('## Salida')) "${n}: falta sección Salida"
    Check ($text.Length -ge 3500) "${n}: contenido demasiado escaso ($($text.Length) caracteres)"
    Check ($text.Length -lt 20000) "${n}: SKILL.md de $($text.Length) caracteres (máximo 20000)"
    Check ($agent.Contains('`' + $n + '`')) "${n}: no aparece en el enrutamiento del agente"

    # Cada recurso debe estar referenciado desde SKILL.md y tener un tipo soportado
    $resources = @(Get-ChildItem $d.FullName -Recurse -File | Where-Object { $_.Name -ne 'SKILL.md' })
    Check ($resources.Count -ge 1) "${n}: sin plantilla ni checklist en templates/ o reference/"
    foreach ($r in $resources) {
        $rel = $r.FullName.Substring($d.FullName.Length + 1).Replace('\', '/')
        Check ($text.Contains($rel)) "${n}: el recurso '$rel' no está referenciado en SKILL.md"
        Check ($supportedExt -contains $r.Extension.ToLower()) "${n}: tipo de archivo no soportado '$rel'"
        Check (($rel.Split('/').Count) -le 3) "${n}: '$rel' supera la profundidad máxima de 3"
        Check ([IO.File]::ReadAllText($r.FullName, $utf8) -notmatch $mojibake) "${n}: posible codificación corrupta en '$rel'"
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
    } else { Check $false "${n}: falta el ZIP" }
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
$bodies = $folders | ForEach-Object { [IO.File]::ReadAllText((Join-Path $_.FullName 'SKILL.md'), $utf8) }
Check (($bodies | ForEach-Object { $_.Substring($_.IndexOf('## Objetivo')) } | Select-Object -Unique).Count -eq $bodies.Count) 'Hay skills con contenido duplicado'
Check (-not ($bodies -match 'Identifica contexto, versión, restricciones y fuentes disponibles')) 'Queda el procedimiento genérico duplicado en alguna skill'

# Contenido obligatorio por skill
$required = @{
    'nestjs-modularity-domain'          = @('puertos de entrada', 'puertos de salida', 'adaptadores de entrada', 'adaptadores de salida', 'microservicios', 'monolito modular', 'forwardref')
    'nestjs-api-integration'            = @('rest frente a graphql', 'n+1', 'paginación', 'autorización', 'complejidad', 'federación', 'openapi', 'webhooks', 'rag', 'ia generativa')
    'nestjs-security-identity'          = @('owasp', 'pkce', 'denegar por defecto', 'bola', 'ssrf', 'secretos', 'throttler', 'inyección de prompts', 'eu-regulatory-map.md')
    'nestjs-data-messaging'             = @('outbox', 'idempot', 'dead-letter', 'expand/contract', 'kafka', 'rabbitmq', 'prisma', 'typeorm')
    'nestjs-runtime-deployment'         = @('enableshutdownhooks', 'liveness', 'readiness', 'sigterm', 'lts', 'rollback')
    'nestjs-observability-resilience'   = @('slo', 'opentelemetry', 'timeout', 'circuit breaker', 'event loop', 'cardinalidad', 'backpressure', 'tokens')
    'nestjs-modernization-governance'   = @('adr', 'strangler', 'quality gates', 'rollback', 'esm', 'fastify', 'spring boot', 'decision_matrix.py')
    'nestjs-architecture-assessment'    = @('hechos', 'evidencia', 'antipatrones', 'impacto', 'roadmap', 'hallazgos')
}
foreach ($n in $required.Keys) {
    $p = Join-Path $skillsDir "$n\SKILL.md"
    if (Test-Path $p) {
        $t = [IO.File]::ReadAllText($p, $utf8).ToLower()
        foreach ($term in $required[$n]) { Check ($t.Contains($term)) "${n}: falta el concepto '$term'" }
    }
}

# Escenarios de enrutamiento: la skill esperada debe contener los disparadores en su descripción
$scenarios = @(
    @('Diseña un caso de uso con puertos y adaptadores sin acoplar el dominio', 'nestjs-modularity-domain', 'puertos y adaptadores'),
    @('¿Monolito modular o microservicios?', 'nestjs-modularity-domain', 'microservicios'),
    @('Tengo dependencias circulares con forwardRef', 'nestjs-modularity-domain', 'forwardref'),
    @('¿REST o GraphQL para varios clientes?', 'nestjs-api-integration', 'graphql'),
    @('Evita N+1 y define paginación en GraphQL', 'nestjs-api-integration', 'dataloader'),
    @('¿Cómo versiono mi API y contrato OpenAPI?', 'nestjs-api-integration', 'openapi'),
    @('Diseña login con Entra ID y roles', 'nestjs-security-identity', 'entra id'),
    @('Revisa mi API contra OWASP', 'nestjs-security-identity', 'owasp'),
    @('¿TypeORM o Prisma?', 'nestjs-data-messaging', 'prisma'),
    @('¿Kafka o RabbitMQ para eventos de pedidos?', 'nestjs-data-messaging', 'rabbitmq'),
    @('Necesito outbox e idempotencia', 'nestjs-data-messaging', 'outbox'),
    @('¿Container Apps o AKS?', 'nestjs-runtime-deployment', 'container apps'),
    @('Graceful shutdown y probes', 'nestjs-runtime-deployment', 'graceful shutdown'),
    @('Define SLO y trazas con OpenTelemetry', 'nestjs-observability-resilience', 'opentelemetry'),
    @('Mi API se cuelga: event loop y timeouts', 'nestjs-observability-resilience', 'event loop'),
    @('Plan para actualizar NestJS y pasar a ESM', 'nestjs-modernization-governance', 'esm'),
    @('Redacta un ADR para el cambio a Fastify', 'nestjs-modernization-governance', 'adr'),
    @('Revisa la arquitectura de mi aplicación y su deuda técnica', 'nestjs-architecture-assessment', 'deuda técnica'),
    @('Diseña un asistente con RAG sobre nuestra documentación', 'nestjs-api-integration', 'rag'),
    @('¿NestJS o Spring Boot para el nuevo servicio?', 'nestjs-modernization-governance', 'spring boot'),
    @('¿Qué normativa UE afecta a nuestra API?', 'nestjs-security-identity', 'normativa'),
    @('Coste de tokens y cuotas del proveedor de IA', 'nestjs-observability-resilience', 'tokens')
)
foreach ($s in $scenarios) {
    $ok = $desc.ContainsKey($s[1]) -and $desc[$s[1]].Contains($s[2])
    Check $ok "Enrutamiento: '$($s[0])' no tiene disparador '$($s[2])' en $($s[1])"
}

if ($errors.Count -eq 0) { Write-Output "OK: $checks comprobaciones superadas"; exit 0 }
Write-Output "FALLOS ($($errors.Count) de $checks comprobaciones):"
$errors | ForEach-Object { Write-Output " - $_" }
exit 1
