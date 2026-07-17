#%%
import pandas as pd
import numpy as np

telem_jan = pd.read_parquet('../data/telemetria/telemetry_jan.parquet')
print(telem_jan.columns.tolist())

telem_jan.duplicated().sum()
# %%

def limpeza(df):
    total_linhas = df.shape[0]
    total_colunas = df.shape[1]
    total_duplicadas = df.duplicated().sum()

    print(f"Total de Linhas: {total_linhas}\nTotal de Colunas: {total_colunas}\nLinhas Duplicadas: {total_duplicadas}")

    diagnostico = pd.DataFrame({
        'Tipo': df.dtypes,
        'Valores Não-Nulos': df.notnull().sum(),
        'Valores Nulos': df.isnull().sum(),
        'Nulos (%)': (df.isnull().sum() / total_linhas * 100).round(2),
        'Valores Únicos': df.nunique()
    })

    diagnostico = diagnostico.sort_values(by='Valores Nulos', ascending=False)
    diagnostico['Nulos (%)'] = diagnostico['Nulos (%)'].astype(str) + '%'
    
    return diagnostico

teste = limpeza(telem_jan)
# %%

apontamentos = pd.read_parquet('../data/apontamentos/desenvolver_apontamentos.parquet')
apontamentos.columns = apontamentos.columns.str.strip().str.upper()
apontamentos.columns

# %%

apontamentos['DURACAO_MINUTOS'] = (apontamentos['FIM'] - apontamentos['INICIO']).dt.total_seconds() / 60
apontamentos['DURACAO_MINUTOS'] = apontamentos['DURACAO_MINUTOS'].round(2)
apontamentos.head()
# %%

tp_invalido = apontamentos['DURACAO_MINUTOS'] <= 0
tp_invalido.describe()
# %%

apontamentos.sort_values(by=['TAG', 'INICIO'], ignore_index=True, inplace=True)

# %%

apontamentos['FIM_ANTERIOR'] = apontamentos.groupby('TAG')['FIM'].shift(1)
filtro_sobreposicao = apontamentos['INICIO'] < apontamentos['FIM_ANTERIOR']
erros_sobreposicao = apontamentos[filtro_sobreposicao]

len(erros_sobreposicao)
apontamentos = apontamentos[~filtro_sobreposicao].copy()
apontamentos.drop(columns=['FIM_ANTERIOR'], inplace=True)



# %%
apontamentos.head()

# %%
telem_jan.columns.to_list()

col_uteis = [
    'TAG',
    'Data_Evento',
    'Nome_Operador_Anon', 
    'Is_Dont_Go', 
    'Id_Criticidade', 
    'Id_Alarme'
]

arquivos = [
    '../data/telemetria/telemetry_jan.parquet',
    '../data/telemetria/telemetry_feb.parquet',
    '../data/telemetria/telemetry_mar.parquet',
    '../data/telemetria/telemetry_abr.parquet',
    '../data/telemetria/telemetry_may.parquet',
    '../data/telemetria/telemetry_jun.parquet'
]

lista_dfs = [pd.read_parquet(arq, columns=col_uteis) for arq in arquivos]
telemetria = pd.concat(lista_dfs, ignore_index=True)

print(f"Total de registros carregados: {len(telemetria)}")
telemetria.head()


# %%

telemetria.isnull().sum()

# %%
(telemetria['Is_Dont_Go'].value_counts(normalize=True) * 100).round(2)

# %%
telemetria['Is_Dont_Go'].value_counts()
telemetria.head()

# %% [markdown]

#**Após checagem dos dados será feito um merge para avançar no EDA**

# %%

telemetria.sort_values(by='Data_Evento', inplace=True)
apontamentos.sort_values(by='INICIO', inplace=True)

#Padronização do tempo para nanossegundos para chaves de cruzamento
telemetria['Data_Evento'] = telemetria['Data_Evento'].astype('datetime64[ns]')
apontamentos['INICIO'] = apontamentos['INICIO'].astype('datetime64[ns]')
apontamentos['FIM'] = apontamentos['FIM'].astype('datetime64[ns]')

df_unificado = pd.merge_asof(
    left=telemetria,
    right=apontamentos,
    by='TAG',
    left_on='Data_Evento',
    right_on='INICIO',
    direction='backward'
)

# Se o FIM for nulo (NaT), consideramos como erro de cruzamento.
filtro_dentro_do_ciclo = (df_unificado['Data_Evento'] <= df_unificado['FIM']) & (df_unificado['FIM'].notna())
df_analise_final = df_unificado[filtro_dentro_do_ciclo].copy()

df_eventos_orfaos = df_unificado[~filtro_dentro_do_ciclo]

print(f"Total de registros unificados (Dentro de um ciclo): {len(df_analise_final)}")
print(f"Total de eventos órfãos (Fora de ciclo): {len(df_eventos_orfaos)}")
# %% [markdown]

# Criando algumas visualizações antes do modelo preditivo

# %%

import matplotlib.pyplot as plt
import seaborn as sns

analise_tipo = df_analise_final.groupby('TIPO').agg(
    Total_Registros=('Is_Dont_Go', 'count'),
    Total_Alertas=('Is_Dont_Go', 'sum')
).reset_index()

analise_tipo['Taxa_Falha_Percentual'] = (analise_tipo['Total_Alertas'] / analise_tipo['Total_Registros']) * 100

analise_tipo = analise_tipo.sort_values(by='Taxa_Falha_Percentual', ascending=False)

print(analise_tipo)

plt.figure(figsize=(10, 6))
sns.barplot(
    data=analise_tipo, 
    x='Taxa_Falha_Percentual', 
    y='TIPO',
    palette='Reds_r'
)

plt.title('Taxa de Alertas "Don\'t Go" por Tipo de Equipamento', fontsize=14, pad=15)
plt.xlabel('Taxa de Falha (%)', fontsize=12)
plt.ylabel('Tipo de Equipamento', fontsize=12)
plt.grid(axis='x', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()

# %%
df_analise_final['TIPO'].value_counts()
