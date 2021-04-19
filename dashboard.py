#importando bibliotecas
import streamlit as st
import pandas as pd 
import plotly.express as px
from PIL import Image
import requests



#total world dados
total_world = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv',
 usecols=['location', 'date','new_cases','new_deaths', 'new_vaccinations', 'new_tests'], parse_dates=['date'])
total_world['date'] = pd.to_datetime(total_world['date'])
total_world.rename(columns={'location':'country','new_cases':'cases', 'new_deaths':'deaths',
'new_vaccinations':'vaccinations', 'new_tests':'tests'}, inplace=True)

#dados vacinas
vaccines = pd.read_csv('https://raw.githubusercontent.com/Jefsuu/covid-dashboard-streamlit/main/vaccine_country.csv',
 usecols=['country', 'vaccines'])



#função para lineplot com média móvel
def group_plot(dataframe,index, paises, data):
    df = dataframe[dataframe[index].isin(paises)].reset_index(drop=True)
    df_group = df.set_index(index)
    df_group = df_group.groupby(index).rolling(7, min_periods=1).mean()
    df_plot = df_group.reset_index().join(df[data])
    return df_plot

#função de tabela com estatisticas
def group_tab(dataframe, valor, paises, index):
    df = dataframe[dataframe[index].isin(paises)]
    df_group = df.groupby(index)[valor].agg(['mean', 'min', 'max', 'sum'])
    df_group.reset_index(inplace=True)
    df_group['mean'] = df_group['mean'].apply(lambda x: round(x))
    return df_group


#Configurações da pagina
st.set_page_config(
    layout="centered",
    initial_sidebar_state="expanded",
    page_title="Dashboard Covid-19",
    )

#paginas
st.sidebar.title('Navegação')
paginas = st.sidebar.radio('Paginas', ['Vacinação','Casos','Mortes', 'Vacinas', 'Testagem', 'Brasil'])



#lista de países
paises = total_world.country.unique().tolist()

