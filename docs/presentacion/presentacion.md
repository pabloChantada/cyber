---
title: "Análise e detección de intrusións"
sub_title: "CIC-IDS2017 · **AdaBoost** vs **GAN**"
author: "Cabaleiro · Chantada · Ferreiro · Romero"
---

<!-- end_slide -->

# Índice e reparto

<!-- column_layout: [1, 1] -->

<!-- column: 0 -->

## Bloque 1 — *Dataset e análise*

- Contexto e CIC-IDS2017
- Limpeza e análise exploratoria
- Desbalanceo, PCA e UMAP

## Bloque 2 — *Preprocesado e AdaBoost*

- Decisións de preprocesado
- AdaBoost: configuración e resultados

<!-- column: 1 -->

## Bloque 3 — *GAN: deseño e binario*

- Motivación e arquitectura híbrida
- Resultados na clasificación binaria

## Bloque 4 — *GAN multiclase e comparativa*

- Multiclase e data augmentation
- Comparativa, conclusións e futuro

<!-- reset_layout -->

> Duración: ~8 min · 2 min por relator/a

<!-- speaker_note: Esta slide é só organizativa. Léese rápido e pasa ao bloque 1. -->

<!-- end_slide -->

<!-- jump_to_middle -->

# ▎ BLOQUE 1

# Dataset e análise exploratoria

*Relator/a 1*

<!-- end_slide -->

# Contexto — NIDS sobre CIC-IDS2017

**Obxectivo**: sistema de detección de intrusións a **nivel de rede** (NIDS), alertando sobre posibles intrusións sen actuar directamente.

<!-- pause -->

## CIC-IDS2017

- **5 días** de tráfico sintético en entorno controlado.
- **~3,1 M fluxos** × **85 características** na versión `TrafficLabelling`.
- **14 clases**: BENIGN + varios DoS/DDoS, Web Attacks, Bot, Heartbleed, PortScan, Infiltration, FTP/SSH-Patator.

<!-- pause -->

## Por que **TrafficLabelling** e non `MachineLearningCVE`

A versión "ML-ready" descarta información útil (timestamps, IPs...) que é valiosa para análise, agregación e preprocesamento propios.

<!-- speaker_note: Presentarse. Mencionar que traballamos sobre os fluxos xa extraídos, non sobre pcaps. O tamaño do dataset é un reto pero tamén unha oportunidade. -->

<!-- end_slide -->

# Limpeza inicial

<!-- column_layout: [1, 1] -->

<!-- column: 0 -->

## Nulos

- **288 602 filas** con NaN → todas no ficheiro `Thursday-Morning-WebAttacks`.
- **1 358 NaN** adicionais agrupados en `FlowBytes/s`.
- Decisión: **eliminación directa** (imputación imposible, fila completa ausente).

<!-- column: 1 -->

## Valores infinitos

- `±∞` agrupados en 2 columnas, **1 509 mostras**.
- Decisión: **eliminación** (fracción desprezable do dataset).

## Outliers físicos

- **Valores negativos** en duracións temporais → reducidos a **0** (bugs coñecidos do CICFlowMeter).
- `TotalLengthOfBwdPackets` truncado ao **p99**.
- `FlowBytes/s` **conservado**: captura os ataques de tráfico masivo.

<!-- reset_layout -->

<!-- speaker_note: Recalcar que os bugs do CICFlowMeter están documentados. A decisión de non truncar FlowBytes/s é clave: eses "outliers" son o que queremos detectar. -->

<!-- end_slide -->

# Características e codificación

<!-- pause -->

## Categóricas

- **Portos**: identificamos os máis frecuentes (22, 21, 53, 80, 443, 8080...) e codificamos mediante **One-Hot**, agrupando o resto nunha categoría paraugas `outro`.
- **Protocolo**: só 3 valores → **One-Hot** (conservamos `0.0` a pesar da súa baixa frecuencia, ~10⁻³, por significatividade).

<!-- pause -->

## Columnas eliminadas

- **IDs e IPs** → introducen sesgo directo.
- **Timestamps** → sesgo temporal por día/ataque.
- **Bulk features** (todas a 0) e **duplicadas** (ex: `TotalFwdPackets == SubflowFwdPackets`, bug documentado).

<!-- pause -->

## Normalización

