import streamlit as st
from app import CodingChatbot
from enchance_app import EnhancedCodingChatbot

def run_basic_chatbot():
    st.title("🤖 AI Coding Tutor Chatbot")
    st.markdown("Upload your coding PDFs and ask programming questions!")
    
    if 'chatbot_basic' not in st.session_state:
        st.session_state.chatbot_basic = CodingChatbot()
    
    if 'messages_basic' not in st.session_state:
        st.session_state.messages_basic = []
    
    with st.sidebar:
        st.header("📚 Training Materials")
        uploaded_files = st.file_uploader(
            "Upload PDF files",
            type="pdf",
            accept_multiple_files=True,
            help="Upload coding textbooks, tutorials, or reference materials"
        )
        if uploaded_files and st.button("Process PDFs", key="process_basic"):
            with st.spinner("Processing PDFs..."):
                text_chunks = st.session_state.chatbot_basic.process_pdfs(uploaded_files)
                st.session_state.chatbot_basic.create_vector_store(text_chunks)
                st.session_state.chatbot_basic.setup_qa_chain()
                st.success(f"Processed {len(uploaded_files)} PDF(s) successfully!")
        
        st.markdown("---")
        st.markdown("### 💡 Example Questions")
        st.markdown("""
        - "How do I implement a binary search algorithm?"
        - "Explain object-oriented programming concepts"
        - "What are the differences between Python lists and tuples?"
        - "Help me debug this code: [paste your code]"
        """)
    
    st.header("💬 Chat Interface")
    for message in st.session_state.messages_basic:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask your coding question..."):
        st.session_state.messages_basic.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.chatbot_basic.answer_question(prompt)
                st.markdown(response)
        
        st.session_state.messages_basic.append({"role": "assistant", "content": response})

def run_enhanced_chatbot():
    st.title("🚀 Enhanced AI Coding Tutor")
    st.markdown("Upload PDFs, ask questions, and execute code - all for free!")
    
    if 'chatbot_enhanced' not in st.session_state:
        st.session_state.chatbot_enhanced = EnhancedCodingChatbot()
    
    if 'messages_enhanced' not in st.session_state:
        st.session_state.messages_enhanced = []
    
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
        
        if uploaded_files and st.button("🔄 Process PDFs", key="process_enhanced"):
            with st.spinner("Processing..."):
                text_chunks = st.session_state.chatbot_enhanced.process_pdfs(uploaded_files)
                st.session_state.chatbot_enhanced.create_vector_store(text_chunks)
                st.session_state.chatbot_enhanced.setup_qa_chain()
                st.success("✅ PDFs processed!")
    
    for message in st.session_state.messages_enhanced:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask anything about coding..."):
        st.session_state.messages_enhanced.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                response = st.session_state.chatbot_enhanced.answer_with_code_execution(prompt)
                st.markdown(response)
        
        st.session_state.messages_enhanced.append({"role": "assistant", "content": response})

def main():
    st.set_page_config(
        page_title="Unified AI Coding Tutor",
        page_icon="🤖🚀",
        layout="wide"
    )
    
    tab = st.sidebar.radio("Select Mode", ["Basic Coding Tutor", "Enhanced Coding Tutor"])
    
    if tab == "Basic Coding Tutor":
        run_basic_chatbot()
    else:
        run_enhanced_chatbot()

if __name__ == "__main__":
    main()
