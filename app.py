import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from api.scan import scan_and_answer_file

st.title("AI Document Q&A Bot")
st.write("Upload a text file containing questions, and the AI will find and answer them for you!")

uploaded_file = st.file_uploader("Choose a .txt file", type=["txt"])

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    file_text = file_bytes.decode("utf-8")
    
    with st.expander("Preview uploaded file text"):
        st.text(file_text[:1000] + "..." if len(file_text) > 1000 else file_text)

    if st.button("Scan and Answer Questions"):
        with st.spinner("Scanning document and generating answers..."):
            results = scan_and_answer_file(file_text)

        st.success(f"Scan complete! Found and answered {len(results)} genuine questions.")
        
        for item in results:
            st.markdown(f"### ❓ Question: {item['question']}")
            st.markdown(f"**Answer:**")
            st.markdown(item['answer'])
            st.markdown("---")