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
    
def plotdadosano(df):
    for feature in df.columns:
        fig_dx = px.line(df[feature],
                         title = feature)
        st.plotly_chart(fig_dx)

############### Usado no Dashboard pelo professor ###################
#         for gas in emissoes_gas_ano.columns:
#            fig = px.line(emissoes_gas_ano[gas], title=gas)
#            fig.update_layout(yaxis_title='Emissão', showlegend=False)
#            st.plotly_chart(fig)        

# ------------------------------
#           Dados
# ------------------------------

dados = pd.read_csv('emissoes.csv')

# ------------------------------
#           SideBar
# ------------------------------

st.sidebar.title('Filtros')

with st.sidebar.expander('Ano'):
    ano_min = dados['Ano'].min()
    ano_max = dados['Ano'].max()
    todos_anos = st.checkbox("Habilitar Filtro", value = True)
    if todos_anos:
        ano_selecionado = (ano_min, ano_max)
    else:
        ano_selecionado = st.slider("Selecione o Ano para Filtrar",
                        ano_min, ano_max, (ano_min, ano_max))
    ano_selecionado

with st.sidebar.expander('Setor'):
    setores = dados['Setor de emissão'].unique()
    setor_selecionado =  st.multiselect("Seleicone o setor para filtro",
                   setores,
                   default=setores)

with st.sidebar.expander('Gás'):
    gases = dados['Gás'].unique()
    gas_selecionado =  st.multiselect("Seleicone o Gás para filtro",
                   gases,
                   default=gases)

with st.sidebar.expander('Estado ou Regiões'):
    filtro_regiao = st.checkbox('Filtrar por região')

    if filtro_regiao:
        regioes = ['Todas', 'Sudeste', 'Sul']
        regiao_selecionada = st.selectbox("Selecione a Região", regioes)
        
        if regiao_selecionada == 'Todas':
            filtro_estados = dados['Estado'].unique()
        elif regiao_selecionada == 'Sudeste':
            filtro_estados = ['MG', 'SP', 'RJ', 'ES']
        elif regiao_selecionada == 'Sul':
            filtro_estados = ['PR', 'SC', 'RS']       
    else:
        filtro_estados = st.multiselect("Selecione os estados", dados['Estado'].unique(), default= 'MG')

## Filtro de Dados

query = '''
@ano_selecionado[0] <= Ano <= @ano_selecionado[1] and \
`Setor de emissão` in @setor_selecionado and \
`Gás` in @gas_selecionado and \
`Estado` in @filtro_estados
'''
dados = dados.query(query)

# ------------------------------
#           Tabelas
# ------------------------------

## Estados
emissoes_estados = dados.groupby('Estado')[['Emissão']].sum().reset_index()
emissoes_estados = dados.drop_duplicates(subset='Estado')[['Estado', 'lat', 'long']].merge(emissoes_estados, on='Estado').sort_values(by = 'Emissão', ascending=True).reset_index()
emissoes_estados.drop('index', axis = 1, inplace= True)

## Setores
emissoes_setores = dados.groupby('Setor de emissão')[['Emissão']].sum().sort_values(by = 'Emissão', ascending=True).reset_index()

## Emissões estado setor

emissoes_estado_setor = dados.groupby(['Estado', 'Setor de emissão'])[['Emissão']].sum().reset_index()
emissoes_estado_setor = emissoes_estado_setor.loc[emissoes_estado_setor.groupby('Estado')['Emissão'].idxmax()]

## Anos
emissoes_anos = dados.groupby('Ano')[['Emissão']].sum().sort_values(by = 'Ano').reset_index()

## Gases
#
grupo_gas = dados.groupby('Gás')
emissoes_gas = dados.groupby('Gás')[['Emissão']].sum().reset_index()

###-----------------------------------------------------------------------
emissoes_por_gas = grupo_gas[['Emissão']].sum().sort_values(by='Emissão', ascending=False).reset_index()
emissoes_por_gas['Percentual'] = ((emissoes_por_gas['Emissão']/emissoes_por_gas['Emissão'].sum())*100).apply(lambda x: round(x, 2)).astype(float)
### Maior Emissão
maior_emissao = emissoes_por_gas.index[emissoes_por_gas['Emissão'] == emissoes_por_gas['Emissão'].max()]
### Menor Emissão
menor_emissao = emissoes_por_gas.index[emissoes_por_gas['Emissão'] == emissoes_por_gas['Emissão'].min()]
###-----------------------------------------------------------------------

## Percentual
emissoes_gas['Percentual'] = ((emissoes_gas['Emissão'] / emissoes_gas['Emissão'].sum()) * 100).apply(lambda x : f'{x:2f}').astype(float)

## Emissões Gás Ano

emissoes_gas_ano = dados.groupby(['Ano', 'Gás'])[['Emissão']].mean().reset_index()
emissoes_gas_ano = emissoes_gas_ano.pivot_table(index = 'Ano', columns = 'Gás', values = 'Emissão')

emissoes_estados_gas = dados.groupby(['Estado', 'Gás'])[['Emissão']].sum().reset_index()
emissoes_estados_gas = emissoes_estados_gas.loc[emissoes_estados_gas.groupby('Estado')['Emissão'].idxmax()]

# ------------------------------
#           Gráficos
# ------------------------------

