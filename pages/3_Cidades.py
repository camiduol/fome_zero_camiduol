# Importando as bibliotecas necessárias
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
import inflection
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px


st.set_page_config(page_title='Visão Cidades', page_icon='🏙',layout='wide')


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

def rating_city(df,parameter):
	"""
	Esta função retorna as cidades com mais restaurantes com nota acima de 4 e mais restaurantes com nota abaixo de 2,5.
	A quantidade de cidades mostradas nas tabelas depende do filtro acionado pelo usuário.
	
	Input: dataframe, parameter (melhor ou pior)
	Output: dataframe (cidades e quantidade de restaurantes com nota acima de 4 ou nota abaixo de 2,5)
	"""
	
	cols=['aggregate_rating','city']
	aux=df.loc[:,cols].groupby('city').mean().round(2).reset_index()

	
	if parameter == 'melhor':
		cols=['city','restaurant_id']
		city_high_rating=df.loc[df['aggregate_rating']>4.0,cols].groupby(['city']).count().reset_index()
		city_high_rating=city_high_rating.sort_values('restaurant_id',ascending=0).reset_index(drop=True).head(top_number)
		city_high_rating.columns=['Cidades','Quantidade de Restaurantes']
		return(city_high_rating)
	elif parameter == 'pior':
		cols=['city','restaurant_id']
		city_low_rating=df.loc[df['aggregate_rating']<2.5,cols].groupby(['city']).count().reset_index()
		city_low_rating=city_low_rating.sort_values('restaurant_id',ascending=0).reset_index(drop=True).head(top_number)
		city_low_rating.columns=['Cidades','Quantidade de Restaurantes']
		return(city_low_rating)
	else:
		return ('Parâmetro inválido')

def city_cuisine (df):
	"""
	Esta função tem como objetivo retornar um gráfico de colunas para representar a quantidade de tipos de culinária distintos por cidade.
	Os dados são mostrados em ordem decrescente do número de tipos de culinária.

	Input: dataframe (df)
	Output: gráfico de colunas onde o eixo x é o nome da cidade e o eixo y a quantidade de tipos de culinária distintos
	"""
	cols=['country_name','cuisines','city']
	city_cuisine=(df.loc[:,cols]
					.groupby(['city','country_name'])
					.count()
					.reset_index()
					.sort_values('cuisines',ascending=0)
					.reset_index(drop=True)
					.head(top_number))
	graph=px.bar(
				city_cuisine,
				x='city',
				y='cuisines',
				color='country_name',
				width=800,height=600,
				template='simple_white',
				title='<b>Cidades com maior quantidade de tipos de culinária distintos<b>',
				labels={'cuisines':'Tipos de culinária distintos','country_name':'País','city':'Cidade'})
	
	# Customizando o gráfico
	graph.update_layout(font_family='sans-serif',
						title=dict(font=dict(size=22,color='black'),x=0.5),
						legend=dict(title='<b>Países<b>',title_font={'size':20,'color':'black'},orientation='h',yanchor='bottom',xanchor='center',y=-0.7,x=0.5))
	return (graph)	

