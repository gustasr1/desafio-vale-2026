#%%
import pandas as pd
import numpy as np

telem_jan = pd.read_parquet('../data/telemetria/telemetry_jan.parquet')
print(telem_jan.columns.tolist())
# %%

telem_jan.columns = telem_jan.columns.str.upper()
telem_jan.columns = telem_jan.columns.str.strip()
# %%

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
