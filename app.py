import os
import json
import streamlit as st
from PIL import Image
from google import genai
from google.genai import types

# Page Config
st.set_page_config(
    page_title="TTB AI Label Verification Prototype",
    page_icon="🍾",
    layout="wide"
)

# Initialize Gemini Client (expects GEMINI_API_KEY in environment or Streamlit secrets)
api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", None)

if not api_key:
    st.warning("⚠️ No Gemini API Key found. Please enter your API key below or set it in your environment variables.")
    api_key = st.text_input("Gemini API Key", type="password")

st.title("🍾 TTB AI-Powered Alcohol Label Verification")
st.markdown("*Prototype built for the Compliance Division — Fast, reliable compliance screening with human-in-the-loop judgment.*")

if not api_key:
    st.stop()

client = genai.Client(api_key=api_key)

# Sidebar controls
st.sidebar.header("Workflow Options")
mode = st.sidebar.radio("Select Mode", ["Single Label Verification", "Batch Upload (Queue)"])

# Prompt Engineering for TTB Compliance
VERIFICATION_PROMPT = """
You are an expert TTB (Alcohol and Tobacco Tax and Trade Bureau) compliance officer.
Analyze the provided alcohol beverage label image and compare it against the provided application form data.

Application Form Data provided by applicant:
- Brand Name: {brand_name}
- Class/Type: {class_type}
- Alcohol Content (ABV): {abv}
- Net Contents: {net_contents}

Perform the following checks and return valid JSON:
1. extracted_brand: Brand name found on the label.
2. extracted_class: Class/type designation found on the label.
3. extracted_abv: Alcohol content found on the label.
4. extracted_net: Net contents found on the label.
5. brand_match: boolean (true if matches semantically, accounting for minor punctuation/casing differences like 'STONE'S THROW' vs 'Stone\'s Throw').
6. abv_match: boolean (true if ABV matches).
7. warning_check: object containing:
   - present (boolean: is the government warning present?)
   - exact_wording (boolean: does it closely follow statutory warning language?)
   - uppercase_bold_prefix (boolean: is 'GOVERNMENT WARNING:' formatted correctly in uppercase/prominent text?)
8. overall_status: "APPROVED", "FLAGGED", or "REJECTED"
9. compliance_notes: Detailed explanation of any discrepancies, warnings, or human review recommendations for senior agents like Dave or Jenny.
"""

if mode == "Single Label Verification":
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("1. Application Form Data")
        form_brand = st.text_input("Brand Name", value="OLD TOM DISTILLERY")
        form_class = st.text_input("Class/Type Designation", value="Kentucky Straight Bourbon Whiskey")
        form_abv = st.text_input("Alcohol Content (ABV)", value="45% Alc./Vol. (90 Proof)")
        form_net = st.text_input("Net Contents", value="750 mL")

        st.subheader("2. Upload Label Artwork")
        uploaded_file = st.file_uploader("Choose label image (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])

    with col2:
        st.subheader("3. Verification Results")
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Submitted Label Artwork", use_container_width=True)

            if st.button("Run AI Compliance Check (~2s)", type="primary"):
                with st.spinner("Analyzing label typography, layout, and statutory warnings..."):
                    try:
                        formatted_prompt = VERIFICATION_PROMPT.format(
                            brand_name=form_brand,
                            class_type=form_class,
                            abv=form_abv,
                            net_contents=form_net
                        )

                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=[image, formatted_prompt],
                            config=types.GenerateContentConfig(
                                response_mime_type="application/json"
                            )
                        )

                        result = json.loads(response.text)

                        # Display Results clearly for agents
                        status = result.get("overall_status", "FLAGGED")
                        if status == "APPROVED":
                            st.success(f"Status: {status}")
                        else:
                            st.error(f"Status: {status} - Discrepancies Found")

                        # Metrics breakdown
                        m1, m2, m3 = st.columns(3)
                        m1.metric("Brand Match", "Pass" if result.get("brand_match") else "Mismatch", 
                                  delta=f"Found: {result.get('extracted_brand')}")
                        m2.metric("ABV Match", "Pass" if result.get("abv_match") else "Mismatch",
                                  delta=f"Found: {result.get('extracted_abv')}")
                        
                        warning_ok = result.get("warning_check", {}).get("present") and result.get("warning_check", {}).get("uppercase_bold_prefix")
                        m3.metric("Govt Warning", "Valid" if warning_ok else "Review Required")

                        with st.expander("Detailed Compliance Notes & AI Reasoning", expanded=True):
                            st.write(result.get("compliance_notes"))
                            st.json(result)

                    except Exception as e:
                        st.error(f"Error processing image with AI model: {e}")
        else:
            st.info("Please upload a label image on the left to begin verification.")

else:
    st.subheader("Batch Upload Queue (Importers)")
    st.markdown("Upload multiple label images simultaneously to process peak-season backlogs.")
    batch_files = st.file_uploader("Upload Label Batch", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

    if batch_files:
        st.write(f"Loaded **{len(batch_files)}** labels into review queue.")
        if st.button("Process Batch Queue"):
            progress_bar = st.progress(0)
            results_data = []

            for i, file in enumerate(batch_files):
                img = Image.open(file)
                # Quick scan simulation / execution
                prompt = "Verify this alcohol label for basic TTB compliance (Brand name, ABV, Government Warning presence). Return JSON with fields: filename, brand_found, warning_valid, status ('APPROVED' or 'FLAGGED')."
                
                resp = client.models.generate_content(
                    model='gemini-3.8-flash',
                    contents=[img, prompt],
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                res_json = json.loads(resp.text)
                res_json["filename"] = file.name
                results_data.append(res_json)
                progress_bar.progress((i + 1) / len(batch_files))

            st.success("Batch processing complete!")
            st.table(results_data)