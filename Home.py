import streamlit as st

st.set_page_config(
    page_title='Home',
    page_icon="🔥"
)

st.sidebar.markdown('# Projeto Fome Zero')
st.sidebar.caption('Developed by Camila Duarte')

st.write("# Fome Zero Dashboard")

st.markdown(
	"""
	Este dashboard foi construído com o objetivo de ter uma visão melhor sobre as métricas do negócio.
	### Como utilizar esse Dashboard?
	- Visão Geral:
		- Métricas gerais do negócio. Geolocalização dos restaurantes e principais números.
	- Visão Países:
		- Métricas relacionadas aos países, como: quantidade de avaliações por país, quantidade de restaurantes que fazem entrega por país, etc.
	- Visão Cidades:
		- Visão das cidades com maiores notas e piores notas, mais diversas e das que possuem mais restaurantes com reserva e entrega. Filtrada por países e por número do ranking (top 1 a top 100).
	- Visão Restaurantes:
		- Insights sobre restaurantes que realizam entrega e o número de avaliação, média das notas e que fazem entrega. Top 10 dos restaurantes mais avaliados.
	- Visão Tipos Culinários:
		- Indicadores dos melhores e piores restaurantes para alguns tipos de culinária.
	### Ask for help
	- linkedin/camiladuol
	""")
	
	
	