def make_multiple_charts(df):
	"""
	Esta função tem como objetivo criar uma tabela de gráficos, levando em consideração as três categorias 'has_table_booking','has_online_delivering','is_delivering_now'.
	A função cria subplots, que são subgráficos de coluna para representar a quantidade de restaurantes que atendem à categoria por cidade.
	A quantidade de cidades é mostrada de acordo com o número de cidades escolhido pelo usuário ('top_number')
	
	Input: dataframe(df)
	Output: gráficos (graph)
	"""
	graph = make_subplots(rows=1, cols=3)
	
	# Selecionando os dados que serão utilizados para construir o gráfico 1
	cols=['city','has_table_booking','restaurant_id','country_name']
	aux=df.loc[:,cols].groupby(['has_table_booking','city']).count().reset_index()
	aux = aux.loc[aux['has_table_booking']==1].sort_values('restaurant_id',ascending=0).reset_index(drop=True).head(top_number)
	# Adicionando o primeiro gráfico dos restaurantes que fazem reserva
	graph.add_trace(go.Bar(x=aux['city'],y=aux['restaurant_id'],name='que fazem reserva'), row=1, col=1)
	# Customizando o gráfico
	graph.update_xaxes(tickangle=45,title_text='Cidade',title_font={'size':14,'color':'black'},title_standoff=25, row=1, col=1)
	graph.update_yaxes(tickangle=0,title_text="Nº de Restaurantes",title_font={'size':16,'color':'black'},title_standoff=25, row=1, col=1)
	
	# Selecionando os dados que serão utilizados para construir o gráfico 2
	cols=['city','has_online_delivery','restaurant_id']
	aux1=df.loc[:,cols].groupby(['has_online_delivery','city']).count().reset_index()
	aux1 = aux1.loc[aux1['has_online_delivery']==1].sort_values('restaurant_id',ascending=0).reset_index(drop=True).head(top_number)
	# Adicionando o segundo gráfico dos restaurantes que fazem entrega online
	graph.add_trace(go.Bar(x=aux1['city'],y=aux1['restaurant_id'],name='que fazem entrega online',marker_color='green'), row=1, col=2)
	# Customizando o gráfico
	graph.update_xaxes(tickangle=45,title_text='Cidade',title_font={'size':14,'color':'black'},title_standoff=25, row=1, col=2)
	graph.update_yaxes(tickangle=0, row=1, col=2)
	
	# Selecionando os dados que serão utilizados para construir o gráfico 3
	cols=['city','is_delivering_now','restaurant_id']
	aux2=df.loc[:,cols].groupby(['is_delivering_now','city']).count().reset_index()
	aux2 = aux2.loc[aux2['is_delivering_now']==1].sort_values('restaurant_id',ascending=0).reset_index(drop=True).head(top_number)
	# Adicionando o terceiro gráfico dos restaurantes que estão fazendo entrega agora
	graph.add_trace(go.Bar(x=aux2['city'],y=aux2['restaurant_id'],name='que estão fazendo entrega agora'), row=1, col=3)
	# Customizando o gráfico
	graph.update_xaxes(tickangle=45,title_text='Cidade',title_font={'size':14,'color':'black'},title_standoff=25, row=1, col=3)
	graph.update_yaxes(tickangle=0, row=1, col=3)
	
	graph.update_layout(font_family='sans-serif',
						legend=dict(title=f'<b>Top {top_number} cidades com mais restaurantes<b>',title_font={'size':30,'color':'black'},orientation='h',yanchor='bottom',xanchor='center',y=1.1,x=0.5))
	
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

top_number=st.sidebar.slider('Quantas cidades você quer ver no ranking?',min_value=1,max_value=100,value=10)

st.sidebar.markdown('---')
st.sidebar.caption('Developed by Camila Duarte')

# =====================================================
# Layout Streamlit
# =====================================================


st.title('Visão Cidades')

with st.container():
	city=df.loc[:,['city','restaurant_id']].groupby('city').count().reset_index().sort_values('restaurant_id',ascending=0).loc[0,'city']
	st.metric('Cidade com mais restaurantes registrados:',city)
	
	st.header(f'TOP {top_number}:')	
	col1,col2=st.columns(2)
	with col1:

		st.markdown('Cidades com a maior quantidade de restaurantes com nota média maior que 4:')
		melhor=rating_city(df,'melhor')
		st.dataframe(melhor)
		
	with col2:
		st.markdown('Cidades com a maior quantidade de restaurantes com nota média menor que 2.5:')
		pior=rating_city(df,'pior')
		st.dataframe(pior)
	
	st.divider()		
	fig=city_cuisine(df)
	st.plotly_chart(fig,theme=None)
	
	st.divider()	
	fig=make_multiple_charts(df)
	st.plotly_chart(fig)