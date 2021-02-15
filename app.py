"""
Display the EUCAST data.
"""

import mizani
import numpy
import pandas
import plotnine
import streamlit


DATA_FILEPATH = 'EUCAST_data.csv'

CONCENTRATION_COLS = [
    '0.002',
    '0.004',
    '0.008',
    '0.016',
    '0.03',
    '0.06',
    '0.125',
    '0.25',
    '0.5',
    '1',
    '2',
    '4',
    '8',
    '16',
    '32',
    '64',
    '128',
    '256',
    '512'
]

OTHER_COLS = [
    'ANTIBIOTIC',
    'SPECIES',
    'ECOFF',
    'accessed'
]


#%% wrangle data

d = pandas.read_csv(DATA_FILEPATH)

d = pandas.melt(
    d,
    id_vars = OTHER_COLS,
    value_vars = CONCENTRATION_COLS,
    var_name = 'concentration',
    value_name = 'n'
)

d['concentration'] = d['concentration'].astype(float)

d['strain'] = numpy.where(d['concentration'] > d['ECOFF'], 'resistant', 'wildtype')


#%% sidebar

antibiotic = streamlit.sidebar.selectbox(
    'antibiotic',
    pandas.unique(d['ANTIBIOTIC'])
)

d = d[d['ANTIBIOTIC'] == antibiotic]


species = streamlit.sidebar.selectbox(
    'bacteria species',
    pandas.unique(d['SPECIES'])
)

d = d[d['SPECIES'] == species]


#%% main column

streamlit.title('EUCAST')

streamlit.markdown('accessed ' + d['accessed'].iloc[0])

streamlit.header(antibiotic + ': ' + species)

fig = (
    plotnine.ggplot(d, plotnine.aes(x = 'concentration', y = 'n'))
    + plotnine.scale_x_continuous(
        breaks = pandas.unique(d['concentration']),
        trans = mizani.transforms.log2_trans
    )
    + plotnine.theme(
        axis_text_x = plotnine.element_text(rotation = 45)
    )
    + plotnine.labs(x = 'concentration (mg/L)')
    + plotnine.geom_col()
)


streamlit.pyplot(fig.draw())


#%% data (for debugging)

streamlit.dataframe(d)
