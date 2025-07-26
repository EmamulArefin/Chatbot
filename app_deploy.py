# app_deploy.py - Cloud deployment version
import os
import tempfile
import pickle
import time
import subprocess
import urllib.request
from dotenv import load_dotenv
import streamlit as st
from pdf2image import convert_from_path
import pytesseract
from sentence_transformers import SentenceTransformer
import faiss
import openai
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load environment variables
load_dotenv()

# Configure Tesseract for cloud deployment
def setup_tesseract():
    """Setup Tesseract for cloud deployment"""
    if os.name == 'posix':  # Linux/Unix systems (like Streamlit Cloud)
        # Download Bengali language data if not exists
        tessdata_dir = "/usr/share/tesseract-ocr/4.00/tessdata/"
        if not os.path.exists(tessdata_dir):
            tessdata_dir = "/usr/share/tesseract-ocr/tessdata/"
        
        ben_path = os.path.join(tessdata_dir, "ben.traineddata")
        
        if not os.path.exists(ben_path):
            try:
                # Download Bengali language data
                url = "https://github.com/tesseract-ocr/tessdata/raw/main/ben.traineddata"
                with st.spinner("Downloading Bengali language data..."):
                    urllib.request.urlretrieve(url, ben_path)
                st.success("Bengali language data downloaded successfully!")
            except Exception as e:
                st.warning(f"Could not download Bengali data: {e}")
                return False
        return True
    else:
        # Windows deployment (local)
        tesseract_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
        ]
        
        for path in tesseract_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                return True
        return False

