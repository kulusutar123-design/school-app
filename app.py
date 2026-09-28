import streamlit as st

# ପୃଷ୍ଠା ସେଟିଂସ୍ (Wide layout)
st.set_page_config(page_title="School Home Portal", page_icon="🏫", layout="wide")

# index.html ଫାଇଲ୍‌କୁ ପଢ଼ି ସିଧାସଳଖ ଡ୍ୟାସ୍‌ବୋର୍ଡରେ ଦେଖାଇବା
try:
    with open("index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    st.components.v1.html(html_content, height=900, scrolling=True)
except FileNotFoundError:
    st.error("index.html ଫାଇଲ୍ ମିଳିଲା ନାହିଁ।")
