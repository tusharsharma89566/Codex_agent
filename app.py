import streamlit as st
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
import PyPDF2
import tempfile
from typing import List

class CodingChatbot:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        self.vector_store = None
        self.qa_chain = None
        self.setup_llm()
    
    def setup_llm(self):
        """Initialize the Gemini LLM"""
        try:
            # Initialize the ChatGoogleGenerativeAI model
            self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=st.secrets["GEMINI_API_KEY"])
        except Exception as e:
            st.error(f"Error loading model: {e}")
            self.llm = None
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from uploaded PDF"""
        text = ""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        except Exception as e:
            st.error(f"Error reading PDF: {e}")
        return text
    
    def process_pdfs(self, pdf_files) -> List[str]:
        """Process multiple PDF files and return text chunks"""
        all_text = ""
        for pdf_file in pdf_files:
            text = self.extract_text_from_pdf(pdf_file)
            all_text += f"\n\n--- {pdf_file.name} ---\n\n{text}"
        
        # Split text into chunks
        chunks = self.text_splitter.split_text(all_text)
        return chunks
    
    def create_vector_store(self, text_chunks: List[str]):
        """Create vector store from text chunks"""
        if text_chunks:
            self.vector_store = Chroma.from_texts(
                texts=text_chunks,
                embedding=self.embeddings,
                persist_directory="./chroma_db"
            )
            self.vector_store.persist()
    
    def setup_qa_chain(self):
        """Setup the question-answering chain"""
        if self.vector_store and self.llm:
            retriever = self.vector_store.as_retriever(
                search_kwargs={"k": 3}
            )
            
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True
            )
    
    def get_coding_prompt(self, question: str) -> str:
        """Enhanced prompt for coding-specific responses"""
        coding_prompt = f"""
        You are a specialized coding tutor assistant. Answer the following coding question
        based on the provided context. If the question involves code:
        
        1. Provide clear, well-commented code examples
        2. Explain the logic step by step
        3. Mention best practices and potential pitfalls
        4. Include multiple programming languages if relevant
        5. Reference the training materials when applicable
        
        Question: {question}
        
        Provide a comprehensive answer focusing on coding concepts and practical implementation.
        """
        return coding_prompt
    
    def answer_question(self, question: str) -> str:
        """Generate answer to user question"""
        try:
            if self.qa_chain:
                # Use the QA chain if it has been initialized
                enhanced_question = self.get_coding_prompt(question)
                result = self.qa_chain({"query": enhanced_question})
                return result["result"]
            elif self.llm:
                # Otherwise, use the LLM directly for general questions
                return self.llm.invoke(question).content
            else:
                return "The language model is not available. Please check your API key."
        except Exception as e:
            return f"Error generating response: {e}"

def main():
    st.set_page_config(
        page_title="Coding Tutor Chatbot",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 AI Coding Tutor Chatbot")
    st.markdown("Upload your coding PDFs and ask programming questions!")
    
    # Initialize chatbot
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = CodingChatbot()
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Sidebar for PDF upload
    with st.sidebar:
        st.header("📚 Training Materials")
        
        uploaded_files = st.file_uploader(
            "Upload PDF files",
            type="pdf",
            accept_multiple_files=True,
            help="Upload coding textbooks, tutorials, or reference materials"
        )
        
        if uploaded_files and st.button("Process PDFs"):
            with st.spinner("Processing PDFs..."):
                text_chunks = st.session_state.chatbot.process_pdfs(uploaded_files)
                st.session_state.chatbot.create_vector_store(text_chunks)
                st.session_state.chatbot.setup_qa_chain()
                st.success(f"Processed {len(uploaded_files)} PDF(s) successfully!")
        
        st.markdown("---")
        st.markdown("### 💡 Example Questions")
        st.markdown("""
        - "How do I implement a binary search algorithm?"
        - "Explain object-oriented programming concepts"
        - "What are the differences between Python lists and tuples?"
        - "Help me debug this code: [paste your code]"
        """)
    
    # Main chat interface
    st.header("💬 Chat Interface")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask your coding question..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.chatbot.answer_question(prompt)
                st.markdown(response)
        
        # Add assistant response
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Footer
    st.markdown("---")
    st.markdown("Built with ❤️ using Streamlit, LangChain, and GPT4All")

if __name__ == "__main__":
    main()
