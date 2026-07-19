"""Funções puras de análise de persistência competitiva (Frente 2).

Sem dependência de MDAnalysis/GROMACS aqui — mantidas testáveis com dado
sintético. A orquestração real (leitura de trajetória) fica em
deep_test_persistence.py.
"""


def occupancy_fraction(distances: list, cutoff: float = 4.0) -> float | None:
    """Fração de frames com distância <cutoff (padrão salt-bridge/H-bond, 4 A).
    Retorna None se a lista estiver vazia (sem dado, não fabricar 0.0)."""
    if not distances:
        return None
    n_within = sum(1 for d in distances if d < cutoff)
    return n_within / len(distances)


def find_anchor_residue(distances_per_residue: dict) -> int:
    """Descobre empiricamente qual resíduo do peptídeo fica mais perto do
    Asp-S1 em média — não assume C-terminal (5/13 candidatos do TOP-13 não
    terminam em Arg/Lys, ver plano)."""
    means = {res_idx: sum(d) / len(d) for res_idx, d in distances_per_residue.items() if d}
    return min(means, key=means.get)
