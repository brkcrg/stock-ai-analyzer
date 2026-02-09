import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS
from PIL import Image
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Page Config ---
st.set_page_config(
    page_title="AI Borsa Sinyal Analizi",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Sidebar & API Key Setup ---
st.sidebar.title("Ayarlar")
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
    api_key = st.sidebar.text_input("Google Gemini API Anahtarı", type="password")

if not api_key:
    st.error("Lütfen Google Gemini API anahtarınızı girin veya .env dosyasına ekleyin.")
    st.stop()

genai.configure(api_key=api_key)

# --- Functions ---

def analyze_chart(image, ticker):
    """
    Analyzes the chart image using Gemini Flash (Latest).
    """
    model = genai.GenerativeModel('gemini-flash-latest')
    
    prompt = f"""
    Sen uzman bir borsa teknik analistisin. Bu {ticker} hissesinin grafiği.
    Lütfen şu başlıklar altında detaylı bir analiz yap:
    1. **Trend Analizi:** Ana trend ne yönde? (Yükseliş, Düşüş, Yatay)
    2. **Formasyonlar:** Grafikte belirgin bir formasyon var mı? (Bayrak, OBO, TOBO, Kama vb.)
    3. **Destek ve Dirençler:** Önemli destek ve direnç seviyeleri nereler?
    4. **İndikatör Yorumu:** (Eğer görünüyorsa) Hacim veya hareketli ortalamalar ne söylüyor?
    
    Analizini madde madde ve anlaşılır yaz.
    """
    
    with st.spinner(f"{ticker} grafiği inceleniyor..."):
        try:
            response = model.generate_content([prompt, image])
            return response.text
        except Exception as e:
            return f"Hata oluştu: {str(e)}"

def get_sentiment(ticker):
    """
    Searches for recent news and sentiment using DuckDuckGo.
    """
    search_query = f"{ticker} hisse yorum haber son dakika"
    
    with st.spinner(f"{ticker} için piyasa haberleri taranıyor..."):
        try:
            results = DDGS().text(search_query, max_results=5)
            summary_text = "\n\n".join([f"- {r['title']}: {r['body']}" for r in results])
            return summary_text
        except Exception as e:
            return f"Hata oluştu: {str(e)}"

def synthesize_signal(technical_analysis, sentiment_data, ticker):
    """
    Combines technical and sentiment analysis to generate a final signal.
    """
    model = genai.GenerativeModel('gemini-flash-latest')
    
    prompt = f"""
    Aşağıda {ticker} hissesi için iki farklı veri kaynağı var.
    
    **1. Grafik Analizi (Teknik):**
    {technical_analysis}
    
    **2. Piyasa Haberleri ve Duygu Durumu (Temel/Sentiment):**
    {sentiment_data}
    
    Bu iki veriyi sentezleyerek YATIRIMCIYA ÖZET BİR RAPOR SUN.
    
    Çıktı Formatı:
    # {ticker} Yatırım Sinyali
    
    ## 🚦 GÖRÜŞ: [AL / SAT / TUT / NÖTR] (Sebebini 1 cümleyle açıkla)
    
    ## 🎯 Kısa Vadeli Hedefler
    - **İlk Hedef:** [Fiyat]
    - **İkinci Hedef:** [Fiyat]
    - **Stop Loss (Zarar Kes):** [Fiyat]
    
    ## 📝 Özet Değerlendirme
    (Teknik ve temel verileri birleştirerek 2-3 cümlelik final yorumu.)
    """
    
    with st.spinner("Veriler birleştirilip final sinyali üretiliyor..."):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Hata oluştu: {str(e)}"

# --- Main UI ---
st.title("📈 AI Destekli Borsa Sinyal Analizcisi")
st.markdown("""
Bu uygulama, yüklediğiniz grafik görselini analiz eder ve internetteki son haberlerle birleştirerek 
size yapay zeka destekli bir **AL/SAT sinyali** üretir.
""")

col1, col2 = st.columns([1, 2])

with col1:
    ticker = st.text_input("Hisse Sembolü (Örn: THYAO, BTCUSDT)", value="").upper()
    uploaded_file = st.file_uploader("Grafik Yükle (Ekran Görüntüsü)", type=["jpg", "png", "jpeg"])
    analyze_btn = st.button("Analiz Et", type="primary")

with col2:
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Yüklenen Grafik', use_container_width=True)

if analyze_btn:
    if not ticker:
        st.warning("Lütfen bir hisse sembolü girin.")
    elif not uploaded_file:
        st.warning("Lütfen bir grafik görseli yükleyin.")
    else:
        # 1. Image Analysis
        technical_analysis = analyze_chart(image, ticker)
        with st.expander("🔍 Detaylı Teknik Analiz (Gemini Vision)"):
            st.markdown(technical_analysis)
        
        # 2. Sentiment Analysis
        sentiment_data = get_sentiment(ticker)
        with st.expander("📰 Piyasa Haberleri ve Sentiment"):
            st.markdown(sentiment_data)
            
        # 3. Final Synthesis
        final_signal = synthesize_signal(technical_analysis, sentiment_data, ticker)
        st.divider()
        st.markdown(final_signal)
