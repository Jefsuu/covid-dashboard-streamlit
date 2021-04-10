#importando bibliotecas
import streamlit as st
import pandas as pd 
import plotly.express as px
from PIL import Image
import requests


#carregando dados
df = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv',
parse_dates=['date'])
df['date'] = pd.to_datetime(df['date']).dt.date
df.rename(columns={'location':'country'}, inplace=True)
vaccines = pd.read_csv('https://raw.githubusercontent.com/Jefsuu/covid-dashboard-streamlit/main/vaccine_country.csv', usecols=['country', 'vaccines'])

#paginas
paginas = st.selectbox('Selecione o tema desejado',['Vacinação', 'Vacinas'])

#lista de paises
paises = df.country.unique().tolist()

#dashboard
if paginas == 'Vacinação':
    st.title('Dados de vacinação COVID-19')
    st.markdown(
        """
        Dados sobre o progresso de vacinação nos Paises

        Na tabela é mostrado a média do numero de vacinações, o menor numero de vacinação em um dia,
        o maior numero de vacinação em um dia e o total de vacinações até o momento

        """)

    df = df[['country', 'date', 'daily_vaccinations']]
    df.dropna(subset=['daily_vaccinations'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    

    # Multiselect com os paises
    label_to_filter = st.sidebar.multiselect(
        label="Escolha o Pais desejado para visualizar os dados",
        options=paises, default='Brazil'
    )

    if st.sidebar.checkbox('Mostrar tabela'):
        st.subheader('Tabela de dados')
        group = df[df['country'].isin(label_to_filter)]
        group = group.groupby(['country'])['daily_vaccinations'].agg(['mean', 'min', 'max', 'sum'])
        group = pd.DataFrame(group)
        group.reset_index(inplace=True)
        group['mean'] = group['mean'].apply(lambda x: round(x))
        st.write(group)


    #grafico de numero de vacinações no brasil

    line_plot = df[df['country'].isin(label_to_filter)][['country','date', 'daily_vaccinations']].set_index('date')
    fig = px.line(line_plot, labels={'date':'Data', 'value':'Nº de vacinações'}, color='country')
    fig.update_layout(
        title={
            'text': "<b>Vacinações por dia</b>",
            'y':0.95,
            'x':0.45,
            'xanchor': 'center',
            'yanchor': 'top'},
            showlegend=True)

    st.plotly_chart(fig, use_container_width=True)


if paginas == 'Vacinas':

    st.title('Vacinas ultilizadas em cada Pais')
    # Multiselect com os paises
    label_to_filter = st.sidebar.multiselect(
        label="Escolha o Pais desejado para visualizar os dados",
        options=paises, default='Brazil'
    )
    if st.sidebar.checkbox('Mostrar tabela', value=True):
        st.dataframe(vaccines[vaccines['country'].isin(label_to_filter)])

    st.markdown("""
    
    """)


    image = Image.open(requests.get('https://raw.githubusercontent.com/Jefsuu/covid-dashboard-streamlit/main/cloud.png', stream=True).raw)
    st.markdown("<h4 style='text-align: center; color: black;'>Vacinas mais utilizadas</h4>", unsafe_allow_html=True)
    st.image(image)



    



