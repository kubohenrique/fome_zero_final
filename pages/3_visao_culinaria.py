# ===========================================================================================
#                                       BIBLIOTECA
# ===========================================================================================

import pandas as pd
import numpy as np
import plotly.express as px
import folium
import streamlit as st
import datetime
import inflection

from haversine import haversine
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title='Culinária', page_icon='🍽️', layout='wide')
# ===========================================================================================
#                                       VARIÁVEIS
# ===========================================================================================

COUNTRIES = {
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
# ------------------------------------------------------------------------------------------------------------------------------------------------

COLORS = {
   "3F7E00": "darkgreen",
   "5BA829": "green",
   "9ACD32": "lightgreen",
   "CDD614": "orange",
   "FFBA00": "red",
   "CBCBC8": "darkred",
   "FF7800": "darkred",
}

# ===========================================================================================
#                                       FUNÇÕES
# ===========================================================================================

def rename_columns(df):
    df = df.copy()
    title = lambda x: inflection.titleize(x) 
    snakecase = lambda x: inflection.underscore(x) 
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old)) 
    cols_new = list(map(snakecase, cols_old))
    df.columns = cols_new
    return df
# ------------------------------------------------------------------------------------------------------------------------------------------------
def country_name(country_id):
    return COUNTRIES[country_id]
# ------------------------------------------------------------------------------------------------------------------------------------------------
def create_price_tye(price_range):
    if price_range == 1:
        return "cheap"
    elif price_range == 2: 
        return "normal"
    elif price_range == 3: 
        return "expensive"
    else:
        return "gourmet"
# ------------------------------------------------------------------------------------------------------------------------------------------------
def color_name(color_code): 
    return COLORS[color_code]
# ------------------------------------------------------------------------------------------------------------------------------------------------
def adjust_columns_order(dataframe):
    df = dataframe.copy()

    new_cols_order = [
        "restaurant_id",
        "restaurant_name",
        "country",
        "city",
        "address",
        "locality",
        "locality_verbose",
        "longitude",
        "latitude",
        "cuisines",
        "price_type",
        "average_cost_for_two",
        "currency",
        "has_table_booking",
        "has_online_delivery",
        "is_delivering_now",
        "aggregate_rating",
        "rating_color",
        "color_name",
        "rating_text",
        "votes",
    ]

    return df.loc[:, new_cols_order]

# ------------------------------------------------------------------------------------------------------------------------------------------------
def clean_code(df1):
    df1 = df1.dropna()
    df1["country"] = df1.loc[:, "country_code"].apply(lambda x: country_name(x))
    df1["price_type"] = df1.loc[:, "price_range"].apply(lambda x: create_price_tye(x))
    df1["color_name"] = df1.loc[:, "rating_color"].apply(lambda x: color_name(x))
    df1["cuisines"] = df1.loc[:, "cuisines"].apply(lambda x: x.split(",")[0])    
    return df1
# ------------------------------------------------------------------------------------------------------------------------------------------------
def top_cuisine(df1, top_b):
    df_aux = df1.loc[:,['cuisines', 'aggregate_rating']].groupby('cuisines').max().sort_values('aggregate_rating', ascending=top_b).reset_index()
    fig = px.bar(df_aux.head(top_n), x='cuisines', y='aggregate_rating', labels={"cuisines": "Tipo de Culinária", "aggregate_rating": "Avaliação Média",})
    return fig

# ===========================================================================================
#                               INICIO DA ESTRUTURA LÓGICA
# ===========================================================================================

# Importando o Data set
df = pd.read_csv('dataset/zomato.csv')

# Renomeando as Colunas
df = rename_columns(df)

# Limpeza dos dados

df = clean_code(df)

# Organizando as Colunas

df1 = adjust_columns_order(df)

# cópia do código

df1 = df.copy()

# =====================================================================================
#                           BARRA LATERAL
# =====================================================================================
st.header('Culinária 🍽️')
st.markdown('---')

st.sidebar.markdown('## Selecione um País')


data_select = st.sidebar.multiselect(
    'Quais os países ?',
    df1.loc[:, 'country'].unique().tolist(),
    default=["Brazil", "England", "Qatar", "South Africa", "Canada", "Australia"])

top_n = st.sidebar.slider("Selecione a quantidade de Restaurantes que deseja visualizar", 1, 20, 10)

cuisine_select = st.sidebar.multiselect(
    'Quais culinárias ?',
    df1.loc[:, "cuisines"].unique().tolist(),
    default=["Home-made", "BBQ", "Japanese", "Brazilian", "Arabian", "American", "Italian",])


st.sidebar.markdown("""---""")
st.sidebar.markdown('#### Feito por Henrique Kubo')

# Filtro de País
linhas_selecionadas = df1['country'].isin(data_select)
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de Culinária
linhas_selecionadas_culinaria = df1['cuisines'].isin(cuisine_select)
df1 = df1.loc[linhas_selecionadas_culinaria, :]

# =====================================================================================
#                           LAYOUT STREAMNLIT
# =====================================================================================

with st.container():
    st.markdown(f'## Top {top_n} Restaurantes melhores avaliados')
    df_aux = (df1.loc[:,['restaurant_id', 'restaurant_name', 'country', 'city', 'cuisines', 'average_cost_for_two', 'aggregate_rating', 'votes']]
        .sort_values(['aggregate_rating', 'restaurant_id'], ascending=[False, True])).head(top_n)
    st.dataframe(df_aux)

st.sidebar.markdown("""---""")

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'##### Top {top_n} Melhores Tipos de Culinária')
        fig = top_cuisine(df1, False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(f'##### Top {top_n} Piores Tipos de Culinária')
        fig = top_cuisine(df1, True)
        st.plotly_chart(fig, use_container_width=True)