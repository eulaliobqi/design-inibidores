# Estado ao fim do dia — 01/10/2026, 23h00

Documento de retomada. Leia este primeiro amanhã; os detalhes estão em `AUDITORIA_2026-10-01.md`,
`PLANO_DE_ANALISES_2026-10-01.md` e `PLANO_DE_TRABALHO_2026-10-01.md`.

## 1. O que conferir amanhã, em ordem

```bash
ssh eulalio@200.235.143.10
cd ~/design-inibidores && python3 -c "
import json
for F in ('L','M'):
    d=json.load(open('outputs/md10_%s/summary.json'%F))
    print(F, sum(v.get('status')=='done' for v in d.values()), '/24',
          'erros:', [k for k,v in d.items() if v.get('status')=='erro'])"
screen -ls | grep -E 'two-fronts|md-controls'      # os dois devem aparecer
tail -3 outputs/e1_fix_pipeline.log                 # etapa atual
```

**Esperado amanhã de manhã:** cerca de **23 a 25 das 48 MDs** (ritmo medido de 75–105 min por MD; 17 às 23h00).
Se o número não tiver subido, o `mdrun` morreu — ver §4.

## 2. Onde o trabalho parou (tudo versionado e sincronizado)

| | Estado |
|---|---|
| Pipeline `two-fronts` | **rodando**: E6 com 17 de 48 MDs (L 14/24, M 3/24), **zero erros** |
| Laço de análise E7 | **rodando**: analisa cada MD ao terminar e para sozinho quando o pipeline chegar ao E7 |
| `md-controls` | **esperando** o E3 gravar `delta_paired_{L,M}.json` |
| Campanha de pH | **cancelada** neste artigo (72 MDs, 4–5 dias); scripts prontos para o artigo seguinte |
| Manuscrito EN e PT | atualizados; `manuscript/Manuscrito_PT_leitura.docx` é **um arquivo só** |
| Figuras | **26 de 26** dentro da especificação da revista |
| Disco | 855 GB livres (75% usado) — suficiente para as 31 MDs restantes |

**Último commit:** `754310e`. Servidor sincronizado.

## 3. Os três achados do dia que mudam a leitura dos resultados

1. **A pose inicial decide a triagem, não a química da âncora.** Nas 17 MDs, ocupância ≥0,70 ocorreu
   exatamente nos 3 sistemas que partiram a ≤3,5 Å do Asp189 e em nenhum dos 13 que partiram a ≥4,1 Å.
   GQNDS passa sem ter resíduo básico. ⇒ os 10 ns em boa medida repetem a pose do Boltz-2.
2. **O critério de S1 não tem especificidade no único conjunto de referência disponível.** As 5 iscas
   embaralhadas da calibração atingem ocupância 1,00, e 4 dos 6 inibidores reais também. ⇒ passar na
   triagem significa que a pose não se desfez, não que o peptídeo se liga.
3. **As figuras estavam todas fora da especificação** (216–330 mm; o texto chegaria a 3,7 pt impresso,
   contra o mínimo de 8 pt). Corrigido na origem, com `manuscript/figures/frontiers_style.py`.

## 4. Se algo tiver parado

- **`mdrun` morto:** o runner marca `status: erro` no `summary.json` e segue para o próximo candidato;
  conferir qual falhou e relançar só ele.
- **Pipeline morto:** `tail -30 outputs/e1_fix_pipeline.log`. Relançar exige **parar por PID, a partir de um
  script copiado por scp** — nunca `pkill -f` na linha do ssh nem `screen -X quit` (ver memória
  `feedback_ssh_servidor_cuidados`).
- **SSH sem resposta:** quase sempre é a VPN, não o servidor. Reconectar com
  `& "C:\Program Files\OpenVPN\bin\openvpn-gui.exe" --connect vpn-UFV-config.ovpn`.
- **Nada precisa de intervenção para continuar:** os três laços são autônomos.

## 5. Decisões suas, que não dependem de processamento

1. **Como tratar no artigo o confundimento da pose inicial** (achado 1). Hoje está declarado em 3.9 e em
   4.4 (xi), com os números. A alternativa mais forte seria rebaixar a ocupância a critério secundário —
   mas isso mexe num procedimento já declarado e é decisão sua.
2. **O que fazer se a isca do candidato também ficar em S1** (os controles respondem isso): a entrega
   passaria a ser uma lista priorizada por não clivabilidade e escore, com a ressalva explícita.
3. **Seções dos autores** — lista, afiliações, contribuições, financiamento, conflito de interesses,
   declaração de IA e DOI do código. Não dependem de nenhum cálculo e já podem ser escritas.
4. **Conferir no texto completo** as citações Valaitis, Yang, Zhan e Severiche (pendência antiga).

## 6. Quanto falta de processamento

| Etapa | Tempo medido |
|---|---|
| E6, 31 MDs restantes | 39–54 h |
| E3, 1.413 predições | 15–20 h |
| Matriz 8×8, E8, E9 | ~1 h, em paralelo |
| 5 controles de MD | 6–9 h |
| **Até poder fechar o artigo** | **60–84 h ≈ 2,5 a 3,5 dias** |

A escrita (~1 dia) corre em paralelo e não está no caminho crítico.