- **RobustScaler** para numéricas (distribucións *power-law* e bimodais).
- **MinMaxScaler** especial para `Active*`, `Idle*`, `*IATMin` (IQR ≈ 0 por exceso de ceros).

<!-- speaker_note: O tratamento especial de Active/Idle é un bo detalle para mostrar que non se aplicou unha receita cega: analizamos por que o RobustScaler fallaba. -->

<!-- end_slide -->

# Desbalanceo de clases

## Escenario binario

- `BENIGN`: 2 273 097 (80,3 %) · `ATTACK`: 557 646 (19,7 %) → ratio **4,08 : 1**.

## Escenario multiclase — **crítico**

- `BENIGN`: 2,27 M · `Heartbleed`: **11 mostras** → ratio **200 000 : 1**.

<!-- pause -->

## Estratexia combinada

- **Undersampling** das 4 maioritarias (`BENIGN`, `DoS Hulk`, `PortScan`, `DDoS`) a 50 000 / 20 000.
- **SMOTE** das minoritarias → mínimo 2 000 mostras (k_neighbors=5 para `Heartbleed`).

<!-- pause -->

> **Dataset final: 182 000 mostras** · ratio máxima **25 : 1** (fronte a 200 000 : 1 orixinal).
> Partición estratificada **70 / 15 / 15** → 127 400 / 27 300 / 27 300.

<!-- speaker_note: Xustificar por que podemos permitirnos undersampling: o dataset é moi grande. SMOTE é necesario especialmente para Heartbleed. A ratio 25:1 é moi manexable. -->

<!-- end_slide -->

# Análise de correlación e PCA

<!-- column_layout: [3, 2] -->

<!-- column: 0 -->

## Tres familias de alta correlación (r > 0,99)

1. **Conteo de paquetes e cabeceiras**
   `TotalFwdPackets`, `TotalBwdPackets`, `FwdHeaderLength`... (r > 0,999)
2. **Duración e tempos forward**
   `FwdIATTotal` ↔ `FlowDuration` (r = 0,999)
3. **Taxas de paquetes**
   `FwdPackets/s` ↔ `FlowPackets/s` (r = 0,990)

<!-- column: 1 -->

## PCA

- **5 compoñentes** explican o **95 %** da varianza.
- Feature máis importante: **`FlowBytes/s`** (0,999) → consistente con DoS/DDoS.

<!-- reset_layout -->

<!-- pause -->

## UMAP

As clases **non forman clusters separados** en 2D → a proxección aproximada non é limitante; modelos como Random Forest ou NNs poden atopar fronteiras no espazo completo.

> Resultado final: **52 características predictoras** tras a selección.

<!-- speaker_note: As correlacións altísimas xustifican o PCA. Se FlowBytes/s domina con importancia 0,999, dinos algo do dominio: os ataques son esencialmente anomalías de volume. -->

<!-- end_slide -->

<!-- jump_to_middle -->

# ▎ BLOQUE 2

# AdaBoost — modelo base

*Relator/a 2*

<!-- end_slide -->

# AdaBoost — Configuración

Estimador base: **árbore de decisión**. Supervisado, rápido e axeitado para datos tabulares.

<!-- pause -->

## Busca de hiperparámetros

- Primeiro *grid search* exploratorio para validar a tubaxe.
- Final: **optimización bayesiana**.
  - 15 puntos iniciais aleatorios + 40 iteracións.
  - `n_estimators ∈ [15, 500]`, `learning_rate ∈ [0,0001, 2]`.
  - **Función obxectivo**: F1 micro en validación (robusta ó desbalanceo).

<!-- pause -->

## Mellores configuracións atopadas

| Escenario  | `n_estimators` | `learning_rate` | F1 micro |
| ---------- | -------------- | --------------- | -------- |
| Binario    | 390            | 1,91            | 0,909    |
| Multiclase | 434            | 0,706           | 0,656    |

<!-- speaker_note: A optimización bayesiana sobre parámetros enteiros non é trivial — citar a referencia a Garrido-Merchán & Hernández-Lobato. -->

<!-- end_slide -->

# AdaBoost — Resultados en test

<!-- column_layout: [1, 1] -->

<!-- column: 0 -->

## Binario

- Accuracy: **0,9144**
- Recall `ATTACK`: **0,98**
- Recall `BENIGN`: **0,73**
- AUC-ROC: **0,9474**

