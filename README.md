# Pipeline — Desafio Desenvolver (Antecipação de Alertas "Don't Go")

Este pipeline foi construído e validado sobre as **amostras** fornecidas
(`desenvolver_dontgo.xlsx`, `desenvolver_apontamentos.xlsx`,
`Alarmes - Regra de Negocio_V2.xlsx`). Ele está pronto para ser
reaplicado sobre a **base completa** (arquivos `.parquet` de Telemetria
e a base completa de Apontamentos).

## ⚠️ Sobre os arquivos .parquet

O ambiente usado para montar este relatório não tem acesso à internet
nem às bibliotecas `pyarrow`/`fastparquet` necessárias para ler `.parquet`.
Por isso, todo o desenvolvimento e validação foi feito sobre as amostras
em `.xlsx`. Para rodar este pipeline sobre a base completa, você tem duas
opções:

1. **No seu ambiente local** (Jupyter, Colab, VS Code): instale
   `pip install pandas pyarrow scikit-learn matplotlib` e troque
   `pd.read_excel(...)` por `pd.read_parquet(...)` nos três scripts.
2. **De volta nesta conversa**: se converter os `.parquet` para `.csv`
   ou `.xlsx` antes de enviar, eu consigo ler e rodar o pipeline
   diretamente aqui.

## Arquivos

- `rule_engine.py` — motor de regras que aplica a aba CMA sobre a
  Telemetria e recalcula `Is_Dont_Go`. Inclui a validação empírica que
  mostrou que o recálculo literal (ignorando a nuance de texto de
  SITUACAO) gera falsos positivos — por isso o pipeline **usa o
  `Is_Dont_Go` original como rótulo oficial**, e usa a CMA apenas para
  gerar features (ver `feature_engineering.py`).
- `feature_engineering.py` — cria as features temporais (Apontamentos)
  e de contagem/recência de alarmes (Telemetria), e constrói o alvo
  prospectivo `alvo_dont_go_proxima_1h` (horizonte configurável via
  `JANELA_PREDICAO_MIN`).
- `modelagem.py` — split temporal (sem embaralhamento), baselines
  (classe majoritária + heurística de regra de negócio), Regressão
  Logística, Random Forest, métricas (precision/recall/F1/AUC-PR),
  matriz de confusão e importância de features (Gini + permutation).

## Como rodar sobre a base completa

```bash
# 1) trocar os caminhos dos arquivos de entrada nos scripts para os arquivos completos
# 2) rodar em sequência:
python3 rule_engine.py            # valida Is_Dont_Go x regras CMA
python3 feature_engineering.py    # gera features + alvo prospectivo
python3 modelagem.py              # treina e avalia os modelos
```

## Ressalva importante

Os resultados de modelagem obtidos sobre a amostra (F1 ~0.99 nos
modelos supervisionados) são **artefato do tamanho da amostra** (147
linhas, 1 equipamento, 1 incidente — ver Seção 5.2 e 6.2 do relatório)
e não devem ser reportados como desempenho esperado em produção. Rode
o pipeline sobre a base completa para obter números válidos.