#dashboard
if paginas == 'Vacinação':
    st.title('Dados de vacinação COVID-19')
    st.markdown(
        """
        Dados sobre o progresso de vacinação nos Países

        Na tabela é mostrado a média do número de vacinações, o menor número de vacinação em um dia,
        o maior número de vacinação em um dia e o total de vacinações até o momento

        """)

    vaccination = total_world[['country', 'date', 'vaccinations']]
    vaccination.dropna(subset=['vaccinations'], inplace=True)
    vaccination.reset_index(drop=True, inplace=True)

    

    # Multiselect com os países
    label_to_filter = st.multiselect(
        label="Escolha o País desejado para visualizar os dados",
        options=paises, default='Brazil')

    if st.checkbox('Mostrar tabela'):
        st.subheader('Tabela de dados')
        st.write(group_tab(vaccination, 'vaccinations', label_to_filter, 'country'))


    #grafico de número de vacinações nos países
    st.text('Foi utilizado média móvel no gráfico para melhor visualização da tendência.')
    #vacc_line_plot = df[df['country'].isin(label_to_filter)][['country','date', 'daily_vaccinations']].set_index('date')
    fig = px.line(group_plot(vaccination, 'country', label_to_filter, 'date'),x='date', y='vaccinations',
     labels={'date':'Data', 'value':'Nº de vacinações'}, color='country')
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
    vacc_bar_plot = vaccination.groupby(by=['country'])['vaccinations'].sum()
    vacc_bar_plot.sort_values(ascending=False, inplace=True)
    fig = px.bar(vacc_bar_plot, range_x=[-0.6,25.5], labels={'country':'País', 'value':'Nº de vacinações'})
    fig.update_layout(barmode='group', xaxis_tickangle=-45)
    fig.update_layout(
        title={
            'text': "<b>Número total de vacinações por País</b>",
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

if paginas == 'Casos':

    st.title('Dados sobre casos de Covid-19')
    st.markdown(
    """
    Dados sobre o número de casos nos Países

    Na tabela é mostrado a média do número de casos, o menor número de casos em um dia,
    o maior número de casos em um dia e o total de casos até o momento.

    """)
    #dados casos
    cases = total_world[['country','date', 'cases']]

    label_to_filter = st.multiselect(
        label="Escolha o País desejado para visualizar os dados",
        options=paises, default='Brazil')


    if st.checkbox('Mostrar tabela'):
        st.subheader('Tabela de dados')
        st.write(group_tab(cases, 'cases', label_to_filter, 'country'))


    st.text('Foi utilizado média móvel no gráfico para melhor visualização da tendência.')

    fig = px.line(data_frame=group_plot(cases, 'country', label_to_filter, 'date'), x='date', y='cases',
     color='country', labels={'cases':'Nº de casos','date':'Data'})
    fig.update_layout(
    title={
        'text': "<b>Número de casos por País</b>",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
        showlegend=True)

    st.plotly_chart(fig, use_container_width=True)

    case_bar_plot = total_world.groupby('country').agg({'cases':'sum'})
    case_bar_plot.sort_values('cases', inplace=True, ascending=False)

    fig = px.bar(case_bar_plot, range_x=[-0.6,25.5], labels={'country':'Pais', 'value':'Nº de casos'})
    fig.update_layout(barmode='group', xaxis_tickangle=-45)
    fig.update_layout(
        title={
            'text': "<b>Número total de casos por País</b>",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
            showlegend=False)

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("[Fonte dos dados](https://github.com/owid/covid-19-data/blob/master/public/data/owid-covid-data.csv)")

if paginas == 'Mortes':

    st.title('Dados sobre mortes de Covid-19')
    st.markdown(
    """
    Dados sobre o número de mortes nos Países

    Na tabela é mostrado a média do número de mortes, o menor número de mortes em um dia,
    o maior número de mortes em um dia e o total de mortes até o momento.

    """)
    #dados mortes
    deaths = total_world[['country', 'date', 'deaths']]

    # Multiselect com os países
    label_to_filter = st.multiselect(
        label="Escolha o País desejado para visualizar os dados",
        options=paises, default='Brazil')

    if st.checkbox('Mostrar tabela'):
        st.subheader('Tabela de dados')
        st.write(group_tab(deaths, 'deaths', label_to_filter, 'country'))

    
    st.text('Foi utilizado média móvel no gráfico para melhor visualização da tendência.')
    fig = px.line(data_frame=group_plot(deaths, 'country', label_to_filter, 'date' ), x='date', y='deaths',
    color='country', labels={'date':'Data', 'deaths':'Nº de mortes'})
    fig.update_layout(
    title={
        'text': "<b>Número de mortes por País</b>",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
        showlegend=True)
    st.plotly_chart(fig)

    #grafico de barra
    death_bar_plot = deaths.groupby('country').sum()
    death_bar_plot.sort_values('deaths', ascending=False, inplace=True)
    fig = px.bar(death_bar_plot, range_x=[-0.6,25.5], labels={'country':'País', 'value':'Nº de mortes'})
    
    fig.update_layout(barmode='group', xaxis_tickangle=-45)
    fig.update_layout(
        title={
            'text': "<b>Número total de mortes por País</b>",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
            showlegend=False)
    st.plotly_chart(fig)

#Testagem
if paginas == 'Testagem':

    st.title('Dados sobre testagem de Covid-19')
    st.markdown(
        """
        Dados sobre a testagem de Covid-19 nos Países

        Na tabela é mostrado a média do número de testagens, o menor número de testagem em um dia,
        o maior número de testagem em um dia e o total de testagens até o momento.

        """)
    test = total_world[['country', 'tests', 'date']]

    label_to_filter = st.multiselect(
        label="Escolha o País desejado para visualizar os dados",
        options=paises, default='Brazil')

    
    
    #tabela dados testes
    if st.checkbox('Mostrar tabela'):
        st.subheader('Tabela de dados')
        st.write(group_tab(test, 'tests', label_to_filter, 'country'))

    #grafico de linha

    st.text('Foi utilizado média móvel no gráfico para melhor visualização da tendência.')
    st.text('Para alguns países, não há dados desses números na base de dados.')
    fig = px.line(group_plot(test, 'country', label_to_filter, 'date'), x='date', y='tests', color='country', labels={'date':'Data', 'tests':'Nº de testes'})
    fig.update_layout(
    title={
        'text': "<b>Número de testagens por dia</b>",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
        showlegend=True)
    st.plotly_chart(fig)

    #grafico de barra
    test_bar_plot = test.groupby('country').sum()
    test_bar_plot.sort_values('tests', ascending=False, inplace=True)
    fig = px.bar(test_bar_plot, range_x=[-0.6,25.5], labels={'country':'País', 'value':'Nº de testes'})
    
    fig.update_layout(barmode='group', xaxis_tickangle=-45)
    fig.update_layout(
        title={
            'text': "<b>Número total de testagens por País</b>",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
            showlegend=False)
    st.plotly_chart(fig)

        #link da fonte dos dados
    st.markdown("[Fonte dos dados](https://github.com/owid/covid-19-data/tree/master/public/data/testing)")

if paginas == 'Brasil':

    #dados brasil
    cities = pd.read_csv('https://raw.githubusercontent.com/wcota/covid19br/master/cases-gps.csv')
    cities.drop(cities[cities['type']=='D1'].index, inplace=True)
    cities.drop(columns=['type', 'total_per_100k_inhabitants'], inplace=True)
    cities.reset_index(drop=True, inplace=True)

    st.title('Dados sobre Covid-19 no Brasil')
    st.markdown("""
    Nessa seção serão apresentados dados sobre a Covid-19 no Brasil, número de casos, 
    mortes, testes e vacinação""")

    st.subheader('Dados por cidade e estado')
    #selecinando por estado
    cities['cidade'] = cities.name.str.split('/').str[0]
    cities['estado']= cities.name.str.split('/').str[1]
    estados = cities['estado'].unique()
    estado_filter = st.multiselect(
    label="Escolha o estado desejado para visualizar os dados",
    options=estados)

    st.dataframe(cities[cities['estado'].isin(estado_filter)][['cidade','total']].reset_index(drop=True))


    #mapa de casos nas cidades
    fig = px.scatter_mapbox(data_frame=cities, lat='lat', lon='lon',size='total', mapbox_style='open-street-map',
     zoom=2.7, hover_name='name')
    fig.update_layout(title={
    'text': "<b>Número de casos por cidades</b>",
    'y':1,
    'x':0.5,
    'xanchor': 'center',
    'yanchor': 'top'})
    fig.update_layout(
    margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig)

    #grafico de casos por estado
    casos_estados = cities.groupby('estado').agg({'total':'sum', 'lat':'mean','lon':'mean'}).reset_index()

    fig = px.scatter_mapbox(data_frame=casos_estados, lat='lat', lon='lon', size='total',
     mapbox_style='open-street-map', zoom=2.7, hover_name='estado')
    fig.update_layout(title={
    'text': "<b>Número de casos por estados</b>",
    'y':1,
    'x':0.5,
    'xanchor': 'center',
    'yanchor': 'top'})
    fig.update_layout(
    margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig)


    st.markdown("[Fonte dos dados](https://github.com/wcota/covid19br)")
    



#progresso
st.sidebar.title('Desenvolvimento')
st.sidebar.info("""
    Dados que serão adicionados:
    * Covid no Brasil""")

#informações de contato
st.sidebar.title('Sobre')
st.sidebar.info("""
    Dashboard criado por Jeferson Ribeiro
    
    [Github](https://github.com/Jefsuu)
    [Kaggle](https://www.kaggle.com/jefsuu)""")





