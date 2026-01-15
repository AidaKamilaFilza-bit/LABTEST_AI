

import streamlit as st
import nltk
from nltk.tokenize import sent_tokenize
from PyPDF2 import PdfReader


st.set_page_config(
    page_title="Text Chunking using NLTK",
    layout="wide"
)

st.title("Text Chunking Web App (NLTK Sentence Tokenizer)")
st.caption("Semantic sentence chunking from PDF text")

# Download NLTK resources

nltk.download("punkt")

# Step 1: Upload PDF file

uploaded_pdf = st.file_uploader(
    "Upload a PDF file",
    type=["pdf"]
)

if uploaded_pdf is not None:

    
    # Step 2: Extract text from PDF
 
    reader = PdfReader(uploaded_pdf)
    extracted_text = ""

    for page in reader.pages:
        extracted_text += page.extract_text()

  
    # Step 3: Sentence preprocessing
  
    sentences = sent_tokenize(extracted_text)

    st.subheader("🧩 Sample Extracted Sentences (Index 58–68)")

    if len(sentences) >= 69:
        sample_sentences = sentences[58:69]

        for i, sentence in enumerate(sample_sentences, start=58):
            st.write(f"{i}: {sentence}")
    else:
        st.warning("The document does not contain enough sentences.")

   
    # Step 4: Sentence chunking
    st.subheader("🔍 Semantic Sentence Chunking Output")

    chunk_df = {
        "Sentence Index": list(range(len(sentences))),
        "Sentence": sentences
    }

    st.dataframe(chunk_df, use_container_width=True)

    st.info(
        "NLTK sentence tokenizer divides unstructured text into meaningful "
        "sentence-level chunks for semantic analysis."
    )
