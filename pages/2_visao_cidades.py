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

st.set_page_config(page_title='Cidades', page_icon='🏙️', layout='wide')
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
def top_cities_restaurants(df1):
    df_aux = (df1.loc[:, ["restaurant_id", "country", "city"]]
                         .groupby(["country", "city"])
                         .count().sort_values(["restaurant_id", "city"], ascending=[False, True]).reset_index())

    fig = px.bar(df_aux.head(10),x="city", y="restaurant_id",text="restaurant_id", text_auto=".2f",color="country", title="Top 10 Cidades com mais Restaurantes na Base de Dados",
                 labels={"city": "Cidade", "restaurant_id": "Quantidade de Restaurantes", "country": "País"})
    return fig
# ------------------------------------------------------------------------------------------------------------------------------------------------

def top_7_cities_4(df1):
    df_aux = (df1.loc[df1['aggregate_rating'] >= 4, ['city', 'restaurant_id', 'country']]
                 .groupby(['country', 'city']).count()
                 .sort_values(["restaurant_id", "city"],ascending=[False, True]).reset_index())

    fig = px.bar(
        df_aux.head(7),
        x="city",
        y="restaurant_id",
        text="restaurant_id",
        text_auto=".2f",
        color="country",
        title="Top 7 Cidades com Avaliação média Acima de 4",
        labels={
            "city": "Cidade",
            "restaurant_id": "Quantidade de Restaurantes",
            "country": "País"
        }
    )
    return fig
# ------------------------------------------------------------------------------------------------------------------------------------------------

def top_worst_cities_4(df1):
    df_aux = (df1.loc[df1['aggregate_rating'] <= 2.5, ['city', 'restaurant_id', 'country']]
                 .groupby(['country', 'city']).count()
                 .sort_values(["restaurant_id", "city"],ascending=[False, True]).reset_index())

    fig = px.bar(
        df_aux.head(7),
        x="city",
        y="restaurant_id",
        text="restaurant_id",
        text_auto=".2f",
        color="country",
        title="Top 7 Cidades com Avaliação média Abaixo de 2.5",
        labels={
            "city": "Cidade",
            "restaurant_id": "Quantidade de Restaurantes",
            "country": "País"
        }
    )
    return fig

# ------------------------------------------------------------------------------------------------------------------------------------------------

def top_cuisine(df1):
    df_aux = (df1.loc[:, ['city', 'country', 'cuisines']]
                 .groupby(['country', 'city']).nunique()
                 .sort_values(['cuisines', 'city'],ascending=[False, True]).reset_index())

    fig = px.bar(
        df_aux.head(10),
        x="city",
        y="cuisines",
        text="cuisines",
        text_auto=".2f",
        color="country",
        title="Top 10 Cidades mais restaurantes com tipos culinários distintos",
        labels={
            "city": "Cidade",
            "cuisines": "Quantidade dCulinárias Distintas",
            "country": "País"
        }
    )
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
st.header('Cidades 🏙️')
st.markdown('---')

st.sidebar.markdown('## Selecione um País')


data_select = st.sidebar.multiselect(
    'Quais os países ?',
    df1.loc[:, 'country'].unique().tolist(),
    default=["Brazil", "England", "Qatar", "South Africa", "Canada", "Australia"])


st.sidebar.markdown("""---""")
st.sidebar.markdown('#### Feito por Henrique Kubo')

# Filtro de País
linhas_selecionadas = df1['country'].isin(data_select)
df1 = df1.loc[linhas_selecionadas, :]

# =====================================================================================
#                           LAYOUT STREAMNLIT
# =====================================================================================

with st.container():
    fig = top_cities_restaurants(df1)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("""---""")

with st.container():
    col1,col2 = st.columns(2)
    with col1:
        fig = top_7_cities_4(df1)
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        fig = top_worst_cities_4(df1)
        st.plotly_chart(fig, use_container_width=True)

st.markdown("""---""")

with st.container():
    fig = top_cuisine(df1)
    st.plotly_chart(fig, use_container_width=True)