def check_tesseract_installation():
    """Check if Tesseract is properly configured"""
    try:
        result = subprocess.run(['tesseract', '--version'], 
                                capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except Exception:
        return False

def check_bengali_support():
    """Check if Bengali language pack is installed"""
    try:
        result = subprocess.run(['tesseract', '--list-langs'], 
                                capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return 'ben' in result.stdout
        return False
    except Exception:
        return False

# Initialize Tesseract
if not setup_tesseract():
    st.error("⚠️ Could not setup Tesseract OCR!")
    st.stop()

# Check Tesseract installation
TESSERACT_AVAILABLE = check_tesseract_installation()

if not TESSERACT_AVAILABLE:
    st.error("⚠️ Tesseract OCR is not available!")
    st.markdown("""
    **For cloud deployment:** Tesseract should be automatically installed.
    
    **For local deployment:** 
    1. Install Tesseract OCR
    2. Run the `install_bengali_lang.ps1` script
    """)
    st.stop()

# Check Bengali language support
BENGALI_AVAILABLE = check_bengali_support()

if not BENGALI_AVAILABLE:
    st.warning("⚠️ Bengali language data not found! Attempting to download...")
    if setup_tesseract():
        BENGALI_AVAILABLE = check_bengali_support()
    
    if not BENGALI_AVAILABLE:
        st.error("⚠️ Could not enable Bengali OCR support!")
        st.markdown("""
        **Note:** You can try with English OCR for testing by changing the language configuration.
        """)
        # Fall back to English
        TESSERACT_CONFIG = '--oem 3 --psm 6 -l eng'
        st.info("🔄 Falling back to English OCR...")
    else:
        TESSERACT_CONFIG = '--oem 3 --psm 6 -l ben'
        st.success("✅ Bengali OCR support enabled!")
else:
    TESSERACT_CONFIG = '--oem 3 --psm 6 -l ben'

# Configuration
DATA_DIR = "data"
CACHE_DIR = "cache"
PDF_NAME = "bangla_document.pdf"  
PDF_PATH = os.path.join(DATA_DIR, PDF_NAME)
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

# Create directories if missing
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

# Initialize models
@st.cache_resource
def load_embedding_model():
    return SentenceTransformer(MODEL_NAME)

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using OCR"""
    try:
        images = convert_from_path(pdf_path, dpi=300)
        full_text = ""
        
        with st.spinner("Extracting text from PDF..."):
            progress_bar = st.progress(0)
            for i, image in enumerate(images):
                try:
                    text = pytesseract.image_to_string(image, config=TESSERACT_CONFIG)
                    full_text += text + "\n\n"
                except pytesseract.TesseractError as e:
                    st.error(f"Tesseract error: {str(e)}")
                    st.stop()
                progress_bar.progress((i + 1) / len(images))
            st.success("Text extraction complete!")
        return full_text
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        st.stop()

def process_pdf(pdf_path, model):
    """Process PDF and create embeddings"""
    cache_path = os.path.join(CACHE_DIR, f"{os.path.basename(pdf_path)}.pkl")
    
    # Check cache
    if os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            return pickle.load(f)
    
    # Process PDF
    text = extract_text_from_pdf(pdf_path)
    
    # Split text
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        length_function=len,
        separators=['\n\n', '।', '\n', ' ', '']
    )
    chunks = text_splitter.split_text(text)
    
    # Create embeddings
    with st.spinner("Creating embeddings..."):
        embeddings = model.encode(chunks, show_progress_bar=True)
    
    # Create FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    # Save to cache
    with open(cache_path, "wb") as f:
        pickle.dump((chunks, index), f)
    
    return chunks, index

def query_openai(prompt):
    """Send query to OpenAI GPT-4o"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions in Bangla."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"OpenAI Error: {str(e)}")
        return None

# Streamlit UI
st.set_page_config(page_title="Bangla PDF QA", page_icon="📄", layout="wide")
st.title("📄 Bangla PDF Question Answering System")

# Sidebar configuration
st.sidebar.header("Configuration")
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
if openai_api_key:
    os.environ["OPENAI_API_KEY"] = openai_api_key
else:
    st.sidebar.warning("Enter OpenAI API key to enable GPT-4o")

# File upload option for cloud deployment
uploaded_file = st.sidebar.file_uploader("Upload PDF Document", type="pdf")
if uploaded_file is not None:
    # Save uploaded file
    with open(PDF_PATH, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.sidebar.success("PDF uploaded successfully!")

# Main processing
if not os.path.exists(PDF_PATH):
    st.warning(f"No PDF document found!")
    st.info("Please upload a PDF document using the sidebar.")
    st.stop()

embedding_model = load_embedding_model()
chunks, index = process_pdf(PDF_PATH, embedding_model)

# Query interface
st.subheader("Ask questions about the document")
question = st.text_input("Enter your question:", "")

if question and openai_api_key:
    # Embed question
    question_embedding = embedding_model.encode([question])
    
    # Search index
    D, I = index.search(question_embedding, k=3)
    context = "\n\n".join([chunks[i] for i in I[0]])
    
    # Build prompt
    if 'ben' in TESSERACT_CONFIG:
        prompt = f"""
        নিচের প্রসঙ্গ ব্যবহার করে প্রশ্নের উত্তর দাও:
        
        প্রসঙ্গ:
        {context}
        
        প্রশ্ন: {question}
        উত্তর:
        """
    else:
        prompt = f"""
        Answer the question based on the following context:
        
        Context:
        {context}
        
        Question: {question}
        Answer:
        """
    
    # Get response
    with st.spinner("Generating answer..."):
        answer = query_openai(prompt)
    
    if answer:
        st.subheader("Answer:")
        st.success(answer)
        
        with st.expander("See context used"):
            st.text(context)

# Add footer
st.markdown("---")
st.caption("Note: First run will take time for OCR processing. Subsequent runs will use cached embeddings.")

# Show deployment info
if st.sidebar.button("ℹ️ Deployment Info"):
    st.sidebar.info(f"""
    **System Info:**
    - OS: {os.name}
    - Tesseract: {'✅' if TESSERACT_AVAILABLE else '❌'}
    - Bengali: {'✅' if BENGALI_AVAILABLE else '❌'}
    - Config: {TESSERACT_CONFIG}
    """)
