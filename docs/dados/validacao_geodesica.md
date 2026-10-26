# Validação geodésica

Gerado em 2026-10-26 com `uv run python scripts/validar_geodesica.py` (a partir de `backend/`).

Cada instância roda o Sort_and_Closest-Pair no plano projetado e a força bruta
com Haversine na esfera. A verificação **diverge** quando o par escolhido no plano
está, na esfera, mais de 1 mm mais longe do que o par geodesicamente mais próximo.
Pares diferentes empatados contam como confirmados.

**Total: 2 divergência(s) em 404 instâncias.**

| Região | Tipo | Instâncias | n (mín–máx) | Divergências | Maior diferença (km) |
|---|---|--:|--:|--:|--:|
| Japão | Catálogo completo | 1 | 3695–3695 | 0 | 0.000000 |
| Japão | Subamostras do real | 50 | 112–983 | 1 | 0.000318 |
| Japão | Sintético uniforme | 50 | 112–983 | 0 | 0.000000 |
| Chile | Catálogo completo | 1 | 4557–4557 | 0 | 0.000000 |
| Chile | Subamostras do real | 50 | 112–983 | 0 | 0.000000 |
| Chile | Sintético uniforme | 50 | 112–983 | 1 | 0.007572 |
| Califórnia | Catálogo completo | 1 | 7714–7714 | 0 | 0.000000 |
| Califórnia | Subamostras do real | 50 | 112–983 | 0 | 0.000000 |
| Califórnia | Sintético uniforme | 50 | 112–983 | 0 | 0.000000 |
| Turquia | Catálogo completo | 1 | 1509–1509 | 0 | 0.000000 |
| Turquia | Subamostras do real | 50 | 112–983 | 0 | 0.000000 |
| Turquia | Sintético uniforme | 50 | 112–983 | 0 | 0.000000 |

Dados por instância: [`validacao_geodesica.csv`](./validacao_geodesica.csv).
