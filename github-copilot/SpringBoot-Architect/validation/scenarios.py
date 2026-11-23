"""Simulación de selección de skills por descripción (aproximación al mecanismo de Copilot).
La skill esperada debe quedar en el top 3 por solapamiento de raíces de palabras.
Uso: python3 scenarios.py <nestjs|spring> <ruta-del-agente>"""
import re
import sys
import unicodedata
from pathlib import Path

PROFILE = sys.argv[1]
S = Path(sys.argv[2] if len(sys.argv) > 2 else "..").resolve() / ".github/skills"
STOP = set("de la el los las un una y o en con para que se por al del mi me lo le es este esta cuando usar cubre".split())


def roots(text):
    t = unicodedata.normalize("NFD", text.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return {w[:5] for w in re.findall(r"[a-z0-9]+", t) if len(w) > 2 and w not in STOP}


desc = {d.name: roots(re.search(r"^description:\s*'?(.*?)'?$", (d / "SKILL.md").read_text(), re.M).group(1))
        for d in S.iterdir() if d.is_dir()}
P = "nestjs-" if PROFILE == "nestjs" else "spring-"
COMMON = [
    ("Crea el CRUD de pedidos con su controlador y los endpoints REST", {"controllers"}),
    ("Valida que el email del body sea correcto y rechaza campos extra", {"dto-validation"}),
    ("Añade login con JWT y refresh token", {"auth"}),
    ("Solo el propietario puede ver y modificar sus pedidos", {"auth"}),
    ("Revisa este endpoint de subida de ficheros por vulnerabilidades", {"security"}),
    ("Crea la migración para añadir la columna teléfono a la tabla de usuarios", {"persistence"}),
    ("El listado de pedidos hace una consulta por cada pedido (N+1)", {"persistence", "graphql"}),
    ("Unifica el formato de los errores que devuelve la API", {"error-handling"}),
    ("Añade la variable de entorno con la URL del servicio de pagos", {"config"}),
    ("Escribe los tests unitarios del servicio de usuarios", {"testing"}),
    ("Configura el formato del código y corrige los avisos de SonarQube", {"quality"}),
    ("El servicio de pedidos tiene demasiadas responsabilidades, refactorízalo", {"solid"}),
    ("Expón usuarios y pedidos mediante GraphQL", {"graphql"}),
    ("Configura rate limiting en el endpoint de login", {"security"}),
    ("Documenta los endpoints con Swagger OpenAPI", {"controllers"}),
    ("Los mensajes duplicados del broker crean facturas repetidas", {"microservices", "messaging"}),
    ("Dónde va la transacción cuando creo un pedido con sus líneas", {"services", "persistence"}),
]
SPECIFIC = {
    "nestjs": [
        ("Tengo una dependencia circular entre UsersModule y OrdersModule", {"modules"}),
        ("Añade un interceptor que mida el tiempo de cada petición", {"request-pipeline"}),
        ("Publica un evento en RabbitMQ cuando se cree un pedido y consúmelo en facturación", {"microservices"}),
    ],
    "spring": [
        ("Llama al servicio externo de pagos con timeout y reintentos", {"http-clients"}),
        ("Configura los health checks y las métricas para Kubernetes", {"observability"}),
        ("Publica un evento en Kafka cuando se cree un pedido y consúmelo en facturación", {"messaging"}),
        ("Añade un filtro que genere un correlation id para cada petición", {"web-pipeline"}),
        ("Organiza los paquetes de la nueva funcionalidad de facturación", {"structure"}),
    ],
}[PROFILE]
hits = 0
cases = COMMON + SPECIFIC
for prompt, expected in cases:
    expected = {P + e for e in expected}
    p = roots(prompt)
    top3 = sorted(desc, key=lambda s: -len(p & desc[s]))[:3]
    ok = bool(expected & set(top3))
    hits += ok
    print(f"{'OK ' if ok else 'MISS'} {prompt[:70]:70} -> {', '.join(x.replace(P, '') for x in top3)}")
print(f"\nSelección correcta en top-3: {hits}/{len(cases)}")
