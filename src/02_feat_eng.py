# %%

import pandas as pd
import numpy as np

df_frota = pd.read_parquet('../data/intermediate/dados_frota_2s.parquet')

df_frota = df_frota.sort_values(by='Data_Evento')

df_falhas = df_frota[df_frota['Is_Dont_Go'] == 1][['TAG', 'Data_Evento']].copy()
df_falhas.rename(columns={'Data_Evento': 'Data_Proxima_Falha'}, inplace=True)

df_target = pd.merge_asof(
    left=df_frota,
    right=df_falhas,
    by='TAG',
    left_on='Data_Evento',
    right_on='Data_Proxima_Falha',
    direction='forward'
)

df_target['Tempo_Ate_Falha'] = df_target['Data_Proxima_Falha'] - df_target['Data_Evento']

df_target['Alvo_4H'] = np.where(
    (df_target['Tempo_Ate_Falha'] <= pd.Timedelta(hours=4)) & (df_target['Tempo_Ate_Falha'].notna()), 
    1, 
    0
)

df_target.drop(columns=['Data_Proxima_Falha', 'Tempo_Ate_Falha'], inplace=True)

print("Distribuição da Variável Alvo:")
print(df_target['Alvo_4H'].value_counts())
# %%

y = df_target['Alvo_4H']

colunas_descarte = [
    'TAG',
    'Data_Evento',
    'Is_Dont_Go',
    'TIPO',
    'FROTA',
    'Alvo_4H'
]

X = df_target.drop(columns=colunas_descarte, errors='ignore')

X = pd.get_dummies(X, columns=['CLASSE'], drop_first=True)

print("Formato do X (Variáveis Preditivas):", X.shape)
print("Formato do y (Alvo):", y.shape)

print("\nColunas prontas para o modelo:")
print(X.columns.tolist())
# %%

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

colunas_finais_descarte = ['ID', 'INICIO', 'FIM', 'Nome_Operador_Anon']
X = X.drop(columns=colunas_finais_descarte, errors='ignore')

X = X.fillna(0)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)

print(f"Linhas para treinar: {X_train.shape[0]}")
print(f"Linhas para testar: {X_test.shape[0]}")
print("\nTreinando a Floresta Aleatória... (Pode levar alguns segundos)")

modelo_rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced', n_jobs=-1)
modelo_rf.fit(X_train, y_train)

previsoes = modelo_rf.predict(X_test)

print("\n=== Relatório de Desempenho do Modelo ===")
print(classification_report(y_test, previsoes))


# %%

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

importancia = modelo_rf.feature_importances_
colunas = X.columns

df_importancia = pd.DataFrame({
    'Variavel': colunas,
    'Importancia': importancia
})

df_importancia = df_importancia.sort_values(by='Importancia', ascending=False)

print("Ranking de Importância das Variáveis:")
print(df_importancia)

plt.figure(figsize=(10, 6))

sns.barplot(
    data=df_importancia, 
    x='Importancia', 
    y='Variavel', 
    palette='viridis'
)

plt.title('Importância das Variáveis para Previsão de Falha (Alvo 4H)', fontsize=14, pad=15)
plt.xlabel('Nível de Importância', fontsize=12)
plt.ylabel('Variável', fontsize=12)
plt.grid(axis='x', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()
# %%

# Auditoria no código

df_pre_falha = df_target[df_target['Alvo_4H'] == 1]

top_alarmes_risco = df_pre_falha['Id_Alarme'].value_counts().head(10)

print("Top 10 IDs de Alarme que mais aparecem nas 4 horas antes da quebra:")
print(top_alarmes_risco)



# %%

telem_jan = pd.read_parquet('../data/telemetria/telemetry_jan.parquet')


top_ids = [
    84608753, 84608752, 84626976, 335609934, 335609935, 
    84609421, 84609420, 84609411, 84609410, 84626979
]

df_descricoes = telem_jan[telem_jan['Id_Alarme'].isin(top_ids)][['Id_Alarme', 'Alarme']]

print(df_descricoes)
# %%

df_descricoes.head(10)
# %%

pd.set_option('display.max_colwidth', None)
df_unicos = df_descricoes.drop_duplicates()

df_unicos.head(10)
# %%
previsoes = modelo_rf.predict(X_test)

df_alertas = df_target.loc[X_test.index].copy()
df_alertas['Alerta_Preditivo'] = previsoes

df_risco = df_alertas[df_alertas['Alerta_Preditivo'] == 1].copy()

colunas_relatorio = [
    'TAG', 
    'Data_Evento', 
    'Id_Alarme', 
    'DURACAO_MINUTOS',
    'Id_Criticidade'
]

df_relatorio_final = df_risco[colunas_relatorio]

df_relatorio_final = df_relatorio_final.sort_values(by='Data_Evento', ascending=False)

nome_arquivo = 'Alertas_Preditivos_793D_2S.xlsx'
df_relatorio_final.to_excel(nome_arquivo, index=False)

print(f"Sucesso! Relatório gerado com {df_relatorio_final.shape[0]} alertas preditivos.")
print(f"Arquivo salvo como: {nome_arquivo}")