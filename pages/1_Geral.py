# Importando as bibliotecas necessárias
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
import inflection


st.set_page_config(page_title='Visão Geral', page_icon='👍',layout='wide')


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

def central_spot(df):
    """ Esta função retorna um mapa da localização central dos pedidos feitos em cada cidade por cada tipo de tráfego.
    A função agrupa o dataframe por cidade e tipo de tráfego e faz a mediana da latitude e da longitude dos restaurantes em cada condição. Esses dados são plotados e é criado um mapa com os pontos.
    Input: dataframe
    Output: mapa
    """
    df_aux1=(df
             .loc[:,['latitude','city','country_name','restaurant_id']]
             .groupby(['country_name','city','restaurant_id'])
             .median()
             .reset_index()) 
    df_aux2=(df
             .loc[:,['longitude','city','country_name','restaurant_id']]
             .groupby(['country_name','city','restaurant_id'])
             .median()
             .reset_index())
    df_aux=pd.merge(df_aux1,df_aux2,how='inner')
    map=folium.Map()
    for i in range(len(df_aux)):
             folium.Marker(
                 [df_aux.loc[i,'latitude'],df_aux.loc[i,'longitude']],
                 popup=df_aux.loc[i,['city','country_name','restaurant_id']]).add_to(map)
    return map
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

# Filtros

countries=df['country_name'].unique()
st.sidebar.subheader('Filtros')
data_selected=st.sidebar.multiselect('Por quais países você deseja navegar?',countries,countries)
st.sidebar.markdown('---')

st.sidebar.caption('Developed by Camila Duarte')

# =====================================================
# Layout Streamlit
# =====================================================


st.title('Visão Geral')

with st.container():
	st.header('Fome Zero')
	st.subheader('Os melhores restaurantes você encontra aqui!')


with st.container():
	st.markdown('Conheça os nossos números:')
	col1,col2,col3,col4,col5=st.columns(5)
	with col1:
		st.metric('Restaurantes',df['restaurant_id'].nunique())
	with col2:
		st.metric('Países',df['country_code'].nunique())
	with col3:
		st.metric('Cidades',df['city'].nunique())
	with col4:
		st.metric('Total de avaliações',df['votes'].nunique())		
	with col5:
		st.metric('Tipos de culinária',df['cuisines'].nunique())
	
	st.markdown('Restaurantes onde o nosso serviço está disponível:')
	#fig=central_spot(df)
	fig=folium.Map()
	folium_static(fig)
	