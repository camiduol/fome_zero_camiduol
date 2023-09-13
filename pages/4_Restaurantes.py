# Importando as bibliotecas necessárias
import pandas as pd
import streamlit as st
import inflection
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px


st.set_page_config(page_title='Visão Restaurantes', page_icon='♨',layout='wide')


# =====================================================
# FUNÇÕES
# =====================================================

def rename_columns(df):
    """
    Esta função tem como objetivo renomear as colunas do dataframe, modificando elas para o modo Snake Case, ou seja, com letras minúsculas, separadas por '_'.
    
    Input: dataframe a modificar(df)
    Output: dataframe modificado (dataframe) 
    """
    dataframe=df.copy()
    cols_old=dataframe.columns
    spaces= lambda x: x.replace(" ","")
    snakecase= lambda x: inflection.underscore(x)
    title=lambda x: inflection.titleize(x)
    cols_old=list(map(title,cols_old))
    cols_old=list(map(spaces,cols_old))
    cols_new=list(map(snakecase,cols_old))
    dataframe.columns=cols_new
    return dataframe

def country_name(country_id):
    COUNTRIES={
    1: "India",
    14: "Australia",
    30: "Brazil",
    37: "Canada",
    94: "Indonesia",
    148: "New Zeland",
    162: "Philippines",
    166: "Qatar",
    184: "Singapure",
    189: "South Africa",
    191: "Sri Lanka",
    208: "Turkey",
    214: "United Arab Emirates",
    215: "England",
    216: "United States of America",
    }

    return COUNTRIES[country_id]

def create_price_type (price_range):
	"""
	Esta função tem como objetivo classificar os restaurantes a partir do valor do preço dos pratos.
	
	Input: valor numérico
	Output: string com a classificação
	"""
	if price_range==1:
		return 'cheap'
	elif price_range==2:
		return 'normal'
	elif price_range==3:
		return 'expensive'
	else:
		return 'gourmet'
	
def color_name(color_code):
    COLORS = {
    "3F7E00": "darkgreen",
    "5BA829": "green",
    "9ACD32": "lightgreen",
    "CDD614": "orange",
    "FFBA00": "red",
    "CBCBC8": "darkred",
    "FF7800": "darkred",
    }
    return COLORS[color_code]

def clean_data(df):
	""" 
	Esta função tem como objetivo limpar o dataframe para que ele fique mais fácil de ser manipulado. 
	
	As seguintes etapas são realizadas:
	1. Renomear todas as colunas a partir da função 'rename_columns'
	2. Limpar os valores nulos 
	3. Remover os valores duplicados
	4. Criar uma nova coluna com o nome dos países usando a função 'country_name'
	5. Criar uma categoria de preço usando a função 'create_price_type'
	6. Trocar os códigos das cores pelos nomes delas utilizando a função 'color_name'
	7. Categorizar todos os restaurantes por apenas um tipo de culinária
	8. Ordenar o dataframe pelo número do ID dos restaurantes, para que o primeiro seja sempre o mais antigo (menor ID)
	
	Input: dataframe
	Output: dataframe modificado
	"""
	df=rename_columns(df)
	df=df.dropna()
	df=df.drop_duplicates(ignore_index=True)
	df['country_name']=list(map(country_name,df['country_code']))
	df['price_type']=list(map(create_price_type,df['price_range']))
	df['rating_color']=list(map(color_name,df['rating_color']))
	df['cuisines']=df.loc[:,'cuisines'].apply(lambda x: x.split(',')[0])
	df=df.sort_values('restaurant_id',ascending=1).reset_index(drop=True)
	return df