Matriz de confusión:
- ✅ 5 466 benignos · ✅ 19 498 ataques
- ⚠️ 2 034 FP · **302 FN**

<!-- column: 1 -->

## Multiclase

- Accuracy: **0,65**
- **F1 macro: 0,47**
- F1 weighted: 0,62
- AUC-ROC media: 0,9215

Ben en: `SSH-Patator`, `PortScan`, `DDoS`.
Mal en: `Heartbleed`, `Web Attack - *` (absorbidas por `BENIGN`).

<!-- reset_layout -->

<!-- pause -->

## Data augmentation con GAN — resultado neutro

127 400 mostras sintéticas engadidas → accuracy **0,9112** (vs 0,9144). **Sen mellora apreciábel**.

> O xerador aínda non converxía → as mostras sintéticas non tiñan a mesma calidade estatística cós datos reais.

<!-- speaker_note: Tempo estimado: ~4 min. O recall da clase ATTACK é altísimo (0,98) — en ciberseguridade é o que queremos. Os FP son aceptables. -->

<!-- end_slide -->

<!-- jump_to_middle -->

# ▎ BLOQUE 3

# GAN — deseño e binario

*Relator/a 3*

<!-- end_slide -->

# GAN — Motivación e formulación

<!-- column_layout: [1, 1] -->

<!-- column: 0 -->

## Probas exploratorias descartadas

- **Detector de anomalías**: adestrar só con `BENIGN` + ruído.
- Variante con máis exemplos malignos do dataset orixinal.

→ Ambas demasiado exploratorias.

<!-- column: 1 -->

## Versión final adoptada

- **Discriminador**: mostras reais coa etiqueta binaria (`BENIGN=1`, `ATTACK=0`) + sintéticas.
- **Xerador**: optimizado para que o discriminador as clasifique como `BENIGN`.

<!-- reset_layout -->

<!-- pause -->

> **Nin GAN non supervisada clásica nin condicionada**:
> formulación **adversaria híbrida** que aproveita as etiquetas reais na perda sen introducilas como entrada.

<!-- speaker_note: Este é o punto diferenciador do traballo. Explicar que nunha GAN clásica o discriminador só distingue real/falso; aquí fai dúas cousas á vez. -->

<!-- end_slide -->

# GAN — Arquitectura

<!-- column_layout: [1, 1] -->

<!-- column: 0 -->

## Adestramento do **Discriminador**

1. Recibe mostras **reais** + **sintéticas**.
2. Perda *CrossEntropy* coa etiqueta correspondente.
3. Aprende a distinguir a natureza dos exemplos.

## Adestramento do **Xerador**

1. Recibe vector aleatorio do **espazo latente**.
2. Discriminador actúa como **avaliador**.
3. Sempre recibe etiqueta `BENIGN` → tenta enganar.

<!-- column: 1 -->

## Hiperparámetros explorados

- Regularización (dropout)
- Tamaño de lote
- Dimensión do espazo latente
- Número de épocas

## Comportamento esperado

- Xogo de ganancia cero.
- Dinámica de equilibrio inestable.
- Oscilacións típicas das perdas.

<!-- reset_layout -->

<!-- speaker_note: Mencionar que o esquema da memoria (Figura 1) é moi ilustrativo. A dificultade principal é equilibrar ambas redes. -->

<!-- end_slide -->

# GAN binaria — Resultados en test

Mellor modelo na **época 310** (AUC-ROC val = 0,9499).

<!-- pause -->

<!-- column_layout: [1, 1] -->

<!-- column: 0 -->

## Métricas en test

| Métrica   | Valor  |
| --------- | ------ |
| Accuracy  | 0,9327 |
| Precision | 0,9273 |
| **Recall**| **0,9844** |
| F1-score  | 0,9550 |
| AUC-ROC   | 0,9544 |

<!-- column: 1 -->

## Matriz de confusión

- ✅ **19 492** ataques detectados
- ✅ **5 971** fluxos normais ben
- ⚠️ **1 529** falsos positivos
- ⚠️ **308** falsos negativos

<!-- reset_layout -->

<!-- pause -->

## Dinámica de adestramento

Perda do discriminador ↓ progresivamente · Perda do xerador ↑ con oscilacións → típico do adestramento adversario. **Limitación de recursos** impediu levar o xerador a converxer.