## Estados
fig_mapa_emissoes = px.scatter_geo(emissoes_estados,
                                    lat='lat',
                                    lon='long',
                                    scope ='south america',
                                    size='Emissão',
                                    color = 'Estado',
                                    text='Estado',
                                    hover_name='Estado',
                                    hover_data={'lat': False, 'long': False},
                                    title='Total de emissões por estado')

## Setores
fig_emissoes_setores = px.bar(emissoes_setores,
                              x = 'Emissão',
                              y = 'Setor de emissão',
                              color = 'Setor de emissão',
                              title = 'Total de emissões por setores')
fig_emissoes_setores.update_layout(yaxis_title = '', showlegend = False)

## Anos
fig_emissoes_anos = px.line(emissoes_anos,
                             x = 'Ano',
                             y = 'Emissão',
                             title = 'Total de emissões por ano')

fig_percentual_emissoes_gas = px.pie(emissoes_gas, 
                               names='Gás',
                               values='Emissão',
                               title='Percentual de emissões dos gases')

## Gás
fig_emissoes_gas = px.bar(emissoes_gas,
                              x = 'Emissão',
                              y = 'Gás',
                              color = 'Gás',
                              text_auto= True,
                              title = 'Total de emissões por Gás')
fig_emissoes_gas.update_layout(yaxis_title = '', showlegend = False)

## Por estado

fig_emissoes_estado = px.bar(emissoes_estados,
                             x = 'Estado',
                             y = 'Emissão',
                             text_auto= True,
                             color = 'Estado',
                             title= 'Total de emissões por estado')
fig_emissoes_estados_gas = px.sunburst(emissoes_estados_gas,
                                       path=['Estado', 'Gás', 'Emissão'],
                                       height= 750,
                                       width= 750,
                                       values='Emissão',
                                       color= 'Gás',
                                       title= 'Gás mais emitido por estado')

## Por Setor
fig_emissoes_estado_setor = px.sunburst(emissoes_estado_setor,
                                       path=['Estado', 'Setor de emissão', 'Emissão'],
                                       height= 750,
                                       width= 750,
                                       values='Emissão',
                                       color= 'Setor de emissão',
                                       title= 'Setor de emissão mais emitido por estado')
fig_emissoes_estado_setor.update_traces(sort=False, selector=dict(type='sunburst'))
fig_emissoes_estado_setor_bar = px.bar(emissoes_estado_setor,
                                       x='Estado',
                                       y='Emissão',
                                       text_auto= True,
                                       color= 'Setor de emissão',
                                       title= 'Setor de emissão mais emitido por estado')
fig_emissoes_estado_setor_bar.update_layout(xaxis={'categoryorder':'total ascending'})
# ------------------------------
#           Dashboard
# ------------------------------

st.title("Emissões de Gases de Efeito Estufa")

tab_home, tab_gas, tab_estado = st.tabs(['Home', 'Gás', 'Estado'])

with tab_home:
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total de Emissões", formatanumero(dados['Emissão'].sum()) + " Toneladas")
        st.plotly_chart(fig_mapa_emissoes)
        st.plotly_chart(fig_emissoes_anos)
        

    with col2:
        idx_maior_emissao = emissoes_anos.index[emissoes_anos['Emissão'] == emissoes_anos['Emissão'].max()]
        ano_mais_poluente = emissoes_anos.loc[idx_maior_emissao[0]]['Ano'].astype(int)
        emissao_ano_mais_poluente = emissoes_anos.loc[idx_maior_emissao[0]]['Emissão']
        st.metric(f'Emissão ano mais poluente: {ano_mais_poluente}', formatanumero(emissao_ano_mais_poluente) + ' toneladas')
        st.plotly_chart(fig_emissoes_setores)
        st.dataframe(emissoes_estados)

with tab_gas:
    col1, col2 = st.columns(2)
    with col1:
        idx_maior_emissao = emissoes_gas.index[emissoes_gas['Emissão'] == emissoes_gas['Emissão'].max()]
        st.metric('Gás com mais emissões', emissoes_gas.iloc[idx_maior_emissao[0]]['Gás'])
    with col2:
        idx_menor_emissao = emissoes_gas.index[emissoes_gas['Emissão'] == emissoes_gas['Emissão'].min()]
        st.metric('Gás com menos emissões', emissoes_gas.iloc[idx_menor_emissao[0]]['Gás'])
    
    st.plotly_chart(fig_percentual_emissoes_gas)
    st.plotly_chart(fig_emissoes_gas)

    with st.container(height=300):
        st.subheader("Média das emissões dos gases por ano")
        plotdadosano(emissoes_gas_ano)

with tab_estado:
    col1, col2 = st.columns(2)
    with col1:
        idx_maior_emissao = emissoes_estados.index[emissoes_estados['Emissão'] == emissoes_estados['Emissão'].max()]
        st.metric('Estado com mais emissões', emissoes_estados.iloc[idx_maior_emissao[0]]['Estado'])
    with col2:
        idx_menor_emissao = emissoes_estados.index[emissoes_estados['Emissão'] == emissoes_estados['Emissão'].min()]
        st.metric('Estado com menos emissões', emissoes_estados.iloc[idx_menor_emissao[0]]['Estado'])
    
    st.plotly_chart(fig_emissoes_estado)
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_emissoes_estados_gas)
    with col2:
        st.plotly_chart(fig_emissoes_estado_setor)

    st.plotly_chart(fig_emissoes_estado_setor_bar)


