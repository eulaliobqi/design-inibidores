# Consolidação parcial — 03/10/2026 (atualizada 12h57)

Base: `outputs/md10_L` (24/24), `outputs/md10_M` (16/24), `outputs/ranking_parcial_0310` (gerado hoje no servidor, `--lang pt`).
Todos os números abaixo vêm de `analysis_summary.json` dessas pastas; nada foi estimado.

## 1. Andamento
- **Atualização 12h57:** **43/48** (L 24/24, M 19/24), zero erros, GPU só com a MD (58%). Ritmo da manhã: 3 MDs em ~3,5 h (~1h10 cada). M fecha por volta das 18h; E3 ainda inexistente, `md-controls` ainda aguardando.
- MDs de 10 ns: **40/48**, zero erros. L completa; M faltam 8 (~8 h). A GPU ficou livre: o `gore-ph10` terminou às 04:25 (`logs/05.all.done`).
- `two-fronts` e `md-controls` vivos. **E3 (`delta_paired_*.json`) ainda não existe**; `md-controls` está parado esperando-o (log: "aguardando o E3"), portanto as iscas por candidato só começam depois.

## 2. O que as 40 MDs mostram (distância âncora–Asp189 no último quadro)
| | ≤ 4 Å | ≤ 5,5 Å | > 10 Å (saiu do bolso) |
|---|---|---|---|
| Linear (24) | 2 (NGGRPDAP 2,74; GQNDS 3,77) | 7 | 6 (GISGS, TDETG, GGPSTG, GGDINPG, GGPSPES, HGGGGSG) |
| Macrociclo (16) | 2 (GGKPGEP 2,71; GGHSE 3,07) | 5 | 3 (HSQPGSPTGG, QSPDFPNPPNNH, GQNDS) |

- A maior parte dos complexos **não mantém** a âncora em S1 em 10 ns; os que mantêm são os que já partiram perto (≤ 3,5 Å), o que confirma a decisão de 02/10 de tratar a ocupância como descritiva.
- Casos de atenção: `HGGGGSG` (L) e `HSQPGSPTGG` (M) terminam a 38 e 35 Å, com 200 e 63 quadros de salto de imagem; `GGDINPG` (L) e `QSPDFPNPPNNH` (M) também têm saltos (114 e 151). Distâncias dessas MDs devem ser lidas com a correção de PBC verificada.
- **Lacuna de análise:** `peptide_rmsd_local_nm_last10ns` está `None` em todos os sistemas a partir de Dsaccharalis (L) e nos de M depois dos três primeiros. Parece ser coluna ausente nas análises mais novas, não RMSD ruim; precisa ser recalculada (com a correção de PBC, ver `feedback_pbc_rmsd`) antes de se afirmar estabilidade estrutural.
- `analysis_summary_prefix_glup_bug.json` ainda existe ao lado do arquivo atual em `md10_L`: conferir que o ranqueamento lê só o corrigido.

## 3. Ranqueamento parcial (camadas A/B/C/P)
- **Linear: 24/24 na camada A — mas isso não discrimina nada.** Falta o E3, então nenhum candidato falha o critério Δ>0; o único filtro ativo é o QC de pose (todos passam). Todos saem `provisional`.
- **Macrociclo:** 6 em A, 10 em B (todos por `ring_strict`, anel não íntegro), 8 em P (MD pendente).
- Macrociclos A com âncora no bolso: só `GGHSE` (S. frugiperda; ocupância 0,99). Os demais A têm ocupância ≈ 0.
- Conclusão honesta: **até o E3 e as iscas não há candidato recomendável**; a lista de hoje é "sobreviveu aos filtros disponíveis", não "deve inibir".

## 4. Pendências, na ordem
1. Fim das 8 MDs de M (manhã/tarde de 03/10).
2. E3 (1.413 predições, 15–20 h) → matriz 8×8, E8, E9.
3. `md-controls` (iscas por candidato, 6–9 h) → decisão do controle negativo Asp/Leu.
4. Recalcular RMSD local com PBC e regenerar `analysis_summary.json` (ver §2).
5. Rodar `rank_final_candidates.py` no ambiente com matplotlib (o python do sistema não tem; hoje saiu CSV/JSON/MD sem a figura).
6. Preencher os `[[PENDING]]` de 3.9, 3.10, 3.11, Resumo e 4.1; referências/autores no fim.

## 5. Pontos abertos para decisão
- Lançar `md-controls` das iscas **sem esperar o E3**? Hoje o script bloqueia nele; a GPU fica só com a MD enquanto isso.
- Retomar o `gore-ph10` não é mais necessário (terminou).

## 6. Retomada à noite (conferir nesta ordem)
```bash
ssh eulalio@200.235.143.10      # se der timeout: VPN -> openvpn-gui.exe --connect vpn-UFV-config.ovpn
cd ~/design-inibidores && python3 -c "
import json
d=json.load(open('outputs/md10_M/summary.json'))
print('M', sum(v.get('status')=='done' for v in d.values()), '/24', [k for k,v in d.items() if v.get('status')=='erro'])"
screen -ls | grep -E 'two-fronts|md-controls'
ls data-b23-scoring/results/delta_paired_*.json     # E3 comeca quando M fechar
```
- Se M fechou (24/24): rodar `rank_final_candidates.py` de novo (4 MDs de macrociclo saem de P) e atualizar a seção 3 deste documento.
- Duas decisões do usuário ainda abertas: (1) lançar `md-controls` sem esperar o E3; (2) recalcular RMSD local com PBC nos 40+ sistemas (coluna `peptide_rmsd_local_nm_last10ns` está `None` na maioria).
- Nada foi alterado no servidor nesta sessão além de `outputs/ranking_parcial_0310/` (saída nova, sem sobrescrever nada).
