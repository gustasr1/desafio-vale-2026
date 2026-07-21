# 🚜 Predição de Alertas Críticos em Frotas de Mineração (Caminhões 793-D 2S)

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/Scikit_Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)

## 📌 Visão Geral do Projeto
Na operação diária de uma mina, os ciclos de atividade dos equipamentos pesados geram um volume massivo de dados de telemetria[cite: 2]. Os alertas críticos (conhecidos como *'don't go'*) representam condições de risco iminente mecânico ou operacional[cite: 2]. 

Este projeto aplica inteligência analítica e Machine Learning sobre mais de **37 milhões de registros brutos** para antecipar paradas não planejadas, focando especificamente nos gargalos operacionais da frota de caminhões **793-D 2S**.

**Pergunta de Negócio:** *Quais equipamentos da frota têm maior risco de gerar um alerta crítico nas próximas 4 horas?*[cite: 2]

---

## 🎯 Impacto Operacional
A solução converteu uma base de dados histórica em uma política de manutenção preditiva automatizada. O modelo desenvolvido alcançou um **Recall de 74%** e uma **Acurácia Global de 87%**. Na prática, o algoritmo é capaz de identificar e avisar a equipe de PCM sobre quase 3/4 das falhas catastróficas com **4 horas de antecedência**, permitindo o desvio da máquina para a oficina antes que a quebra ocorra em rampa.

---

## 🛠️ Metodologia e Pipeline de Dados

O fluxo analítico foi integralmente desenvolvido em Python, estruturado nas seguintes etapas:

1. **Cruzamento Temporal:** Unificação dos apontamentos de despacho e arquivos `.parquet` de telemetria utilizando `merge_asof` para alinhamento exato de fusos horários[cite: 2].
2. **Isolamento de Escopo:** Filtragem exclusiva para a frota 793-D 2S para evitar ruídos de outros equipamentos.
3. **Engenharia de Features:** Criação de uma variável alvo binária (`Alvo_4H`) baseada na janela de predição de 4 horas.
4. **Tratamento Contra Data Leakage:** Exclusão rigorosa de variáveis que poderiam enviesar o modelo (veja tabela abaixo).
5. **Modelagem:** Treinamento de um *Random Forest Classifier* com pesos balanceados (`class_weight='balanced'`) para lidar com a assimetria natural de dados de falhas industriais.

### Controle de Alterações e Limpeza de Dados

| Campo | Tratamento Aplicado | Justificativa Analítica |
| :--- | :--- | :--- |
| **`Is_Dont_Go`** | Excluído | Evitar *Data Leakage*. A coluna informa a falha no momento presente, dando a resposta antecipada ao modelo no treino[cite: 2]. |
| **`INICIO` e `FIM`** | Excluídos | Transformados na grandeza matemática `DURACAO_MINUTOS`. Algoritmos não processam datetimes puros[cite: 2]. |
| **`TAG` e `ID`** | Excluídos | Identificadores únicos sem valor preditivo. Evita que o modelo decore máquinas específicas[cite: 2]. |
| **`Nome_Operador`** | Excluído | Alta cardinalidade. Evita *overfitting* e viés sobre o comportamento de um operador específico[cite: 2]. |
| **`CLASSE`** | One-Hot Encoding | Categorias textuais convertidas em variáveis numéricas binárias (0 e 1) independentes[cite: 2]. |

---

## 🧠 Interpretabilidade (Abrindo a Caixa Preta)

A extração de *Feature Importances* da Floresta Aleatória revelou o verdadeiro padrão de degradação da frota. O modelo não decorou números aleatórios; ele mapeou uma cadeia clara de sintomas pré-falha:

1. **O Vilão Principal (Engine Coolant Level):** O cruzamento revelou mais de 20.000 alertas oscilando entre Ativo e Inativo (*flapping*) devido ao baixo nível de água/aditivo balançando no reservatório.
2. **Colapso de Comunicação (Rx Channel A/B):** Como consequência do superaquecimento, a rede CAN ("sistema nervoso" do caminhão) começa a perder pacotes de dados.
3. **Risco Operacional (Body Up):** Detecção de tentativas de movimentação do equipamento com a caçamba levantada, gerando torções prejudiciais ao chassi.

---

## 🚀 Produto Final

O projeto entrega um script em Python de rápida execução que:
- Ingesta os dados mais recentes da telemetria.
- Roda as predições de risco silenciosamente.
- Gera e exporta um relatório executivo automático em Excel (`.xlsx`) listando apenas a *TAG*, *Data/Hora* e o *Sintoma* dos caminhões que precisam de intervenção imediata, otimizando o fluxo de manutenção sem a necessidade e o custo de processamento de dashboards complexos.

---

## 👤 Autor

**Gustavo Santiago Rosa**  
