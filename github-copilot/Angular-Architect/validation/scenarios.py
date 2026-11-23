"""Simulación de selección de skills por descripción (aproximación al mecanismo de Copilot).

Uso:
  python3 scenarios.py angular <ruta-agente-angular>
  python3 scenarios.py nestjs <ruta-agente-nestjs>
  python3 scenarios.py combined <ruta-agente-angular> <ruta-agente-nestjs>

En modo combined se cargan las skills de los dos agentes juntas (como en un monorepo
fullstack con ambas carpetas en .github/skills) y se mide si la petición encuentra la
skill correcta y del lado correcto (frontend o backend).
"""
import re
import sys
import unicodedata
from pathlib import Path

MODE = sys.argv[1]
STOP = set("de la el los las un una y o en con para que se por al del mi me lo le es este esta cuando usar cubre".split())


def roots(text):
    t = unicodedata.normalize("NFD", text.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return {w[:5] for w in re.findall(r"[a-z0-9]+", t) if len(w) > 2 and w not in STOP}


def load(path):
    s = Path(path).resolve() / ".github/skills"
    return {d.name: roots(re.search(r"^description:\s*'?(.*?)'?$", (d / "SKILL.md").read_text(), re.M).group(1))
            for d in s.iterdir() if d.is_dir()}


ANGULAR = [
    ("Crea un buscador con autocompletado que consulte la API mientras escribo", {"state", "http"}),
    ("Añade la ruta /pedidos/:id protegida solo para administradores", {"routing"}),
    ("Formulario de registro con contraseña y confirmación de contraseña", {"forms"}),
    ("Escribe los tests unitarios del servicio de pedidos", {"testing"}),
    ("La página inicial tarda mucho en cargar, el bundle es enorme", {"performance"}),
    ("Actualiza el proyecto de Angular 21 a Angular 22", {"environment"}),
    ("En producción con SSR las rutas inválidas no redirigen a la ruta por defecto", {"ssr"}),
    ("Haz un modal de confirmación accesible con teclado", {"accessibility"}),
    ("Muestra una notificación global cuando falle cualquier petición HTTP", {"http"}),
    ("Dónde guardo el token después del login", {"security"}),
    ("Traduce la pantalla de detalle al gallego", {"i18n"}),
    ("Este componente tiene 400 líneas y hace de todo, refactorízalo", {"solid"}),
    ("SonarQube marca complejidad cognitiva alta en este fichero", {"quality"}),
    ("Dale estilo a la tarjeta y que sea responsive en móvil", {"styling"}),
    ("Añade una variable de entorno con la URL de la API", {"environment"}),
    ("Activa SSR en el proyecto y prerenderiza la página de inicio", {"ssr"}),
    ("Error window is not defined al arrancar el servidor", {"ssr"}),
    ("Crea una librería de componentes reutilizable para publicar en el registro privado", {"library"}),
    # Monorepo
    ("Tenemos un monorepo Nx: crea una librería feature de pedidos para la aplicación portal", {"monorepo"}),
    ("En el workspace con varias aplicaciones, dónde pongo el código compartido entre portal y admin", {"monorepo"}),
    ("Configura las etiquetas y los límites entre librerías para que ui no importe data-access", {"monorepo"}),
    ("Ejecuta solo los tests y el build de lo afectado por mis cambios en el monorepo", {"monorepo"}),
    ("Actualiza el monorepo Nx de Angular 21 a 22", {"monorepo", "environment"}),
]
NESTJS = [
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
    ("Los mensajes duplicados del broker crean facturas repetidas", {"microservices"}),
    ("Dónde va la transacción cuando creo un pedido con sus líneas", {"services", "persistence"}),
    ("Tengo una dependencia circular entre UsersModule y OrdersModule", {"modules"}),
    ("Añade un interceptor que mida el tiempo de cada petición", {"request-pipeline"}),
    ("Publica un evento en RabbitMQ cuando se cree un pedido y consúmelo en facturación", {"microservices"}),
    # Monorepo
    ("Añade una segunda aplicación billing al monorepo del Nest CLI y una librería compartida", {"monorepo"}),
    ("En el monorepo Nx, crea una librería con los guards de autenticación compartidos por api y worker", {"monorepo"}),
    ("Cada aplicación del monorepo necesita su propio Dockerfile y sus migraciones", {"monorepo"}),
    ("Ejecuta solo los tests de lo afectado por mis cambios en el monorepo", {"monorepo"}),
    ("Comparte los tipos de la API con el frontend Angular del mismo monorepo", {"monorepo"}),
]
# Peticiones de un monorepo fullstack: (petición, lado esperado, skills válidas)
COMBINED = [
    ("Crea en el frontend Angular el formulario de alta de pedidos", "angular", {"angular-forms"}),
    ("Crea en la API NestJS el endpoint REST para dar de alta pedidos", "nestjs", {"nestjs-controllers"}),
    ("Escribe los tests del servicio de pedidos de la API NestJS", "nestjs", {"nestjs-testing"}),
    ("Escribe los tests del componente de pedidos de Angular", "angular", {"angular-testing"}),
    ("Comparte el contrato de pedidos entre el frontend Angular y la API NestJS en el monorepo Nx", "either", {"angular-monorepo", "nestjs-monorepo"}),
    ("Añade login en la aplicación Angular y guarda el token", "angular", {"angular-security"}),
    ("Añade login con JWT en la API NestJS", "nestjs", {"nestjs-auth"}),
    ("Unifica el formato de errores que devuelve la API NestJS", "nestjs", {"nestjs-error-handling"}),
    ("Muestra un aviso en Angular cuando la API devuelva un error", "angular", {"angular-http"}),
    ("Configura las variables de entorno de la aplicación Angular", "angular", {"angular-environment"}),
    ("Configura las variables de entorno de la API NestJS", "nestjs", {"nestjs-config"}),
    ("Ejecuta en el monorepo Nx solo lo afectado de la API NestJS", "nestjs", {"nestjs-monorepo"}),
]


def run(cases, desc, prefix):
    hits = 0
    for prompt, expected in cases:
        exp = {prefix + e for e in expected}
        p = roots(prompt)
        top3 = sorted(desc, key=lambda s: -len(p & desc[s]))[:3]
        ok = bool(exp & set(top3))
        hits += ok
        print(f"{'OK ' if ok else 'MISS'} {prompt[:74]:74} -> {', '.join(x.replace(prefix, '') for x in top3)}")
    print(f"\nSelección correcta en top-3: {hits}/{len(cases)}")


if MODE == "angular":
    run(ANGULAR, load(sys.argv[2]), "angular-")
elif MODE == "nestjs":
    run(NESTJS, load(sys.argv[2]), "nestjs-")
else:
    desc = {**load(sys.argv[2]), **load(sys.argv[3])}
    ok_skill = ok_side = 0
    for prompt, side, expected in COMBINED:
        p = roots(prompt)
        ranked = sorted(desc, key=lambda s: -len(p & desc[s]))
        top3, top1 = ranked[:3], ranked[0]
        good_skill = bool(expected & set(top3))
        good_side = side == "either" or top1.startswith(side + "-")
        ok_skill += good_skill
        ok_side += good_side
        mark = "OK " if good_skill and good_side else "MISS"
        print(f"{mark} {prompt[:74]:74} -> {', '.join(top3)}")
    print(f"\nSkill correcta en top-3: {ok_skill}/{len(COMBINED)} | Lado correcto en top-1: {ok_side}/{len(COMBINED)}")
