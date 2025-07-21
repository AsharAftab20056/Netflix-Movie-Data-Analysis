
import pandas as pd
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

netflix_df = pd.read_csv("Netflix Data.csv", encoding='ISO-8859-1')

netflix_df['Genre'] = netflix_df['Genre'].astype(str).str.strip().str.lower()
netflix_df['Genre'] = netflix_df['Genre'].apply(lambda x: x.split(',')[0] if ',' in x else x)

netflix_df['Popularity'] = pd.to_numeric(netflix_df['Popularity'], errors='coerce')
netflix_df['Vote_Average'] = pd.to_numeric(netflix_df['Vote_Average'], errors='coerce')
netflix_df = netflix_df.dropna(subset=['Genre', 'Popularity', 'Vote_Average', 'Original_Language'])

# One-hot encode genre and language columns
genre_encoded = pd.get_dummies(netflix_df['Genre'], prefix='Genre')
lang_encoded = pd.get_dummies(netflix_df['Original_Language'], prefix='Lang', drop_first=True)

# Feature scaling and applying Normalization
features = pd.concat([netflix_df[['Popularity', 'Vote_Average']], genre_encoded, lang_encoded], axis=1)
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)

# Cosine similarity
cosine_sim = cosine_similarity(features_scaled)

# Making Recommendation function (main part of the code)
def recommend_movies(title, top_n=5):
    if title not in netflix_df['Title'].values:
        return pd.DataFrame()
    idx = netflix_df[netflix_df['Title'] == title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    results = netflix_df.iloc[[i[0] for i in sim_scores]][['Title', 'Genre', 'Popularity', 'Vote_Average', 'Original_Language']]
    
# Capitalize Genre and Language for readability
    results['Genre'] = results['Genre'].str.title()
    results['Original_Language'] = results['Original_Language'].str.upper()
    return results

# Streamlit UI
st.title("🎬 Welcome to Netflix Movies Recommender")
selected_movie = st.selectbox("Select a movie:", sorted(netflix_df['Title'].unique()))

if st.button("🔍Recommend"):
    recommendations = recommend_movies(selected_movie)
    if not recommendations.empty:
        st.subheader("Recommended Movies:")
        st.dataframe(recommendations.reset_index(drop=True))
    else:
        st.warning("Movie not found in dataset.")
