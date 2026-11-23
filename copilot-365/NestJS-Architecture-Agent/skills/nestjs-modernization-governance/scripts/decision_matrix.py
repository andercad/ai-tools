#!/usr/bin/env python3
"""Matriz de decisión ponderada con análisis de sensibilidad. Solo usa la biblioteca estándar.

Uso:
  python decision_matrix.py entrada.json
  python decision_matrix.py '{"criteria": [...], "alternatives": [...]}'
  python decision_matrix.py - < entrada.json

Entrada (JSON), con pesos de 1 a 3 y valoraciones de 1 a 5:
  {
    "criteria": [{"name": "Coste operativo", "weight": 3}, {"name": "Autonomía de equipos", "weight": 2}],
    "alternatives": [
      {"name": "Monolito modular", "scores": {"Coste operativo": 5, "Autonomía de equipos": 3}},
      {"name": "Microservicios", "scores": {"Coste operativo": 2, "Autonomía de equipos": 5}}
    ]
  }

Salida: tabla Markdown con totales ponderados, criterio que decide, sensibilidad a pesos y
valoraciones, y un veredicto de robustez. La matriz apoya la decisión; no la sustituye.
"""
import json
import sys

WEIGHT_MIN, WEIGHT_MAX = 1, 3
SCORE_MIN, SCORE_MAX = 1, 5
MAX_ALTERNATIVES = 3
EPS = 1e-9


def fmt(x):
    if abs(x - round(x)) < EPS:
        return str(int(round(x)))
    return f"{x:.2f}".rstrip("0").rstrip(".").replace(".", ",")


def points(x):
    return f"{fmt(x)} punto" if abs(x - 1) < EPS else f"{fmt(x)} puntos"


def enumerate_es(items):
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " y " + items[-1]


def load(arg):
    if arg == "-":
        return json.load(sys.stdin)
    if arg.lstrip().startswith("{"):
        return json.loads(arg)
    with open(arg, encoding="utf-8") as f:
        return json.load(f)


def is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def parse(data):
    if not isinstance(data, dict):
        raise ValueError("La entrada debe ser un objeto JSON con 'criteria' y 'alternatives'.")
    criteria, alternatives = data.get("criteria"), data.get("alternatives")
    if not isinstance(criteria, list) or not criteria:
        raise ValueError("Falta 'criteria' (lista no vacía).")
    if not isinstance(alternatives, list) or len(alternatives) < 2:
        raise ValueError("'alternatives' debe contener al menos dos alternativas.")

    names, weights = [], []
    for c in criteria:
        name = str(c.get("name", "")).strip() if isinstance(c, dict) else ""
        if not name:
            raise ValueError("Cada criterio necesita 'name'.")
        if name in names:
            raise ValueError(f"Criterio duplicado: {name}")
        w = c.get("weight")
        if not is_number(w) or not WEIGHT_MIN <= w <= WEIGHT_MAX:
            raise ValueError(f"Peso de '{name}' fuera de rango ({WEIGHT_MIN}-{WEIGHT_MAX}): {w}")
        names.append(name)
        weights.append(float(w))

    alts = {}
    for a in alternatives:
        aname = str(a.get("name", "")).strip() if isinstance(a, dict) else ""
        if not aname:
            raise ValueError("Cada alternativa necesita 'name'.")
        if aname in alts:
            raise ValueError(f"Alternativa duplicada: {aname}")
        scores = a.get("scores")
        if not isinstance(scores, dict):
            raise ValueError(f"'{aname}' necesita 'scores' (criterio -> valoración).")
        unknown = sorted(set(scores) - set(names))
        if unknown:
            raise ValueError(f"'{aname}' valora criterios que no existen: {', '.join(unknown)}")
        row = []
        for n in names:
            s = scores.get(n)
            if s is None:
                raise ValueError(f"Falta la valoración de '{aname}' en '{n}'.")
            if not is_number(s) or not SCORE_MIN <= s <= SCORE_MAX:
                raise ValueError(f"Valoración de '{aname}' en '{n}' fuera de rango ({SCORE_MIN}-{SCORE_MAX}): {s}")
            row.append(float(s))
        alts[aname] = row
    return names, weights, alts


def weight_sensitivity(i, weights, alts, tot, winner):
    """Peso del criterio i a partir del cual otra alternativa empata con la ganadora (el más cercano)."""
    nearest = None
    for x in alts:
        if x == winner:
            continue
        d = alts[winner][i] - alts[x][i]
        if abs(d) < EPS:
            continue
        tie_weight = weights[i] - (tot[winner] - tot[x]) / d
        if tie_weight < 0:
            continue
        distance = abs(tie_weight - weights[i])
        if nearest is None or distance < nearest[0]:
            nearest = (distance, tie_weight, x)
    return nearest


