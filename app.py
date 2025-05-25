import streamlit as st
import qrcode
import os
import zipfile
import tempfile
import pandas as pd
from PIL import Image, ImageDraw
import numpy as np
import cv2
import io
import base64
import datetime
import webbrowser

# ------------------- Config ------------------- #
st.set_page_config(
    page_title="Ultimate QR Generator Pro",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://example.com/help',
        'About': "### Advanced QR Generator for Students, Vendors, Businesses, and More"
    }
)

MODES = ["Student Profile", "Vendor Solution", "Bulk Generator", "QR Scanner"]

if 'current_mode' not in st.session_state:
    st.session_state.current_mode = MODES[0]
if 'qr_img' not in st.session_state:
    st.session_state.qr_img = None

# ------------------- Utility Functions ------------------- #
def generate_qr(data, logo=None, fg_color="black", bg_color="white", size=600):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color=fg_color, back_color=bg_color).convert("RGBA")
    qr_img = qr_img.resize((size, size))

    if logo:
        logo_img = Image.open(logo).convert("RGBA")
        logo_size = size // 4
        logo_img = logo_img.resize((logo_size, logo_size))

        mask = Image.new("L", (logo_size, logo_size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, logo_size, logo_size), fill=255)

        pos = ((size - logo_size) // 2, (size - logo_size) // 2)
        qr_img.paste(logo_img, pos, mask)

    return qr_img

def scan_qr(uploaded_image):
    img = Image.open(uploaded_image)
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    detector = cv2.QRCodeDetector()
    data, vertices, _ = detector.detectAndDecode(img_cv)

    if vertices is not None:
        pts = vertices.astype(int).reshape(-1, 2)
        for i in range(len(pts)):
            cv2.line(img_cv, tuple(pts[i]), tuple(pts[(i+1) % len(pts)]), (0, 255, 0), 3)
        img_with_box = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
        return data, img_with_box
    return None, img

def get_image_download_link(img, filename, text):
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:file/png;base64,{img_str}" download="{filename}">{text}</a>'
    return href

# ------------------- Page Functions ------------------- #
def student_profile():
    st.header("🎓 Student QR Profile Generator")
    with st.form("student_form"):
        col1, col2 = st.columns(2)
        with col1:
            prn = st.text_input("PRN Number*", help="Unique student identification number")
            name = st.text_input("Full Name*")
            department = st.text_input("Department*")
        with col2:
            division = st.text_input("Division")
            year = st.text_input("Academic Year*")
            contact = st.text_input("Contact Number")
        submitted = st.form_submit_button("Generate Student QR")

        if submitted:
            if not all([prn, name, department, year]):
                st.error("Please fill all required fields (*)")
            else:
                data = f"STUDENT PROFILE\nPRN: {prn}\nName: {name}\nDepartment: {department}\nDivision: {division}\nYear: {year}\nContact: {contact}\nGenerated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
                st.session_state.qr_img = generate_qr(data, size=600)
                st.success("Student QR generated successfully!")

def vendor_solution():
    st.header("🏪 Vendor QR Solution")
    mode = st.radio("Select QR Type:", ["Business Profile", "Digital Menu", "Payment QR", "Analytics"], horizontal=True)

    if mode == "Business Profile":
        with st.form("vendor_form"):
            col1, col2 = st.columns(2)
            with col1:
                business_name = st.text_input("Business Name*")
                owner_name = st.text_input("Owner Name*")
                contact = st.text_input("Contact Number*")
            with col2:
                location = st.text_input("Location*")
                specialty = st.text_input("Specialty/Products")
                social_media = st.text_input("Social Media Handle")
            submitted = st.form_submit_button("Generate Business QR")

            if submitted:
                if not all([business_name, owner_name, contact, location]):
                    st.error("Please fill all required fields (*)")
                else:
                    data = f"BUSINESS PROFILE\nName: {business_name}\nOwner: {owner_name}\nContact: {contact}\nLocation: {location}\nSpecialty: {specialty}\nSocial: {social_media}\nGenerated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
                    st.session_state.qr_img = generate_qr(data, size=600)
                    st.success("Business QR generated successfully!")

    elif mode == "Digital Menu":
        menu_items = st.text_area("Enter your menu items (one per line):", height=200)
        if st.button("Generate Menu QR"):
            if not menu_items.strip():
                st.error("Please enter menu items")
            else:
                data = f"DIGITAL MENU\n{menu_items}\nGenerated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
                st.session_state.qr_img = generate_qr(data, size=600)
                st.success("Menu QR generated successfully!")

    elif mode == "Payment QR":
        col1, col2 = st.columns(2)
        with col1:
            upi = st.checkbox("UPI")
            paytm = st.checkbox("Paytm")
            phonepe = st.checkbox("PhonePe")
            gpay = st.checkbox("Google Pay")
            cash = st.checkbox("Cash")
        with col2:
            upi_id = st.text_input("UPI ID")

        if st.button("Generate Payment QR"):
            if (upi or paytm or phonepe or gpay) and not upi_id.strip():
                st.error("Please enter UPI ID for digital payments")
            else:
                data = "PAYMENT OPTIONS\n"
                if upi or paytm or phonepe or gpay:
                    data += "Digital Payments Accepted:\n"
                    if upi: data += "• UPI\n"
                    if paytm: data += "• Paytm\n"
                    if phonepe: data += "• PhonePe\n"
                    if gpay: data += "• Google Pay\n"
                    data += f"\nUPI ID: {upi_id}\n"
                if cash:
                    data += "\n• Cash Payments Accepted\n"
                data += f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
                st.session_state.qr_img = generate_qr(data, size=600)
                st.success("Payment QR generated successfully!")

    elif mode == "Analytics":
        st.info("This feature would track QR code scans in a production environment")
        if st.button("Generate Analytics QR"):
            data = f"ANALYTICS TRACKING\nThis QR code would track customer interactions\nGenerated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
            st.session_state.qr_img = generate_qr(data, size=600)
            st.success("Analytics QR generated successfully!")

def bulk_generator():
    st.header("📦 Bulk QR Generator")
    upload_option = st.radio("Input Method:", ["CSV/Excel Upload", "Manual Entry"], horizontal=True)

    if upload_option == "CSV/Excel Upload":
        uploaded_file = st.file_uploader("Upload File", type=["csv", "xlsx"])
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
                st.dataframe(df.head())

                if len(df.columns) > 1:
                    content_col = st.selectbox("QR Content Column", df.columns)
                    name_col = st.selectbox("QR Name Column", [None] + list(df.columns))
                else:
                    content_col = df.columns[0]
                    name_col = None

                if st.button("Generate Bulk QR Codes"):
                    with tempfile.TemporaryDirectory() as tmpdir:
                        zip_path = os.path.join(tmpdir, "qrcodes.zip")
                        with zipfile.ZipFile(zip_path, 'w') as zipf:
                            for index, row in df.iterrows():
                                data = str(row[content_col])
                                qr_img = generate_qr(data, size=600)
                                filename = f"qr_{row[name_col]}.png" if name_col else f"qr_{index+1}.png"
                                img_path = os.path.join(tmpdir, filename)
                                qr_img.save(img_path)
                                zipf.write(img_path, filename)

                        with open(zip_path, "rb") as f:
                            st.download_button("Download QR ZIP", data=f, file_name="qrcodes.zip", mime="application/zip")
            except Exception as e:
                st.error(f"Error: {str(e)}")

    else:
        num = st.number_input("Number of QR Codes", 1, 100, 1)
        names = []
        contents = []
        for i in range(num):
            col1, col2 = st.columns([1, 4])
            with col1:
                name = st.text_input(f"Name {i+1}", key=f"name_{i}")
            with col2:
                content = st.text_input(f"Content {i+1}", key=f"content_{i}")
            names.append(name)
            contents.append(content)

        if st.button("Generate QR Codes"):
            valid_qrs = [(n, c) for n, c in zip(names, contents) if c]
            if not valid_qrs:
                st.warning("Enter at least one valid content")
            else:
                with tempfile.TemporaryDirectory() as tmpdir:
                    zip_path = os.path.join(tmpdir, "bulk_qrs.zip")
                    with zipfile.ZipFile(zip_path, 'w') as zipf:
                        for i, (name, content) in enumerate(valid_qrs):
                            qr_img = generate_qr(content, size=600)
                            filename = f"{name or i+1}.png"
                            img_path = os.path.join(tmpdir, filename)
                            qr_img.save(img_path)
                            zipf.write(img_path, filename)
                    with open(zip_path, "rb") as f:
                        st.download_button("Download Bulk QR ZIP", data=f, file_name="bulk_qr.zip", mime="application/zip")

def qr_scanner():
    st.header("🔍 QR Code Scanner")
    uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        data, processed_img = scan_qr(uploaded_file)
        col1, col2 = st.columns(2)
        with col1:
            st.image(processed_img, caption="Scanned Image")
        with col2:
            if data:
                st.success("QR Detected!")
                st.text_area("Decoded Data", data, height=200)
            else:
                st.error("No QR Code Found")

# ------------------- Main App ------------------- #
def main():
    st.title("✨ Ultimate QR Generator Pro")
    st.session_state.current_mode = st.sidebar.radio("Select Mode:", MODES, index=MODES.index(st.session_state.current_mode))

    if st.session_state.current_mode == "Student Profile":
        student_profile()
    elif st.session_state.current_mode == "Vendor Solution":
        vendor_solution()
    elif st.session_state.current_mode == "Bulk Generator":
        bulk_generator()
    elif st.session_state.current_mode == "QR Scanner":
        qr_scanner()

    if st.session_state.qr_img:
        st.sidebar.header("Generated QR Code")
        st.sidebar.image(st.session_state.qr_img, width=300)
        st.sidebar.markdown(get_image_download_link(st.session_state.qr_img, "qr_code.png", "⬇ Download QR Code"), unsafe_allow_html=True)
        if st.sidebar.button("Save QR to Disk"):
            folder = "saved_qr_codes"
            os.makedirs(folder, exist_ok=True)
            path = os.path.join(folder, f"qr_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            st.session_state.qr_img.save(path)
            st.sidebar.success(f"Saved to: {path}")
            webbrowser.open(os.path.abspath(folder))

if __name__ == "__main__":
    main()