def make_multiple_charts(df):
	"""
	Esta função tem como objetivo criar uma tabela de gráficos para ajudar a analisar os seguintes dados referentes a restaurantes que fazem ou não entrega:
	1. Se a quantidade média de avaliações por restaurante é maior em restaurantes que fazem entrega
	2. Se a média da nota dos restaurantes que fazem entrega é maior do que dos restaurantes que não fazem entrega
	3. Se os restaurantes que fazem entrega são os que menos fazem reserva ou não
	A função cria subplots, que são subgráficos de barra para representar a relação dos restaurantes que fazem entrega ou não com os parâmetros acima mencionados.
		
	Input: dataframe(df)
	Output: gráficos (graph)
	"""
	graph = make_subplots(rows=1, cols=3)
	
	# Selecionando os dados que serão utilizados para construir o gráfico 1
	# Os restaurantes que aceitam pedido online são também, na média, os restaurantes que mais possuem avaliações registradas?
	cols=['has_online_delivery','votes']
	aux=df.loc[:,cols].groupby('has_online_delivery').mean().reset_index()
	# Modificando os valores das variáveis para tornar mais visual
	aux['has_online_delivery']=['Não','Sim']
	# Adicionando o primeiro gráfico dos restaurantes que fazem reserva
	graph.add_trace(go.Bar(y=aux['votes'],x=aux['has_online_delivery'],name='com a média de avaliações registradas',marker=dict(color=['red','blue'])), row=1, col=1)
	# Customizando o gráfico
	graph.update_xaxes(tickangle=0, row=1, col=1)
	graph.update_yaxes(tickangle=0,title_text='Média de avaliações registradas',title_font={'size':14,'color':'black'},title_standoff=15, row=1, col=1)
	
	
	# Selecionando os dados que serão utilizados para construir o gráfico 2
	cols=['has_online_delivery','aggregate_rating']
	aux1=df.loc[:,cols].groupby('has_online_delivery').mean().reset_index()
	# Modificando os valores das variáveis para tornar mais visual
	aux1['has_online_delivery']=['Não','Sim']
	# Adicionando o segundo gráfico dos restaurantes que fazem entrega online
	graph.add_trace(go.Bar(y=aux1['aggregate_rating'],x=aux1['has_online_delivery'],name='com as notas médias',marker=dict(color=['red','blue'])), row=1, col=2)
	# Customizando o gráfico
	graph.update_xaxes(tickangle=0,title_text="Fazem entrega?",title_font={'size':16,'color':'black'},title_standoff=25, row=1, col=2)
	graph.update_yaxes(tickangle=0,title_text='Média das notas',title_font={'size':14,'color':'black'},title_standoff=5, row=1, col=2)
	
	# Selecionando os dados que serão utilizados para construir o gráfico 3
	cols=['has_online_delivery','has_table_booking','restaurant_name']
	aux2=df.loc[:,cols].groupby(['has_online_delivery','has_table_booking']).count().reset_index()
	# Modificando os valores das variáveis para tornar mais visual
	aux2['has_online_delivery']=['Não','Não','Sim','Sim']
	aux2['has_table_booking']=['Não','Sim','Não','Sim']
	# Filtrando apenas os restaurantes que fazem reserva de mesa
	aux2=aux2.loc[aux2['has_table_booking']=='Sim']
	# Adicionando o terceiro gráfico dos restaurantes que estão fazendo entrega agora
	graph.add_trace(go.Bar(y=aux2['restaurant_name'],x=aux2['has_online_delivery'],name='com o número de restaurantes que fazem reserva de mesa',marker=dict(color=['red','blue'])), row=1, col=3)
	# Customizando o gráfico
	graph.update_yaxes(tickangle=0,title_text='Nº de restaurantes que fazem reserva',title_font={'size':14,'color':'black'},title_standoff=5, row=1, col=3)
	graph.update_xaxes(tickangle=0, row=1, col=3)
	
	graph.update_layout(font_family='sans-serif',
						legend=dict(title=f'<b>Relação dos restaurantes que fazem ou não entrega<b>',title_font={'size':24,'color':'black'},orientation='h',yanchor='bottom',xanchor='center',y=1.1,x=0.5))
	
	return (graph)

# -------------------------------------- Início da Estrutura Lógica do código --------------------------------------


# Carregando o meu arquivo
df_raw=pd.read_csv('dataset/zomato.csv')

# Limpando os dados
df=clean_data(df_raw)


# VISÃO GERAL

# =============================
# BARRA LATERAL
# =============================

#st.sidebar.title('Fome Zero')
#st.sidebar.divider()

# Filtros

countries=df['country_name'].unique()
st.sidebar.subheader('Filtros')
data_selected=st.sidebar.multiselect('Por quais países você deseja navegar?',countries,default=countries)
data_selected=df['country_name'].isin(data_selected)
df=df.loc[data_selected,:]

st.sidebar.markdown('---')
st.sidebar.caption('Developed by Camila Duarte')

# =====================================================
# Layout Streamlit
# =====================================================


st.title('Visão Restaurantes')

with st.container():
	
	fig=make_multiple_charts(df)
	st.plotly_chart(fig)
	
	col1,col2=st.columns(2)
	with col1:
		st.markdown('##### **Top 10 restaurantes mais BEM avaliados**')
		aux=df[['restaurant_id','restaurant_name','aggregate_rating']].sort_values(['aggregate_rating','restaurant_id'],ascending=[0,1]).reset_index(drop=True).head(10)
		aux.columns=['ID do Restaurante','Nome do Restaurante','Nota média']
		st.dataframe(aux.iloc[:,1:])
	
	with col2:
		st.markdown('##### **Top 10 restaurantes mais avaliados (vezes)**')
		aux=df.loc[:,['restaurant_name','votes']].groupby('restaurant_name').sum().reset_index().sort_values('votes',ascending=0).reset_index(drop=True).head(10)
		aux.columns=['Nome do Restaurante','Nº de avaliações']
		st.dataframe(aux)