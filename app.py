from pandas.core.arrays.sparse import dtype
import streamlit as st
import numpy as np
import pandas as pd
import urllib.request
import json
import re
import altair as alt

PATH = 'https://raw.githubusercontent.com/sjcdigital/data-etl/main/agenda-presidente/bolsonaro/report.json'

st.set_page_config(
    page_title="Agenda Presidencial | sjcdigital",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache(suppress_st_warning=True, persist=True)
def get_data():
    with urllib.request.urlopen(PATH) as url:
        data = json.loads(url.read().decode())

        horasTotaisLista = data['horasTotaisLista']
        horasAnoLista = data['horasAnoLista']

        duracaoText = data['duracaoText']
        teveAgenda = data['teveAgenda']

        df_full = pd.DataFrame.from_dict(horasTotaisLista)
        df_full['data'] = pd.to_datetime(df_full['data'], dayfirst=True)
        df_full = df_full.sort_values(by='data', ascending=True)

        df_by_year = pd.DataFrame.from_dict(horasAnoLista)
        df_by_year = df_by_year.sort_values(by='data', ascending=True)

        return (duracaoText, teveAgenda), df_full, df_by_year



(duracaoText, teveAgenda), df, df_by_year = get_data()

# Sidebar
st.sidebar.markdown(
    '<div style="text-align: center;margin: 2rem auto;">sjcdigital</div>', unsafe_allow_html=True)

st.sidebar.image(
    'https://avatars.githubusercontent.com/u/5611890', use_column_width=True)

available_years = sorted(list(df_by_year['data']))

anos = sorted(st.sidebar.multiselect(
    'Ano', available_years, available_years))

st.title('Agenda Presidencial')

st.header('Resumo (geral)')

st.caption(f'{duracaoText}')
st.caption(f'{teveAgenda}')

# Summarized
st.header('Nos anos selecionados ({})'.format(', '.join(anos)))

datasets = [df.set_index(
    ['data']).loc[f'{ano}-01-01':f'{ano}-12-31'] for ano in anos]

data = pd.concat(datasets)

# data = data.T.reset_index()

data.loc[:, 'year'] = data.index.strftime('%Y')
data.loc[:, 'month'] = data.index.strftime('%m')
data.loc[:, 'month_str'] = data.index.strftime('%B')
data.loc[:, 'week_day'] = data.index.strftime('%A')

data.loc[:, 'minutes'] = data['duracaoText'].map(
    lambda value: int(re.findall(r'\d+', value)[0]))

data.loc[:, 'hours'] = data['minutes'].map(
    lambda value: round(value / 60, 2))

data.loc[:, 'no_commitment'] = data['semCompromisso'].map(
    lambda value: 1 if value == 'Sim' else 0)

data = data[['year', 'month', 'month_str', 'week_day',
             'minutes', 'hours', 'no_commitment']]

# Count by year
chart = (
    alt.Chart(data)
    .configure(
        axisX=alt.AxisConfig(
            labelAngle=0
        )
    )
    .mark_bar(opacity=0.8)
    .encode(
        x=alt.X('year', title='Ano'),
        y=alt.Y('sum(no_commitment)', title='Dias sem compromisso', stack=None),
        color=alt.Color('year:N', title='Ano'),
        tooltip=[alt.Tooltip('sum(no_commitment)',
                             title='Dias sem compromisso')]
    )
)

col1, _ = st.columns(2)

with col1:
    st.altair_chart(chart, use_container_width=True)

# By Year

for ano in anos:
    st.subheader(f'{ano}:')

    data_by_year = df_by_year.loc[df_by_year['data'] == ano, [
        'duracaoText', 'teveAgenda'
    ]]

    _duracaoText, _teveAgenda = data_by_year.head(1).values[0]

    st.caption(f'{_duracaoText}')
    st.caption(f'{_teveAgenda}')

    year_data = data.loc[data['year'] == ano]

    chart = (
        alt.Chart(year_data)
        .configure(
            axisX=alt.AxisConfig(
                labelAngle=0
            )
        )
        .mark_bar(opacity=0.5, color='red')
        .encode(
            x=alt.X('month_str', title='Mês',
                    sort=alt.EncodingSortField(field='month')),
            y=alt.Y('sum(no_commitment)',
                    title='Dias sem compromisso', stack=None),
            tooltip=[alt.Tooltip('sum(no_commitment)',
                                title='Dias sem compromisso'),
                     alt.Tooltip('average(hours)',
                                 format=',.3r',
                                 title='Média de horas em compromissos')]
        )
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        st.altair_chart(chart, use_container_width=True)

    with col2:
        diasSemCompromisso = int(re.findall(
            r'Foram (\d+) dias sem compromisso', _teveAgenda)[0])

        diasTotal = int(re.findall(r'um total de (\d+) em', _teveAgenda)[0])

        pieChartData = pd.DataFrame({
            'count': [
                diasTotal - diasSemCompromisso,
                diasSemCompromisso
            ],
            'has_commitment': [
                'Compromisso',
                'Sem Compromisso',
            ]
        })

        # year_data
        st.vega_lite_chart(pieChartData, {
            "title": 'Contagem anual de compromissos',
            "height": 300,
            'mark': {"type": "arc", "innerRadius": 50, 'tooltip': True},
            'encoding': {
                'theta': {'field': 'count', 'type': 'quantitative', 'title': 'Dias', },
                'color': {
                    "field": "has_commitment", "type": "nominal", 'title': '',
                    "scale": {"range": ["#7093B9", "#FF7F7F"]}
                },
                'tooltip': {'field': 'count', 'type': 'quantitative'}
            },
            "view": {"stroke": None}
        }, use_container_width=True)


# st.date_input('Dia', value=None, min_value=None, max_value=None, key=None, help=None, on_change=None, args=None, kwargs=None)

# data = df.loc[df['semCompromisso'] == sem_compromisso]

# if sem_compromisso:
#     data = data.loc[df['semCompromisso'] == 'Não']

# if teve_agenda:
#     data = data.loc[df['teveAgenda'] != '']

# st.write("### Gross Agricultural Production ($B)", data.sort_index())
