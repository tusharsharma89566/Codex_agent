import streamlit as st
from app import CodingChatbot
from code_executor import SafeCodeExecutor
import re

class EnhancedCodingChatbot(CodingChatbot):
    def __init__(self):
        super().__init__()
        self.code_executor = SafeCodeExecutor()
    
    def extract_code_blocks(self, text: str):
        """Extract code blocks from markdown text"""
        pattern = r'``````'
        matches = re.findall(pattern, text, re.DOTALL)
        return matches
    
    def answer_with_code_execution(self, question: str) -> str:
        """Generate answer and execute any code if requested"""
        response = self.answer_question(question)
        
        # Check if user wants code execution
        if "run" in question.lower() or "execute" in question.lower():
            code_blocks = self.extract_code_blocks(response)
            
            if code_blocks:
                response += "\n\n### Code Execution Results:\n"
                for lang, code in code_blocks:
                    if lang and code.strip():
                        result = self.code_executor.execute_code(code, lang)
                        response += f"\n**{lang.upper()} Output:**\n"
                        if result["success"]:
                            response += f"``````"
                        else:
                            response += f"``````"
        
        return response

def main():
    st.set_page_config(
        page_title="Enhanced Coding Tutor",
        page_icon="🚀",
        layout="wide"
    )
    
    st.title("🚀 Enhanced AI Coding Tutor")
    st.markdown("Upload PDFs, ask questions, and execute code - all for free!")
    
    # Initialize enhanced chatbot
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = EnhancedCodingChatbot()
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Sidebar
    with st.sidebar:
        st.header("🛠️ Features")
        st.markdown("""
        ✅ **Free & Local**: No API costs
        ✅ **PDF Training**: Upload your materials
        ✅ **Code Execution**: Run Python, Java, C++, JS
        ✅ **Multi-language**: Support for major languages
        ✅ **Safe Environment**: Isolated code execution
        """)
        
        st.header("📚 Upload Training PDFs")
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type="pdf",
            accept_multiple_files=True
        )
        
        if uploaded_files and st.button("🔄 Process PDFs"):
            with st.spinner("Processing..."):
                text_chunks = st.session_state.chatbot.process_pdfs(uploaded_files)
                st.session_state.chatbot.create_vector_store(text_chunks)
                st.session_state.chatbot.setup_qa_chain()
                st.success("✅ PDFs processed!")
    
    # Main interface
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask anything about coding..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                response = st.session_state.chatbot.answer_with_code_execution(prompt)
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()

