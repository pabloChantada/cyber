# Presentación — Análise e detección de intrusións (CIC-IDS2017)

Presentación de ~8 minutos preparada para [presenterm](https://github.com/mfontanini/presenterm),
cubrindo **tanto a Práctica 1 (análise do dataset)** como **a Práctica 2 (modelos de IA)**.

## Reparto en 4 bloques (~2 min cada un)

| Bloque | Relator/a | Contido |
|--------|-----------|---------|
| **1** | Persoa 1 | Contexto, dataset, limpeza, codificación, desbalanceo, PCA/UMAP |
| **2** | Persoa 2 | Preprocesado xustificado + AdaBoost (config + resultados + augmentation) |
| **3** | Persoa 3 | GAN: motivación, arquitectura híbrida, resultados binarios |
| **4** | Persoa 4 | GAN multiclase, comparativa, conclusións, traballo futuro |

Cada bloque ábrese cunha **slide separadora** centrada verticalmente (`▎ BLOQUE N`)
para que sexa doado cambiar de relator.

## Como executala

### 1. Instalar presenterm

```bash
cargo install --locked presenterm
```

### 2. Executar

```bash
presenterm presentacion.md
```

Para un tema distinto:

```bash
presenterm -t dark presentacion.md
# Temas dispoñibles: dark, light, catppuccin-*, tokyonight-storm, ...
```

## Controis

- **→ / l / Space**: seguinte paso/diapositiva
- **← / h**: diapositiva anterior
- **Ctrl+P**: modal co índice de diapositivas
- **?**: axuda de atallos
- **Ctrl+C**: saír

## Speaker notes en paralelo

A presentación inclúe notas para cada relator/a. Para velas en paralelo:

```bash
# Terminal 1 — Presentación principal
presenterm --publish-speaker-notes presentacion.md

# Terminal 2 — Só notas do relator (ideal para un segundo monitor)
presenterm --listen-speaker-notes presentacion.md
```

## Exportar a PDF

```bash
presenterm --export-pdf presentacion.md
```

## Estrutura detallada

| # | Diapositiva | Bloque | Tempo aprox. |
|---|-------------|--------|--------------|
| 1 | Portada | — | 10 s |
| 2 | Índice e reparto | — | 15 s |
| 3 | ▎ Bloque 1 (separador) | 1 | 5 s |
| 4 | Contexto — NIDS sobre CIC-IDS2017 | 1 | 25 s |
| 5 | Limpeza inicial | 1 | 25 s |
| 6 | Características e codificación | 1 | 25 s |
| 7 | Desbalanceo de clases | 1 | 25 s |
| 8 | Análise de correlación e PCA | 1 | 25 s |
| 9 | ▎ Bloque 2 (separador) | 2 | 5 s |
| 10 | AdaBoost — Configuración | 2 | 50 s |
| 11 | AdaBoost — Resultados + augmentation | 2 | 60 s |
| 12 | ▎ Bloque 3 (separador) | 3 | 5 s |
| 13 | GAN — Motivación | 3 | 35 s |
| 14 | GAN — Arquitectura | 3 | 35 s |
| 15 | GAN binaria — Resultados | 3 | 45 s |
| 16 | ▎ Bloque 4 (separador) | 4 | 5 s |
| 17 | GAN multiclase | 4 | 40 s |
| 18 | Comparativa | 4 | 35 s |
| 19 | Conclusións | 4 | 30 s |
| 20 | Traballo futuro | 4 | 15 s |
| 21 | Peche | — | 5 s |

**Total estimado: ~8 min** (dentro do rango 8–10 do enunciado)

## Cobertura dos requisitos do enunciado

✅ **Análise dos datos** → Bloque 1 (distribución, PCA, UMAP, correlación)
✅ **Preprocesado** → Bloque 1+2 (nulos, outliers, codificación, normalización, SMOTE)
✅ **Técnicas e modelos empregados** → Bloques 2+3 (AdaBoost + GAN)
✅ **Desafíos atopados** → Slide "Conclusións" e en cada bloque
✅ **Resultados** → Bloques 2+3 con métricas en test
✅ **Comparativa** → Bloque 4 con táboas binario/multiclase
✅ **Participación equitativa** → 4 bloques de ~2 min cada un
✅ **Duración 8–10 min** → estimado ~8 min