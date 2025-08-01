# app.py
import os
import tempfile
import pickle
import time
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

# Configure Tesseract path for Windows
def check_tesseract_installation():
    """Check if Tesseract is properly configured"""
    if os.name == 'nt':  # Windows
        tesseract_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
        ]
        
        for path in tesseract_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                return True
        
        # If not found in standard locations, try to find it in PATH
        try:
            import subprocess
            result = subprocess.run(['tesseract', '--version'], 
                                    capture_output=True, text=True)
            if result.returncode == 0:
                return True
        except FileNotFoundError:
            pass
        
        return False
    else:
        # For non-Windows systems, assume it's in PATH
        try:
            import subprocess
            result = subprocess.run(['tesseract', '--version'], 
                                    capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

def check_bengali_support():
    """Check if Bengali language pack is installed"""
    try:
        import subprocess
        if os.name == 'nt':
            cmd = [pytesseract.pytesseract.tesseract_cmd, '--list-langs']
        else:
            cmd = ['tesseract', '--list-langs']
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return 'ben' in result.stdout
        return False
    except Exception:
        return False

# Initialize models
@st.cache_resource
def load_embedding_model():
    return SentenceTransformer("sentence-transformers/paraphrase-multilingual-mpnet-base-v2")

def extract_text_from_pdf(pdf_path):
    """Extract Bangla text from PDF using OCR"""
    try:
        images = convert_from_path(pdf_path, dpi=300)
        full_text = ""
        
        with st.spinner("Extracting text from PDF..."):
            progress_bar = st.progress(0)
            for i, image in enumerate(images):
                try:
                    text = pytesseract.image_to_string(image, config='--oem 3 --psm 6 -l ben')
                    full_text += text + "\n\n"
                except pytesseract.TesseractError as e:
                    if 'ben' in str(e):
                        st.error("⚠️ Bengali language data not found for Tesseract!")
                        st.markdown("""
                        **To fix this issue:**
                        1. Run the provided script as Administrator: `install_bengali_lang.ps1`
                        2. Or manually download Bengali language data from: https://github.com/tesseract-ocr/tessdata/raw/main/ben.traineddata
                        3. Place it in: `C:\\Program Files\\Tesseract-OCR\\tessdata\\ben.traineddata`
                        4. Restart your application
                        """)
                        st.stop()
                    else:
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
    cache_dir = "cache"
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, f"{os.path.basename(pdf_path)}.pkl")
    
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

def main():
    """Main Streamlit application"""
    # Set page config
    st.set_page_config(page_title="Bangla PDF QA", page_icon="📄", layout="wide")
    st.title("📄 Bangla PDF Question Answering System")

    # Check Tesseract installation
    if not check_tesseract_installation():
        st.error("⚠️ Tesseract OCR is not installed or not found!")
        st.markdown("""
        **To fix this issue:**
        1. Install Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki
        2. Or run this command in PowerShell as Administrator:
           ```
           winget install UB-Mannheim.TesseractOCR
           ```
        3. Restart your application after installation
        """)
        st.stop()

    # Check Bengali language support
    if not check_bengali_support():
        st.error("⚠️ Bengali language data not found for Tesseract!")
        st.markdown("""
        **To enable Bengali OCR support:**
        1. Run the provided script as Administrator: `install_bengali_lang.ps1`
        2. Or manually:
           - Download: https://github.com/tesseract-ocr/tessdata/raw/main/ben.traineddata
           - Place it in: `C:\\Program Files\\Tesseract-OCR\\tessdata\\ben.traineddata`
        3. Restart your application
        
        **Note:** You can also try with English OCR for testing (change TESSERACT_CONFIG to '--oem 3 --psm 6 -l eng')
        """)
        st.stop()

    # Configuration
    DATA_DIR = "data"
    PDF_NAME = "bangla_document.pdf"  
    PDF_PATH = os.path.join(DATA_DIR, PDF_NAME)

    # Create directories if missing
    os.makedirs(DATA_DIR, exist_ok=True)

    # Sidebar configuration
    st.sidebar.header("Configuration")
    openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key
    else:
        st.sidebar.warning("Enter OpenAI API key to enable GPT-4o")

    # Main processing
    if not os.path.exists(PDF_PATH):
        st.warning(f"PDF not found at: {PDF_PATH}")
        st.info(f"Please place your Bangla PDF in the '{DATA_DIR}' folder as '{PDF_NAME}'")
        st.stop()

    embedding_model = load_embedding_model()
    chunks, index = process_pdf(PDF_PATH, embedding_model)

    # Query interface
    st.subheader("Ask questions about the document")
    question = st.text_input("Enter your question in Bangla:", "")

    if question and openai_api_key:
        # Embed question
        question_embedding = embedding_model.encode([question])
        
        # Search index
        D, I = index.search(question_embedding, k=3)
        context = "\n\n".join([chunks[i] for i in I[0]])
        
        # Build prompt
        prompt = f"""
        নিচের প্রসঙ্গ ব্যবহার করে প্রশ্নের উত্তর দাও:
        
        প্রসঙ্গ:
        {context}
        
        প্রশ্ন: {question}
        উত্তর:
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

if __name__ == "__main__":
    main()