<!-- speaker_note: Recalcar o recall de 0,98: só 308 ataques sen detectar. Os FP son aceptables no contexto IDS. Tempo estimado: ~6 min. -->

<!-- end_slide -->

<!-- jump_to_middle -->

# ▎ BLOQUE 4

# Multiclase, comparativa e peche

*Relator/a 4*

<!-- end_slide -->

# GAN multiclase

Mesmo discriminador, mantendo as **15 etiquetas orixinais**.

<!-- column_layout: [1, 1] -->

<!-- column: 0 -->

## Métricas en test

| Métrica         | Valor  |
| --------------- | ------ |
| Accuracy        | 0,6976 |
| Precision macro | 0,8912 |
| Recall macro    | 0,6814 |
| **F1 macro**    | **0,7032** |
| F1 weighted     | 0,7409 |
| AUC-ROC media   | 0,966  |

<!-- column: 1 -->

## Análise por clase

**AUC ≈ 1,00** en:
- `Bot`, `DDoS`, `FTP-Patator`
- `Heartbleed`, `SSH-Patator`

**Problemáticas**:
- `Web Attack - Brute Force`
- `Web Attack - XSS`
- Confusións con `DoS Slowhttptest`

<!-- reset_layout -->

<!-- pause -->

> Boa separación por score (AUC media 0,966) **non implica** boa clasificación final — a matriz de confusión revela confusións entre ataques con patróns próximos.

<!-- speaker_note: Explicar o paradoxo AUC alta / accuracy moderada: separación vs asignación final son cousas distintas. -->

<!-- end_slide -->

# Comparativa — Test

## Binario

| Modelo               | Accuracy   | F1 `ATTACK` | AUC-ROC    |
| -------------------- | ---------- | ----------- | ---------- |
| AdaBoost             | 0,9144     | 0,94        | 0,9474     |
| AdaBoost aumentado   | 0,9112     | 0,94        | 0,9477     |
| **GAN**              | **0,9327** | **0,9550**  | **0,9544** |

<!-- pause -->

## Multiclase

| Modelo   | Accuracy   | F1 macro   | F1 weighted | AUC-ROC    |
| -------- | ---------- | ---------- | ----------- | ---------- |
| AdaBoost | 0,65       | 0,47       | 0,62        | 0,9215     |
| **GAN**  | **0,6976** | **0,7032** | **0,7409**  | **0,9656** |

<!-- pause -->

A **GAN** acada mellores métricas globais nos dous escenarios, con maior **custo de adestramento e axuste**.

<!-- speaker_note: Resumir: AdaBoost = rápido, interpretable, estable. GAN = mellor rendemento pero máis esixente. -->

<!-- end_slide -->

# Conclusións

<!-- column_layout: [1, 1] -->

<!-- column: 0 -->

## AdaBoost

- Modelo base **moi forte**.
- **Rápido**, **estable**, **interpretable**.
- Mellor relación custo/rendemento.

## GAN

- **Mellores métricas** en test (binario e multiclase).
- Complexidade real: custa converxer, especialmente o xerador.
- Aporta **xeración de mostras sintéticas** como valor engadido.

<!-- column: 1 -->

## Desafíos atopados

- **Desbalanceo severo** (200 000 : 1) → combinar undersampling + SMOTE.
- **Bugs do dataset** (CICFlowMeter) → tratamento físico de outliers.
- **Adestramento adversario** → oscilacións e converxencia lenta.
- **Recursos limitados** → non alcanzamos o equilibrio ideal da GAN.

<!-- reset_layout -->

<!-- speaker_note: Enmarcar a comparativa como rica porque non hai gañador absoluto: depende do criterio (simplicidade vs rendemento). -->

<!-- end_slide -->

# Traballo futuro

- Explorar **GANs condicionais** ou unha **GAN por clase** para mellorar as clases multiclase difíciles.
- Usar unha GAN condicional ben adestrada como **xerador de datos** para alimentar un AdaBoost multiclase mellorado.
- Adestramentos **máis longos** e estratexias de estabilización (WGAN, *gradient penalty*).
- Incorporar modelos temporais (LSTM, Transformer) sobre os fluxos como secuencias.

<!-- end_slide -->

<!-- jump_to_middle -->

# Grazas!

## Preguntas?

*Cabaleiro · Chantada · Ferreiro · Romero*
*Curso 2025–2026*