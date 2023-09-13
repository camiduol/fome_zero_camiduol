# Importando as bibliotecas necessárias
import pandas as pd
import streamlit as st
import inflection
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px


st.set_page_config(page_title='Visão Tipos Culinários', page_icon='🛎',layout='wide')


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

#Filtro de tipo de culinária

st.sidebar.markdown('---')
st.sidebar.caption('Developed by Camila Duarte')

# =====================================================
# Layout Streamlit
# =====================================================


st.title('Visão Tipos Culinários')


def best_worse_restaurant(df,cuisine,parameter):
	"""
	Esta função tem como objetivo retornar o nome do restaurante que possui a maior nota média ou a pior nota média de acordo com o tipo de culinária desejado.
	
	Input: 
		df = dataframe
		cuisine = tipo de culinária ('Italian','Japanese', 'American', 'Brazilian',etc)
		parameter = 'maior' ou 'menor' de acordo com a maior nota ou menor nota
	Output: str (nome do restaurante)
	"""
	aux=df.loc[df['cuisines']==cuisine]
	if parameter == 'maior':
		aux=aux.sort_values('aggregate_rating',ascending=0).reset_index(drop=True)
		restaurant=aux.loc[0,'restaurant_name']
		return(restaurant)
	elif parameter == 'menor':
		aux=aux.sort_values('aggregate_rating',ascending=1).reset_index(drop=True)
		restaurant=aux.loc[0,'restaurant_name']
		return(restaurant)

	
	
	
with st.container():
	col1,col2=st.columns(2)
	with col1:
		st.markdown('### **Melhores restaurantes**')
		st.metric('Melhor Italiano:',best_worse_restaurant(df,'Italian','maior'))
		st.metric('Melhor Americano:',best_worse_restaurant(df,'American','maior'))
		st.metric('Melhor Árabe:',best_worse_restaurant(df,'Arabian','maior'))
		st.metric('Melhor Japonês:',best_worse_restaurant(df,'Japanese','maior'))
		st.metric('Melhor Caseiro:',best_worse_restaurant(df,'Home-made','maior'))	
	with col2:
		st.markdown('### **Piores restaurantes**')
		st.metric('Pior Italiano:',best_worse_restaurant(df,'Italian','menor'))
		st.metric('Pior Americano:',best_worse_restaurant(df,'American','menor'))
		st.metric('Pior Árabe:',best_worse_restaurant(df,'Arabian','menor'))
		st.metric('Pior Japonês:',best_worse_restaurant(df,'Japanese','menor'))
		st.metric('Pior Caseiro:',best_worse_restaurant(df,'Home-made','menor'))	
	st.divider()
	st.markdown('## **Outras métricas**')
	col1,col2=st.columns(2)
	with col1:
		aux=df.sort_values(['aggregate_rating','restaurant_id'],ascending=[0,1]).reset_index(drop=True)
		st.metric('Tipo de culinária mais bem avaliado:',aux.loc[0,'cuisines'])

	with col2:
		aux=df.loc[(df['is_delivering_now']==1)&(df['has_online_delivery']==1)]
		aux=aux.loc[:,['cuisines','has_online_delivery']].groupby('cuisines').count().reset_index()
		aux=aux.sort_values('has_online_delivery',ascending=0).reset_index(drop=True).loc[0,'cuisines']
		st.metric('Tipo de culinária que mais aceita pedido online e está fazendo entregas:',aux)