# Importando as bibliotecas necessárias
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
import inflection

import plotly.express as px


st.set_page_config(page_title='Visão Países', page_icon='🌏',layout='wide')


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

def rating_country(df,parameter):
	"""
	Esta função retorna o país com a maior avaliação ou o país com a menor avaliação média.
	
	Input: dataframe, parameter (maior ou menor)
	Output: str (nome do país)
	"""
	
	cols=['aggregate_rating','country_name']
	aux=df.loc[:,cols].groupby('country_name').mean().round(2).reset_index()

	
	if parameter == 'maior':
		# Ordenar do maior para o menor a partir da nota média e mostrar o primeiro país
		country=aux.sort_values('aggregate_rating',ascending=0).reset_index(drop=True).loc[0,'country_name']
		return (country)
	elif parameter == 'menor':
		country=aux.sort_values('aggregate_rating',ascending=1).reset_index(drop=True).loc[0,'country_name']
		return (country)
	else:
		return ('Parâmetro inválido')

def country_vote(df):
	"""
	Esta função tem como objetivo criar um gráfico de colunas para representar a quantidade média de avaliações registradas por país.
	
	Input: dataframe
	Output: gráfico de colunas
	"""
	cols=['country_name','votes']
	aux1=df.loc[:,cols].groupby('country_name').mean().round(2).reset_index()
	aux1=aux1.sort_values('votes',ascending=0).reset_index(drop=True)
	graph=px.bar(aux1,x='country_name',y='votes',title='Número médio de avaliações por país',color='country_name',labels={'country_name':'Países'})
	graph.update_xaxes(title='Países')
	graph.update_yaxes(title='Número médio de avaliações')
	return (graph)


def country_deliver_booking(df,aux='delivery'or'booking'):
	"""
	
	"""
	if aux=='delivery':
		cols=['restaurant_id','country_name','has_online_delivery']
		aux=df.loc[:,cols].groupby(['has_online_delivery','country_name']).count().reset_index()
		aux=aux.loc[aux['has_online_delivery']==1].sort_values('restaurant_id',ascending=0).reset_index(drop=True)
		graph=px.bar(aux,x='country_name',y='restaurant_id',title='Número de restaurantes que fazem entrega por país',color='country_name',labels={'country_name':'Países','restaurant_id':'Nº de restaurantes'})
		return (graph)
	elif aux=='booking':
		cols=['restaurant_id','country_name','has_table_booking']
		aux=df.loc[:,cols].groupby(['has_table_booking','country_name']).count().reset_index()
		aux=aux.loc[aux['has_table_booking']==1].sort_values('restaurant_id',ascending=0).reset_index(drop=True)
		graph=px.bar(aux,x='country_name',y='restaurant_id',title='Número de restaurantes que fazem reserva de mesa por país',color='country_name',labels={'country_name':'Países','restaurant_id':'Nº de restaurantes'})
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


st.title('Visão Países')

with st.container():
	
	col1,col2=st.columns(2)
	with col1:
		maior=rating_country(df,'maior')
		st.metric('País com a maior nota média',maior)
		
	with col2:
		menor=rating_country(df,'menor')
		st.metric('País com a menor nota média',menor)
			
	# Gráfico de colunas das avaliações médias por país
	fig=country_vote(df)
	st.plotly_chart(fig,use_container_width=True)
	
	# Gráfico de colunas do número de restaurantes por país que fazem entrega
	fig=country_deliver_booking(df,'delivery')
	st.plotly_chart(fig,use_container_width=True)
	
	# Gráfico de colunas do número de restaurantes por país que fazem reserva de mesa
	fig=country_deliver_booking(df,'booking')
	st.plotly_chart(fig,use_container_width=True)
	