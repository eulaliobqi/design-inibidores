# Estado ao fim do dia — 02/10/2026, 13h50

Documento de retomada. Complementa `ESTADO_FIM_DO_DIA_2026-10-01.md` (os comandos de conferência de lá continuam valendo)
e `PLANO_CONTROLE_NEGATIVO_2026-10-02.md`.

## 1. O que conferir amanhã

```bash
ssh eulalio@200.235.143.10
cd ~/design-inibidores && python3 -c "
import json
for F in ('L','M'):
    d=json.load(open('outputs/md10_%s/summary.json'%F))
    print(F, sum(v.get('status')=='done' for v in d.values()), '/24',
          'erros:', [k for k,v in d.items() if v.get('status')=='erro'])"
screen -ls | grep -E 'two-fronts|md-controls|gore-ph10'
ls data-b23-scoring/results/delta_paired_*.json     # E3: existe quando ele terminar
nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader   # quem está na GPU
```

**Ao sair (13h50):** 25 de 48 MDs (L 22/24, M 3/24), **zero erros**; `two-fronts` e `md-controls` vivos; E3 ainda não existe.

## 2. Ponto de atenção: a GPU está compartilhada

- Desde ~09h30 roda `screen gore-ph10` (`bin/03_ph10_e_s102.sh`, em `~/GOREs-boltz`), um job Boltz-2 de **outro trabalho seu**, na mesma GPU.
- Efeito medido: a MD caiu de ~101 para ~61 ns/dia (de ~75 min para ~2h40 por MD). Entre 09h37 e 13h30 fechou só 1 MD.
- **Previsão com o ritmo atual:** 23 MDs restantes ≈ 60 h, e não 30–40 h. Sem o job concorrente volta ao ritmo de ~75 min.
- **Pausado por pedido do usuário às ~14h** (`SIGSTOP`, reversível; nada foi encerrado nem perdeu progresso). PIDs: 2202359 (script),
  2277887 (run_boltz.sh, chunk S/c07), 2277900 (boltz predict) e 2278129/2278130 (filhos). A GPU continua com ~9,8 GB reservados
  por ele, o que não atrapalha a MD (16 GB no total).
- **Retomar quando o E6 e o E3 terminarem:** `ssh eulalio@200.235.143.10 'kill -CONT 2202359 2277887 2277900 2278129 2278130'`
  (os mesmos 5 PIDs estão também em `~/gore_paused_pids.txt` no servidor).
  Conferir antes com `ps -o pid,stat -p 2202359,2277900` (devem estar em `T`); se algum já tiver terminado, o PID some e o `kill` avisa.
- Esperado: a MD volta a ~100 ns/dia (~75 min por MD) e as 23 restantes fecham em ~30–40 h.

## 3. Decisões tomadas hoje (todas no manuscrito EN e PT, commitadas)

1. **Ocupância de S1 rebaixada** de critério a descrição secundária (segue a pose inicial). Camadas: A = QC de pose + Δ pareado > 0
   (+ anel estrito no macrociclo); B = falha um; C = falha dois ou mais; P = MD pendente. Ordem interna: Δ, E2, ocupância.
   Declarado em 2.9 como **mudança pós-dados** (após 16 MDs). `scripts/rank_final_candidates.py` atualizado.
2. **Controle negativo planejado, não lançado:** trocar a âncora por **Asp** e **Leu**, mesma pose, 10 ns; leitura = distância
   âncora–Asp189 / ponte salina. Gly/Ala/Ser não servem (Grzesiak 2000).
3. **Regra fixada antes das rodadas:** se iscas e controle negativo não se diferenciarem dos candidatos, saem por completo das
   análises, camadas e figuras, sem frase de ressalva. A calibração (iscas 5/5 = 1,00) já é dado e permanece.
4. Autores, afiliações, financiamento e conferência de citações ficam **para o fim** (decisão do usuário).
5. `Manuscrito_PT_leitura.docx` é o **único** documento de leitura (V3 removido).

## 4. Literatura nova (PubMed e Crossref conferidos)
Brandsdal 2006 (doi:10.1002/prot.20940), Helland 1999 (doi:10.1006/jmbi.1999.2654), Grzesiak 2000 (doi:10.1006/jmbi.2000.3935).
Todas entram na conferência final de referências que o usuário fará.

## 5. Sequência até fechar o artigo (sem mudança de dependência)
E6 (23 MDs) → E3 (1.413 predições, 15–20 h) → matriz 8×8, E8, E9 → `md-controls` (iscas, 6–9 h) → decisão do controle negativo →
recalcular camadas com `rank_final_candidates.py` → preencher os [[PENDING]] de 3.9, 3.10, 3.11, Resumo e 4.1.

## 6. Cuidados
- Parar processos por PID a partir de script copiado por scp; nunca `pkill -f` na linha do ssh nem `screen -X quit`.
- Reconstruir referências: `build_refs.py` regenera **só** o que está em `refs_doi.json`; as 8 referências manuais
  (Valaitis 1995/1999, Yang, Zhan, Nakonieczny, Karumbaiah, Severiche, Patarroyo 2020) vivem apenas em `refs_meta.json` e
  `refs_resolved.json`. Mesclar, nunca sobrescrever.
- SSH sem resposta costuma ser a VPN (`openvpn-gui.exe --connect vpn-UFV-config.ovpn`).

**Último commit antes deste documento:** `e6f23bb`.
