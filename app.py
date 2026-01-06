import streamlit as st
from markitdown import MarkItDown
import os
import io

# Initialize MarkItDown Engine
# Note: MarkItDown handles docx, xlsx, pptx, pdf, and html automatically.
mid = MarkItDown()

# Page Configuration
st.set_page_config(page_title="Universal Document Reader", page_icon="📄")

def main():
    st.title("📄 Universal Document Reader")
    st.markdown("Convert your Office docs, PDFs, and HTML files into clean Markdown instantly.")

    # [2] Interface: Upload Area
    uploaded_files = st.file_uploader(
        "Upload files (Word, Excel, PPT, PDF, HTML)", 
        type=['docx', 'xlsx', 'pptx', 'pdf', 'html', 'htm'],
        accept_multiple_files=True
    )

    if uploaded_files:
        all_converted_text = ""
        
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            file_extension = os.path.splitext(file_name)[1].lower()
            
            # [3] Resilience: Error Handling
            try:
                # To process with MarkItDown, we save to a temp location or pass bytes
                # MarkItDown's convert method works well with file paths or streams
                with st.spinner(f"Processing {file_name}..."):
                    # We pass the file stream to MarkItDown
                    # Some MarkItDown versions prefer a path; streamlit's UploadedFile 
                    # can be handled by creating a temporary file if needed.
                    result = mid.convert(uploaded_file)
                    content = result.text_content
                    
                    # Store content for preview
                    all_converted_text += f"## Source: {file_name}\n\n{content}\n\n---\n\n"
                    
                    st.success(f"✅ Successfully processed: {file_name}")

            except Exception as e:
                st.error(f"⚠️ Could not read {file_name}. Please check the format.")
                # Log error for developer visibility in console
                print(f"Error processing {file_name}: {e}")

        # [2] Interface: Instant Preview
        if all_converted_text:
            st.subheader("Preview")
            st.text_area(
                label="Converted Content",
                value=all_converted_text,
                height=400
            )

            # [2] & [4] Download Options and Naming Logic
            st.subheader("Download Results")
            col1, col2 = st.columns(2)

            # Prepare file name logic: use the first file's name as a base
            base_name = os.path.splitext(uploaded_files[0].name)[0]
            
            with col1:
                st.download_button(
                    label="Download as Markdown (.md)",
                    data=all_converted_text,
                    file_name=f"{base_name}_converted.md",
                    mime="text/markdown"
                )
            
            with col2:
                st.download_button(
                    label="Download as Text (.txt)",
                    data=all_converted_text,
                    file_name=f"{base_name}_converted.txt",
                    mime="text/plain"
                )

if __name__ == "__main__":
    main()
