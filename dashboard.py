#importando bibliotecas
import streamlit as st
import pandas as pd 
import plotly.express as px
from PIL import Image
import requests


#carregando dados
#dados de vacinção
df = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv',
parse_dates=['date'])
df['date'] = pd.to_datetime(df['date']).dt.date
df.rename(columns={'location':'country'}, inplace=True)
#dados das vacinas
vaccines = pd.read_csv('https://raw.githubusercontent.com/Jefsuu/covid-dashboard-streamlit/main/vaccine_country.csv', usecols=['country', 'vaccines'])

#dados de testagem
test = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/testing/covid-testing-all-observations.csv',
usecols=['Entity', 'Daily change in cumulative total', 'Date'], parse_dates=['Date'])
test['Date'] = pd.to_datetime(test['Date']).dt.date



#Configurações da pagina
st.set_page_config(
    layout="centered",
    initial_sidebar_state="expanded",
    page_title="Dashboard Covid-19",
    )

#paginas
st.sidebar.title('Navegação')
paginas = st.sidebar.radio('Paginas', ['Vacinação', 'Vacinas', 'Testagem'])



#lista de países
paises = df.country.unique().tolist()

#dashboard
if paginas == 'Vacinação':
    st.title('Dados de vacinação COVID-19')
    st.markdown(
        """
        Dados sobre o progresso de vacinação nos Países

        Na tabela é mostrado a média do numero de vacinações, o menor numero de vacinação em um dia,
        o maior numero de vacinação em um dia e o total de vacinações até o momento

        """)

    df = df[['country', 'date', 'daily_vaccinations']]
    df.dropna(subset=['daily_vaccinations'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    

    # Multiselect com os países
    label_to_filter = st.multiselect(
        label="Escolha o País desejado para visualizar os dados",
        options=paises, default='Brazil')

    if st.checkbox('Mostrar tabela'):
        st.subheader('Tabela de dados')
        group = df[df['country'].isin(label_to_filter)]
        group = group.groupby(['country'])['daily_vaccinations'].agg(['mean', 'min', 'max', 'sum'])
        group = pd.DataFrame(group)
        group.reset_index(inplace=True)
        group['mean'] = group['mean'].apply(lambda x: round(x))
        st.write(group)


    #grafico de numero de vacinações nos países

    vacc_line_plot = df[df['country'].isin(label_to_filter)][['country','date', 'daily_vaccinations']].set_index('date')
    fig = px.line(vacc_line_plot, labels={'date':'Data', 'value':'Nº de vacinações'}, color='country')
    fig.update_layout(
        title={
            'text': "<b>Vacinações por dia</b>",
            'y':0.95,
            'x':0.45,
            'xanchor': 'center',
            'yanchor': 'top'},
            showlegend=True)

    st.plotly_chart(fig, use_container_width=True)

    #grafico de barras
    vacc_bar_plot = df.groupby(by=['country'])['daily_vaccinations'].sum()
    vacc_bar_plot.sort_values(ascending=False, inplace=True)
    fig = px.bar(vacc_bar_plot, range_x=[-0.6,25.5], labels={'country':'País', 'value':'Nº de vacinações'})
    fig.update_layout(barmode='group', xaxis_tickangle=-45)
    fig.update_layout(
        title={
            'text': "<b>Numero total de vacinações por País</b>",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
            showlegend=False)

    st.plotly_chart(fig, use_container_width=True)

    #link da fonte dos dados
    st.markdown("[Fonte dos dados](https://github.com/owid/covid-19-data/tree/master/public/data/vaccinations)")


if paginas == 'Vacinas':

    
    st.title('Vacinas ultilizadas em cada País')
    st.markdown("""
    Na tabela abaixo, pode ser visualizada as vacinas que estão sendo utilizadas por cada país.
    E na nuvem de palavras é possivel ver quais são as vacinas que mais estão sendo utilizadas no mundo.""")
    # Multiselect com os países
    label_to_filter = st.multiselect(
        label="Escolha o País desejado para visualizar os dados",
        options=paises, default='Brazil'
    )
    if st.checkbox('Mostrar tabela', value=True):
        st.dataframe(vaccines[vaccines['country'].isin(label_to_filter)])

    st.markdown("""
    
    """)


    image = Image.open(requests.get('https://raw.githubusercontent.com/Jefsuu/covid-dashboard-streamlit/main/cloud.png', stream=True).raw)
    st.markdown("<h4 style='text-align: center; color: black;'>Vacinas mais utilizadas</h4>", unsafe_allow_html=True)
    st.image(image)


#Testagem
if paginas == 'Testagem':

    st.title('Testagem de Covid-19 nos Países')
    st.markdown(
        """
        Dados sobre a testagem de Covid-19 nos Países

        Na tabela é mostrado a média do numero de testagens, o menor numero de testagem em um dia,
        o maior numero de testagem em um dia e o total de testagens até o momento.

        Para alguns países, não há dados desses numeros na base de dados.

        """)

    label_to_filter = st.multiselect(
        label="Escolha o País desejado para visualizar os dados",
        options=paises, default='Brazil')

    test['country'] = test['Entity'].apply(lambda x: str(x))
    test['country'] = test.country.astype('string')
    test['country'] = test.country.str.split('-').str[0]
    test.drop(columns=['Entity'], inplace=True)
    test = test[['country','Date', 'Daily change in cumulative total']]
    test.rename(columns={'Daily change in cumulative total':'daily_test', 'Date':'date'}, inplace=True)
    test.country = test.country.str.strip()
    
    #tabela dados vacinação
    if st.checkbox('Mostrar tabela'):
        st.subheader('Tabela de dados')

        group = test[test['country'].isin(label_to_filter)]
        group = group.groupby(['country'])['daily_test'].agg(['mean', 'min', 'max', 'sum'])
        group = pd.DataFrame(group)
        group.reset_index(inplace=True)
        group.fillna(0, inplace=True)
        group['mean'] = group['mean'].apply(lambda x: round(x))
        st.write(group)

    #grafico de linha
    test_bar_plot = test.groupby('country').sum()
    test_bar_plot.sort_values('daily_test', ascending=False, inplace=True)
    fig = px.bar(test_bar_plot, range_x=[-0.6,25.5], labels={'country':'País', 'value':'Nº de testes'})
    
    fig.update_layout(barmode='group', xaxis_tickangle=-45)
    fig.update_layout(
        title={
            'text': "<b>Numero total de testagens por País</b>",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
            showlegend=False)
    st.plotly_chart(fig)

        #link da fonte dos dados
    st.markdown("[Fonte dos dados](https://github.com/owid/covid-19-data/tree/master/public/data/testing)")

#progresso
st.sidebar.title('Desenvolvimento')
st.sidebar.info("""
    Dados que serão adicionados:
    * Testagem de Covid-19
    * Covid no Brasil""")

#informações de contato
st.sidebar.title('Sobre')
st.sidebar.info("""
    Dashboard criado por Jeferson Ribeiro
    
    [Github](https://github.com/Jefsuu)
    [Kaggle](https://www.kaggle.com/jefsuu)""")