def report(names, weights, alts):
    tot = {a: sum(w * s for w, s in zip(weights, row)) for a, row in alts.items()}
    max_total = SCORE_MAX * sum(weights)
    ranking = sorted(alts, key=lambda a: -tot[a])
    out = []
    if len(alts) > MAX_ALTERNATIVES:
        out += [f"> Aviso: hay {len(alts)} alternativas; las instrucciones del agente recomiendan como máximo {MAX_ALTERNATIVES}.", ""]

    out += ["## Matriz de decisión", "", "| Criterio | Peso | " + " | ".join(ranking) + " |", "|" + "---|" * (len(ranking) + 2)]
    for i, n in enumerate(names):
        cells = [f"{fmt(alts[a][i])} ({fmt(weights[i] * alts[a][i])})" for a in ranking]
        out.append(f"| {n} | {fmt(weights[i])} | " + " | ".join(cells) + " |")
    out.append("| **Total ponderado** | | " + " | ".join(f"**{fmt(tot[a])}**" for a in ranking) + " |")
    out.append("| % del máximo | | " + " | ".join(f"{tot[a] / max_total * 100:.0f} %" for a in ranking) + " |")
    out += ["", "Cada celda: valoración (valoración × peso)."]

    winner, second = ranking[0], ranking[1]
    margin = tot[winner] - tot[second]
    if margin < EPS:
        tied = [a for a in ranking if abs(tot[a] - tot[winner]) < EPS]
        out += ["", f"**Resultado**: empate entre {enumerate_es(tied)} con {fmt(tot[winner])}. "
                "La matriz no decide: revisa los pesos con los interesados o añade un criterio que discrimine."]
        return "\n".join(out)

    margin_pct = margin / max_total * 100
    out += ["", f"**Resultado**: gana **{winner}** con {fmt(tot[winner])} frente a {fmt(tot[second])} de {second} "
            f"(margen {fmt(margin)}, {fmt(round(margin_pct, 1))} % del máximo)."]
    contributions = sorted(((weights[i] * (alts[winner][i] - alts[second][i]), names[i]) for i in range(len(names))), reverse=True)
    top = contributions[0][0]
    deciders = sorted(n for c, n in contributions if abs(c - top) < EPS)
    positive = [f"{n} (+{fmt(c)})" for c, n in contributions if c > EPS]
    negative = [f"{n} ({fmt(c)})" for c, n in contributions if c < -EPS]
    verb = "aporta" if len(deciders) == 1 else "aportan cada uno"
    out.append(f"**Criterio que decide**: {enumerate_es(deciders)} {verb} {points(top)} al margen sobre {second}.")
    out.append(f"A favor de {winner}: {', '.join(positive) or 'ninguno'}. En contra: {', '.join(negative) or 'ninguno'}.")

    out += ["", "## Sensibilidad a los pesos", "",
            "| Criterio | Peso actual | Peso de empate (a partir del cual cambia el ganador) | Nueva ganadora | ¿Dentro de 1-3? |",
            "|---|---|---|---|---|"]
    weight_flip_in_range = False
    for i, n in enumerate(names):
        nearest = weight_sensitivity(i, weights, alts, tot, winner)
        if nearest is None:
            out.append(f"| {n} | {fmt(weights[i])} | Ninguno | — | — |")
            continue
        within = WEIGHT_MIN <= nearest[1] <= WEIGHT_MAX
        weight_flip_in_range |= within
        out.append(f"| {n} | {fmt(weights[i])} | {fmt(nearest[1])} | {nearest[2]} | {'Sí' if within else 'No'} |")

    out += ["", "## Sensibilidad a las valoraciones", "",
            f"Cambio mínimo en un único criterio para que otra alternativa empate con {winner}:", "",
            f"| Criterio | Bajada necesaria en {winner} | Subida necesaria en otra alternativa |",
            "|---|---|---|"]
    one_point_flip = False
    for i, n in enumerate(names):
        down = margin / weights[i]
        down_ok = alts[winner][i] - down >= SCORE_MIN - EPS
        up = None
        for x in ranking[1:]:
            need = (tot[winner] - tot[x]) / weights[i]
            if alts[x][i] + need <= SCORE_MAX + EPS and (up is None or need < up[0]):
                up = (need, x)
        if (down_ok and down <= 1 + EPS) or (up and up[0] <= 1 + EPS):
            one_point_flip = True
        down_txt = points(down) if down_ok else "No posible"
        up_txt = f"{points(up[0])} ({up[1]})" if up else "No posible"
        out.append(f"| {n} | {down_txt} | {up_txt} |")

    if one_point_flip or margin_pct < 5:
        verdict = ("**Frágil**: un cambio de un punto en una sola valoración, o un margen inferior al 5 %, basta para empatar "
                   "o invertir el resultado. Respalda esas valoraciones con evidencia antes de decidir.")
    elif weight_flip_in_range:
        verdict = ("**Sensible a los pesos**: un peso dentro del rango 1-3 invierte el resultado. "
                   "Acuerda los pesos con los interesados y documéntalos en el ADR.")
    else:
        verdict = ("**Robusta**: ningún peso dentro del rango 1-3 ni ningún cambio de un punto en una sola valoración "
                   "invierte el resultado.")
    out += ["", f"**Robustez**: {verdict}"]
    return "\n".join(out)


def main(argv):
    if len(argv) != 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0 if len(argv) == 2 else 2
    try:
        names, weights, alts = parse(load(argv[1]))
    except (OSError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    print(report(names, weights, alts))
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv))
