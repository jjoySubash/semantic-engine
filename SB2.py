
import streamlit as st
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from deep_translator import GoogleTranslator
import langdetect

indexName = "mov12"

# Elasticsearch connection
try:
    las = Elasticsearch(
        "https://localhost:9200",
        basic_auth=("elastic", "7G7F*uQ0+DJuUu=lfk1K"),
        ca_certs="D:/TUF/elasticsearch/config/certs/http_ca.crt"
    )
except ConnectionError as e:
    st.error("Connection Error: Unable to connect to Elasticsearch.")

def detect_language(text):
    try:
        return langdetect.detect(text)
    except:
        return "en"

def translate_to_english(text, source_lang):
    if source_lang == "en":
        return text
    try:
        return GoogleTranslator(source=source_lang, target='en').translate(text)
    except Exception as e:
        st.error(f"Translation error: {e}")
        return text

def translate_to_source(text, target_lang):
    if target_lang == "en":
        return text
    try:
        return GoogleTranslator(source='en', target=target_lang).translate(text)
    except:
        return text

def get_language_name(lang_code):
    names = {
        'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
        'it': 'Italian', 'pt': 'Portuguese', 'nl': 'Dutch', 'hi': 'Hindi',
        'ja': 'Japanese', 'ko': 'Korean', 'zh-cn': 'Chinese (Simplified)',
        'ar': 'Arabic', 'ru': 'Russian', 'bn': 'Bengali', 'ur': 'Urdu',
        'th': 'Thai', 'vi': 'Vietnamese'
    }
    return names.get(lang_code, lang_code)

def search(input_keyword, source_lang):
    english_query = translate_to_english(input_keyword, source_lang)
    model = SentenceTransformer('all-mpnet-base-v2')
    vector = model.encode(english_query)
    query = {
        "field": "Embedding",
        "query_vector": vector.tolist(),
        "k": 10,
        "num_candidates": 2838
    }
    res = las.knn_search(index=indexName, knn=query, _source=["Title", "Director", "Rating", "Metascore", "Genre", "Description"])
    return res["hits"]["hits"], english_query

def load_css():
    st.markdown("""
    <style>
    body {
        background-color: #0e1117;
        color: #f9f9f9;
        font-family: 'Poppins', sans-serif;
    }
    .main-title {
        font-size: 3.5em;
        background: linear-gradient(60deg, #007BFF, #00C9A7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.2em;
    }
    .sub-title {
        font-size: 1.2em;
        color: #a0a0a0;
        text-align: center;
        margin-bottom: 2em;
    }
    .result-card {
        background: #1e1e2e;
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        border-left: 4px solid #FFA500;
    }
    .movie-title { font-size: 1.8em; font-weight: 700; }
    .movie-meta { display: flex; gap: 15px; flex-wrap: wrap; margin-bottom: 15px; }
    .meta-item { background-color: #3a3a50; padding: 5px 12px; border-radius: 8px; }
    .meta-label { font-weight: 600; color: #FFA500; margin-right: 5px; }
    .genre-tags { display: flex; gap: 8px; flex-wrap: wrap; margin: 10px 0; }
    .genre-tag { background: #FF4500; color: white; padding: 4px 12px; border-radius: 20px; }
    .movie-plot { color: #d0d0d0; font-size: 1em; margin-top: 15px; line-height: 1.5; }
    .translation-info {
        background-color: #46465a;
        padding: 10px 15px;
        border-radius: 8px;
        font-size: 0.9em;
        border-left: 3px solid #FFD700;
        margin: 20px 0;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    load_css()
    st.markdown("<h1 class='main-title'>STREAMBERRY 🎬</h1>", unsafe_allow_html=True)
    st.markdown("<h3 class='sub-title'>Discover Movies in Any Language</h3>", unsafe_allow_html=True)

    search_query = st.text_input("Enter a movie plot in any language")
    search_clicked = st.button("Find Movies 🔎")

    if search_clicked and search_query:
        with st.spinner('Detecting language and searching...'):
            detected_lang = detect_language(search_query)
            st.session_state.detected_lang = detected_lang
            st.markdown(f"<div class='translation-info'>🔍 Detected language: <strong>{get_language_name(detected_lang)}</strong></div>", unsafe_allow_html=True)

            try:
                results, english_query = search(search_query, detected_lang)
                if detected_lang != 'en':
                    st.markdown(f"<div class='translation-info'>🔄 Translated query: <strong>{english_query}</strong></div>", unsafe_allow_html=True)
                if results:
                    for result in results:
                        src = result.get('_source', {})
                        title = src.get('Title', 'Unknown')
                        director = src.get('Director', 'Unknown')
                        rating = src.get('Rating', 'N/A')
                        metascore = src.get('Metascore', 'N/A')
                        genre = src.get('Genre', '')
                        description = src.get('Description', '')
                        if detected_lang != 'en':
                            description = translate_to_source(description, detected_lang)
                        genre_tags = ''.join([f"<span class='genre-tag'>{g.strip()}</span>" for g in genre.split(',')])
                        st.markdown(f"""
                        <div class='result-card'>
                            <h3 class='movie-title'>{title}</h3>
                            <div class='movie-meta'>
                                <span class='meta-item'><span class='meta-label'>Director:</span> {director}</span>
                                <span class='meta-item'><span class='meta-label'>Rating:</span> {rating}</span>
                                <span class='meta-item'><span class='meta-label'>Metascore:</span> {metascore}</span>
                            </div>
                            <div class='genre-tags'>{genre_tags}</div>
                            <p class='movie-plot'>{description}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("No results found.")
            except Exception as e:
                st.error(f"Search error: {e}")

if __name__ == "__main__":
    main()
