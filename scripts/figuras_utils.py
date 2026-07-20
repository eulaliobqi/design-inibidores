"""Módulo compartilhado para as figuras do artigo (2026-07-20).

Paleta e princípios da skill dataviz deste ambiente (references/palette.md),
modo claro (destino é documento estático — Word/apresentação, não web).
"""
import json
import subprocess

SSH_HOST = "eulalio@200.235.143.10"

# Paleta categórica — ordem fixa, nunca ciclada.
CATEGORICAL = {
    "azul": "#2a78d6", "verde": "#008300", "magenta": "#e87ba4",
    "amarelo": "#eda100", "aqua": "#1baf7a", "laranja": "#eb6834",
    "violeta": "#4a3aa7", "vermelho": "#e34948",
}

# Status — reservado, nunca reusado como série categórica.
STATUS = {"bom": "#0ca30c", "atencao": "#fab219", "serio": "#ec835a", "critico": "#d03b3b"}

# Sequencial azul, 3 passos usados na Fig 2 (4/5/6 A, claro->escuro).
SEQUENTIAL_BLUE_3 = ["#86b6ef", "#3987e5", "#1c5cab"]  # steps 250/400/550

# Rampa sequencial completa (100->700) para o heatmap da Fig 3.
SEQUENTIAL_BLUE_FULL = [
    "#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7",
    "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b",
]

GRID_COLOR = "#e1e0d9"
AXIS_COLOR = "#c3c2b7"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
TEXT_MUTED = "#898781"

TOP13 = [
    "SRTRR", "HRPRRPR", "RLREELKKAEEWLEKRRKEE", "SEEEVLAANEAYAAAHTAYN",
    "SALASIAAHQATFLAYLESK", "MGSLTAYLEAYAAENAAALA", "MGYLTAYHQALAAQNAALLA",
    "SARESIKKAYKTFLERYKKL", "VRYRR", "VRTRR", "VRRPR", "HRPRRSR", "HRPRRPK",
]

SPECIES_ORDER = [
    "Agemmatalis", "Harmigera", "Msexta", "Bmori", "Pxylostella", "Slitura",
    "Sfrugiperda", "Onubilalis", "Dsaccharalis", "Hvirescens", "Cincludens",
]
SPECIES_LABELS = {
    "Agemmatalis": "A. gemmatalis", "Harmigera": "H. armigera", "Msexta": "M. sexta",
    "Bmori": "B. mori", "Pxylostella": "P. xylostella", "Slitura": "S. litura",
    "Sfrugiperda": "S. frugiperda", "Onubilalis": "O. nubilalis",
    "Dsaccharalis": "D. saccharalis", "Hvirescens": "H. virescens",
    "Cincludens": "C. includens",
}


def fetch_remote_json(remote_path: str) -> dict:
    """Busca um JSON real do servidor via SSH. Levanta RuntimeError explícito
    se a conexão ou o parse falhar — nunca retorna dado parcial/inferido."""
    result = subprocess.run(
        ["ssh", "-o", "ConnectTimeout=15", SSH_HOST, f"cat {remote_path}"],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"SSH falhou buscando {remote_path}: {result.stderr[-500:]}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"JSON invalido em {remote_path}: {e}\nstdout[:300]={result.stdout[:300]}")


def require_key(d: dict, key, context: str):
    """Acesso a dict que falha alto e claro (RuntimeError) em vez de KeyError
    opaco, quando um dado esperado do servidor está ausente."""
    if key not in d:
        raise RuntimeError(f"Dado ausente real: {context} (chave '{key}' não encontrada)")
    return d[key]


def classify_stability(mean_nm: float, std_nm: float) -> str:
    """Mesma regra ja documentada em artigo_resultados.md (Secao 3.11f):
    ESTAVEL_REPRODUTIVEL = media<0.30nm E DP<0.05nm; MARGINAL_REPRODUTIVEL = DP<0.10nm
    (independente da media); ALTA_VARIANCIA = DP>=0.15nm."""
    if std_nm >= 0.15:
        return "ALTA_VARIANCIA"
    if std_nm < 0.05 and mean_nm < 0.30:
        return "ESTAVEL_REPRODUTIVEL"
    if std_nm < 0.10:
        return "MARGINAL_REPRODUTIVEL"
    return "ALTA_VARIANCIA"
