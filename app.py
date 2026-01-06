import streamlit as st
from markitdown import MarkItDown
import os
import tempfile
import io
from pdfminer.high_level import extract_text

# Initialize MarkItDown Engine
mid = MarkItDown()

st.set_page_config(page_title="Universal Document Reader", page_icon="📄", layout="wide")

def get_file_size(size_in_bytes):
    """Converts bytes to a human-readable string (MB)."""
    return round(size_in_bytes / (1024 * 1024), 2)

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
        total_original_size = 0
        
        # We'll use tabs to separate the Preview and the Analytics
        tab1, tab2 = st.tabs(["📄 Conversion & Preview", "📊 File Size Comparison"])

        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            file_ext = os.path.splitext(file_name)[1].lower()
            original_size = uploaded_file.size
            total_original_size += original_size
            
            try:
                with st.spinner(f"Processing {file_name}..."):
                    # Create a temporary file to ensure engine stability
                    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name

                    try:
                        # Primary Engine: MarkItDown
                        result = mid.convert(tmp_path)
                        content = result.text_content
                    except Exception:
                        # Fallback for PDFs if MarkItDown fails
                        if file_ext == ".pdf":
                            content = extract_text(tmp_path)
                        else:
                            content = f"Error: Could not extract content from {file_name}."
                    
                    all_converted_text += f"## Source: {file_name}\n\n{content}\n\n---\n\n"
                    
                    # Cleanup
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)

            except Exception as e:
                st.error(f"⚠️ Could not read {file_name}. Please check the format.")

        # --- TAB 1: CONVERSION & PREVIEW ---
        with tab1:
            if all_converted_text:
                st.subheader("Preview")
                st.text_area("Converted Content", value=all_converted_text, height=400)

                st.subheader("Download Results")
                base_name = os.path.splitext(uploaded_files[0].name)[0]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="Download Markdown (.md)", 
                        data=all_converted_text, 
                        file_name=f"{base_name}_converted.md",
                        mime="text/markdown"
                    )
                with col2:
                    st.download_button(
                        label="Download Text (.txt)", 
                        data=all_converted_text, 
                        file_name=f"{base_name}_converted.txt",
                        mime="text/plain"
                    )

        # --- TAB 2: FILE SIZE COMPARISON ---
        with tab2:
            if all_converted_text:
                converted_bytes = len(all_converted_text.encode('utf-8'))
                
                orig_mb = get_file_size(total_original_size)
                conv_mb = get_file_size(converted_bytes)
                
                # Handling edge case: if file is so small it rounds to 0.00
                display_conv_mb = conv_mb if conv_mb > 0 else "< 0.01"
                
                # Calculate percentage reduction
                if total_original_size > 0:
                    reduction = ((total_original_size - converted_bytes) / total_original_size) * 100
                else:
                    reduction = 0

                st.subheader("Efficiency Metrics")
                
                # Display metrics table
                st.table([
                    {"Metric": "Original File(s) Size", "Value": f"{orig_mb} MB"},
                    {"Metric": "Converted Text Size", "Value": f"{display_conv_mb} MB"}
                ])

                # Highlight the reduction
                st.success(f"💡 **Optimization Result:** Text version is **{reduction:.1f}%** smaller than the original.")
                
                # Visual bar for comparison
                st.progress(min(int(reduction), 100))

if __name__ == "__main__":
    main()
