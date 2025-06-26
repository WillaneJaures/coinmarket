import streamlit as st 
import mysql.connector
import pandas as pd
import plotly.express as px

#connexion mysql

def get_connexion():
    return mysql.connector.connect(
        host="localhost",
        port=8889,
        user="root",
        password="mysql",
        database="coinmarketdb"
    )


#titre
st.title("Visualisation des prix de produits")

#connexion
try:
    conn= get_connexion()
    cursor = conn.cursor(dictionary=True)
    query= "SELECT Name,price,Product,Area FROM Product;"
    df = pd.read_sql(query, conn)

    st.success("Connexion à MySQL réussie")

    produits = df['Product'].unique()
    produit_selected = st.selectbox("selectionne un produit : ", produits)

    filtered_df = df[df['Product']==produit_selected]

    #affichage table
    st.subheader("Donnee filtrees")
    st.dataframe(filtered_df)

    #affichage tableau
    st.subheader("Evolution du prix")
    fig = px.line(df, x="Product", y= "price",color="Product", title=f"Prix de {produit_selected}")
    st.plotly_chart(fig)

    fig1 = px.box(df, x="Area", y="price", title="Répartition des prix par zone")
    st.plotly_chart(fig1)

    fig2 = px.pie(df, names="Product", title="Répartition des produits")
    st.plotly_chart(fig2)

except Exception as e:
    st.error(f"Erreur : {e}")
