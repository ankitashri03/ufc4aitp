import streamlit as st
from markitdown import MarkItDown
import os
import tempfile

# Initialize MarkItDown Engine
mid = MarkItDown()

st.set_page_config(page_title="Universal Document Reader", page_icon="📄")

def main():
    st.title("📄 Universal Document Reader")
    st.markdown("Convert Office docs, PDFs, and HTML into clean Markdown.")

    uploaded_files = st.file_uploader(
        "Upload files", 
        type=['docx', 'xlsx', 'pptx', 'pdf', 'html', 'htm'],
        accept_multiple_files=True
    )

    if uploaded_files:
        all_converted_text = ""
        
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            
            try:
                with st.spinner(f"Processing {file_name}..."):
                    # FIX: Save the uploaded bytes to a temporary file
                    # MarkItDown performs better when it has a physical file path
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[1]) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name

                    # Process the temporary file
                    result = mid.convert(tmp_path)
                    content = result.text_content
                    
                    all_converted_text += f"## Source: {file_name}\n\n{content}\n\n---\n\n"
                    st.success(f"✅ Processed: {file_name}")
                    
                    # Cleanup temporary file
                    os.remove(tmp_path)

            except Exception as e:
                st.error(f"⚠️ Could not read {file_name}. Please check the format.")
                st.info(f"Technical Error: {e}") # This helps debug the specific issue

        if all_converted_text:
            st.subheader("Preview")
            st.text_area("Converted Content", value=all_converted_text, height=400)

            st.subheader("Download Results")
            base_name = os.path.splitext(uploaded_files[0].name)[0]
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button("Download Markdown (.md)", all_converted_text, f"{base_name}_converted.md")
            with col2:
                st.download_button("Download Text (.txt)", all_converted_text, f"{base_name}_converted.txt")

if __name__ == "__main__":
    main()
