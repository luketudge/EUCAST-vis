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
    'Distributions',
    'Observations',
    'ECOFF',
    'ECOFF_tentative',
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


accessed = d['accessed'].iloc[0]

n_distributions = d['Distributions'].iloc[0]
n_observations = d['Observations'].iloc[0]

distributions_text = 'distribution'
observations_text = 'observation'
if n_distributions > 1:
    distributions_text = distributions_text + 's'
if n_observations > 1:
    observations_text = observations_text + 's'
info_text = f'{n_distributions} {distributions_text}, {n_observations} {observations_text}'

ecoff = d['ECOFF'].iloc[0]
ecoff_missing = numpy.isnan(ecoff)
ecoff_tentative = d['ECOFF_tentative'].iloc[0]


show_ecoff = streamlit.sidebar.checkbox('ECOFF')

if show_ecoff:
    if ecoff_missing:
        streamlit.sidebar.markdown('*no ECOFF value available*')
    elif ecoff_tentative:
        streamlit.sidebar.markdown(
                '*ECOFF is tentative (based on fewer than 5 distributions)*'
        )


#%% main column

streamlit.title(antibiotic + ': ' + species)

streamlit.markdown(
    'source: [EUCAST](https://mic.eucast.org) accessed ' + accessed
)

fig = (
    plotnine.ggplot(d, plotnine.aes(x = 'concentration', y = 'n'))
    + plotnine.scale_x_continuous(
        breaks = pandas.unique(d['concentration']),
        trans = mizani.transforms.log2_trans
    )
    + plotnine.scale_fill_manual(
        ['blue', 'red'],
        limits = ['wildtype', 'resistant']
    )
    + plotnine.theme(
        axis_text_x = plotnine.element_text(rotation = 45),
        legend_position = (0.25, 0.75)
    )
    + plotnine.labs(
        title = info_text,
        x = 'concentration (mg/L)'
    )
    + plotnine.geom_col()
)

if show_ecoff:
    fig = (
        fig
        + plotnine.aes(fill = 'strain')
        + plotnine.geom_vline(xintercept = ecoff * 1.5, linetype = 'dashed')
    )

streamlit.pyplot(fig.draw())

streamlit.subheader('Note on limitations')
streamlit.markdown(
    'Different studies often use different MIC concentration ranges. \
    Distributions truncated at the lower end of the scale \
    within the putative wild-type distribution have been excluded. \
    The accepted distributions include studies from a wide variety of sources \
    and time periods and some, on purpose, include high and others low, \
    proportions of resistant organisms, so the distributions must not be used \
    to represent rates of resistance to any agent and cannot be used \
    to compare resistance rates among agents, resistance over time or resistance \
    in different geographic locations.'
)


#%% data (for debugging)

#streamlit.dataframe(d)
