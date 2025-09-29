import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import ast

# =====================
# CONFIG
# =====================
st.set_page_config(page_title="Dashboard de MoviesTMDB", layout='wide')
st.title("🎬 Dashboard de Análise de Filmes (TMDb)")
st.markdown("Este painel interativo apresenta **insights sobre o dataset de filmes da TMDb**, "
            "permitindo explorar métricas de produção, desempenho comercial e padrões culturais "
            "ao longo dos anos. Use os filtros abaixo para refinar as análises.")

@st.cache_data
def load_data():
    return pd.read_csv('moviesTratado.csv')

df = load_data()

# =====================
# FILTRO POR GÊNERO
# =====================
df["genres"] = df["genres"].apply(lambda x: ast.literal_eval(x) if pd.notna(x) and x != "" else [])
df["genre_name"] = df["genres"].apply(lambda x: [d["name"] for d in x])
df_exploded_genres = df.explode("genre_name")

all_genres = sorted(df_exploded_genres["genre_name"].dropna().unique())
selected_genre = st.sidebar.selectbox("🎭 Selecione um gênero para filtrar:", ["Todos"] + list(all_genres))

if selected_genre != "Todos":
    df = df_exploded_genres[df_exploded_genres["genre_name"] == selected_genre]
else:
    df = df_exploded_genres.copy()

# =====================
# MÉTRICAS GERAIS
# =====================
st.subheader('📊 Principais Métricas Gerais')
col1, col2, col3 = st.columns(3)
col1.metric("Total de Filmes", len(df))
col2.metric("Soma dos Orçamentos", f"${df['budget'].sum():,.0f}")
col3.metric("Média das Notas", round(df['vote_average'].mean(), 2))

# =====================
# FILMES POR ANO
# =====================
df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
df['release_year'] = df['release_date'].dt.year
df_year = df.dropna(subset=['release_year'])

movies_per_year = (
    df_year.groupby('release_year')['title']
    .count()
    .reset_index()
    .rename(columns={'title': 'count'})
    .sort_values('release_year')
)

max_movies_year = movies_per_year.loc[movies_per_year['count'].idxmax()]
year_with_most_movies = int(max_movies_year['release_year'])

st.subheader("📈 Quantidade de Filmes por Ano")
fig, ax = plt.subplots(figsize=(15, 6))
sns.barplot(x='release_year', y='count', data=movies_per_year, color='skyblue',palette="viridis", ax=ax)
plt.xticks(rotation=90)
ax.axvline(x=movies_per_year[movies_per_year['release_year'] == year_with_most_movies].index[0],
           color='red', linestyle='--',
           label=f'Ano com mais filmes: {year_with_most_movies}')
plt.legend()
st.pyplot(fig)

st.markdown(f"""
Entre os anos analisados, **{year_with_most_movies} foi o ano com maior número de filmes lançados**.  
Podemos observar um aumento constante na produção a partir da década de 90, refletindo a expansão das tecnologias digitais, 
a popularização de novas mídias e a globalização do mercado cinematográfico.
""")

# =====================
# DISTRIBUIÇÃO DAS NOTAS
# =====================
st.subheader("⭐ Distribuição das Notas Médias")
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(data=df, x='vote_average', kde=True,palette="viridis", ax=ax)
st.pyplot(fig)

st.markdown("""
A distribuição das notas revela que a **média global está em torno de 6.3**, indicando uma tendência centralizada.  
Poucos filmes recebem notas extremas (muito baixas ou muito altas), reforçando que a maioria se concentra em avaliações medianas. 
Porém, se observa um possível outlier, com uma nota 7 sobrepondo uma parte dos filmes.
""")

# =====================
# ORÇAMENTO X RECEITA
# =====================
st.subheader("💰 Relação entre Orçamento e Receita")
fig, ax = plt.subplots(figsize=(10, 6))
sns.scatterplot(data=df, x='budget', y='revenue', color='purple', alpha=0.6, ax=ax)
st.pyplot(fig)

st.markdown("""
A análise mostra que **maiores orçamentos não garantem proporcionalmente maiores receitas**.  
Muitos filmes com grandes investimentos registraram bilheterias abaixo do esperado.  
Ainda assim, observa-se que as maiores receitas estão concentradas em produções com alto orçamento — 
refletindo o risco-recompensa de Hollywood.
""")

# =====================
# FILMES POR IDIOMA
# =====================
st.subheader("🌍 Número de Filmes por Idioma")
top_languages = df["original_language"].value_counts().nlargest(10).index
df_top = df[df["original_language"].isin(top_languages)]

fig, ax = plt.subplots(figsize=(10, 6))
sns.countplot(data=df_top, x="original_language", order=top_languages, palette="viridis", ax=ax)
ax.set_title("Número de Filmes por Idioma Original", fontsize=14, weight="bold", pad=15)
ax.tick_params(axis="x", rotation=45)
sns.despine()
st.pyplot(fig)

st.markdown("""
O **inglês domina amplamente** a produção cinematográfica, refletindo a centralidade da indústria hollywoodiana no mercado global.  
Outros idiomas aparecem em menor escala, mas demonstram a diversidade cultural presente no dataset.
""")

# =====================
# TOP PRODUTORAS
# =====================
st.subheader("🏢 Top 10 Produtoras com Mais Filmes")

df["production_companies"] = df["production_companies"].apply(
    lambda x: ast.literal_eval(x) if pd.notna(x) and x != "" else []
)
df["company_name"] = df["production_companies"].apply(lambda x: [d["name"] for d in x])
df_exploded_companies = df.explode("company_name")
company_counts = df_exploded_companies["company_name"].value_counts().head(10)

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x=company_counts.values, y=company_counts.index, palette="viridis", ax=ax)
st.pyplot(fig)

st.markdown("""
Entre as produtoras, a **Warner Bros. lidera com mais de 250 filmes**, seguida de perto por outras grandes como Universal, Paramount e Columbia.  
Essas companhias formam o núcleo da indústria cinematográfica mundial, com presença marcante em diferentes gêneros e décadas.
""")

# =====================
# AMOSTRA DO DATAFRAME
# =====================
st.subheader("📋 Amostra dos Dados")
st.dataframe(df.head(20))
