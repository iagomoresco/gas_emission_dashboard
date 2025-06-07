import streamlit as st
import pandas as pd
import plotly.express as px

# Page Config
st.set_page_config(layout='wide')

# ------------------------------
#           Funções
# ------------------------------
def formatanumero(valor):
    if valor >= 1_000_000_000:
        return f'{valor / 1000000000:.2f} Bilhões de'
    if valor >= 1_000_000:
        return f'{valor / 1000000:.2f} Milhões de'
    if valor >= 1_000:
        return f'{valor / 1000:.2f} Mil'

@st.cache_data
def converte_csv(df):
    return df.to_csv(index = False).encode('utf-8')

# ------------------------------
#           Dados
# ------------------------------

dados = pd.read_csv('emissoes.csv')

# # ------------------------------
# #           SideBar
# # ------------------------------

# st.sidebar.title('Filtros')

# with st.sidebar.expander('Ano'):
#     ano_min = dados['Ano'].min()
#     ano_max = dados['Ano'].max()
#     todos_anos = st.checkbox("Habilitar Filtro", value = True)
#     if todos_anos:
#         ano_selecionado = (ano_min, ano_max)
#     else:
#         ano_selecionado = st.slider("Selecione o Ano para Filtrar",
#                         ano_min, ano_max, (ano_min, ano_max))
#     ano_selecionado

# with st.sidebar.expander('Setor'):
#     setores = dados['Setor de emissão'].unique()
#     setor_selecionado =  st.multiselect("Seleicone o setor para filtro",
#                    setores,
#                    default=setores)

# with st.sidebar.expander('Gás'):
#     gases = dados['Gás'].unique()
#     gas_selecionado =  st.multiselect("Seleicone o Gás para filtro",
#                    gases,
#                    default=gases)

# with st.sidebar.expander('Estado ou Regiões'):
#     filtro_regiao = st.checkbox('Filtrar por região')

#     if filtro_regiao:
#         regioes = ['Todas', 'Sudeste', 'Sul']
#         regiao_selecionada = st.selectbox("Selecione a Região", regioes)
        
#         if regiao_selecionada == 'Todas':
#             filtro_estados = dados['Estado'].unique()
#         elif regiao_selecionada == 'Sudeste':
#             filtro_estados = ['MG', 'SP', 'RJ', 'ES']
#         elif regiao_selecionada == 'Sul':
#             filtro_estados = ['PR', 'SC', 'RS']       
#     else:
#         filtro_estados = st.multiselect("Selecione os estados", dados['Estado'].unique(), default= 'MG')

# ## Filtro de Dados

# query = '''
# @ano_selecionado[0] <= Ano <= @ano_selecionado[1] and \
# `Setor de emissão` in @setor_selecionado and \
# `Gás` in @gas_selecionado and \
# `Estado` in @filtro_estados
# '''
# #dados = dados.query(query)

# ------------------------------
#           Dashboard
# ------------------------------

st.title("Dados")

with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas', list(dados.columns), default=list(dados.columns))

dados = dados[colunas]

st.dataframe(dados)
st.markdown(f':gray[{dados.shape[0]} linhas x {dados.shape[1]} colunas]')

st.download_button(
    label= "Download CSV",
    data = converte_csv(dados),
    file_name= "data.csv",
    mime= "text/csv",
    icon= ":material/download:")