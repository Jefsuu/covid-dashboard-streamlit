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

#dados brasil
cities = pd.read_csv('https://raw.githubusercontent.com/wcota/covid19br/master/cases-gps.csv')
cities.drop(cities[cities['type']=='D1'].index, inplace=True)
cities.drop(columns=['type', 'total_per_100k_inhabitants'], inplace=True)
cities.reset_index(drop=True, inplace=True)

#total world
total_world = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv',
 usecols=['location', 'date','new_cases','new_deaths', 'new_vaccinations', 'new_tests'], parse_dates=['date'])
total_world['date'] = pd.to_datetime(total_world['date'])
total_world.rename(columns={'location':'country','new_cases':'cases', 'new_deaths':'deaths',
'new_vaccinations':'vaccinations', 'new_tests':'tests'}, inplace=True)

#Configurações da pagina
st.set_page_config(
    layout="centered",
    initial_sidebar_state="expanded",
    page_title="Dashboard Covid-19",
    )

#paginas
st.sidebar.title('Navegação')
paginas = st.sidebar.radio('Paginas', ['Vacinação','Casos', 'Vacinas', 'Testagem', 'Brasil'])



#lista de países
paises = df.country.unique().tolist()

#dashboard
if paginas == 'Vacinação':
    st.title('Dados de vacinação COVID-19')
    st.markdown(
        """
        Dados sobre o progresso de vacinação nos Países

        Na tabela é mostrado a média do número de vacinações, o menor número de vacinação em um dia,
        o maior número de vacinação em um dia e o total de vacinações até o momento

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


    #grafico de número de vacinações nos países

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

    st.title('Dados sobre o número de casos de Covid-19 no mundo')
    st.markdown(
    """
    Dados sobre o número de casos nos Países

    Na tabela é mostrado a média do número de casos, o menor número de casos em um dia,
    o maior número de casos em um dia e o total de casos até o momento.

    """)
    label_to_filter = st.multiselect(
        label="Escolha o País desejado para visualizar os dados",
        options=paises, default='Brazil')

    if st.checkbox('Mostrar tabela'):
        st.subheader('Tabela de dados')
        group = total_world[total_world['country'].isin(label_to_filter)]
        group = group.groupby(['country'])['cases'].agg(['mean', 'min', 'max', 'sum'])
        group = pd.DataFrame(group)
        group.reset_index(inplace=True)
        group['mean'] = group['mean'].apply(lambda x: round(x))
        st.write(group)

    cases = total_world[['country','date', 'cases']]
    cases = cases[cases['country'].isin(label_to_filter)].reset_index(drop=True)
    cases_group = cases.set_index('country')
    cases_group = cases_group.groupby('country').rolling(7, min_periods=1).mean()
    plot_cases = cases_group.reset_index().join(cases['date'])

    fig = px.line(data_frame=plot_cases, x='date', y='cases', color='country', labels={'cases':'Nº de casos',
    'date':'Data'})
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

#Testagem
if paginas == 'Testagem':

    st.title('Testagem de Covid-19 nos Países')
    st.markdown(
        """
        Dados sobre a testagem de Covid-19 nos Países

        Na tabela é mostrado a média do número de testagens, o menor número de testagem em um dia,
        o maior número de testagem em um dia e o total de testagens até o momento.

        Para alguns países, não há dados desses números na base de dados.

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

    plot = test[test['country'].isin(label_to_filter)].reset_index(drop=True)
    plot['date'] = pd.to_datetime(plot['date'], format='%Y-%m-%d')

    
    a = plot.set_index('country')
    a = a.groupby('country').rolling(7, min_periods=1).mean()
    b = a.reset_index().join(plot['date'])

    fig = px.line(b, x='date', y='daily_test', color='country', labels={'date':'Data', 'daily_test':'Nº de testes'})
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
    test_bar_plot.sort_values('daily_test', ascending=False, inplace=True)
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





