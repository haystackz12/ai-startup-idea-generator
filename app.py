import streamlit as st
from openai import OpenAI
import requests
import io
import json
import zipfile
from datetime import datetime
from PIL import Image

# ----------------- CONFIG -----------------
st.set_page_config(page_title="🚀 AI Startup Idea Generator", layout="wide")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ----------------- SESSION DEFAULTS -----------------
if "idea_data" not in st.session_state:
    st.session_state.idea_data = None
if "logo_variants" not in st.session_state:
    st.session_state.logo_variants = []
if "selected_logo_idx" not in st.session_state:
    st.session_state.selected_logo_idx = None
if "history" not in st.session_state:
    st.session_state.history = []

# ----------------- HELPERS -----------------

def call_gpt(payload: str) -> str:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a startup ideation assistant. Return ONLY valid JSON in your answer "
                    "with keys: startup_name, product_description, pitch, tagline, "
                    "light_palette (array of 3 hex strings), dark_palette (array of 3 hex strings), "
                    "mood_keywords (array of 3 words), mvp_features (array of 3-5 short strings), "
                    "scores (object with integer keys novelty, difficulty, business_potential 1-10)."
                ),
            },
            {"role": "user", "content": payload},
        ],
        temperature=0.8,
        max_tokens=700,
    )
    return resp.choices[0].message.content.strip()

def generate_startup_idea(keyword: str, industries: list[str], tweaks: str) -> dict:
    ind = ", ".join(industries)
    tweak_clause = f"Additional creative instructions: {tweaks}" if tweaks else ""
    prompt = (
        f"Keyword / Problem: '{keyword}'. Industry tags: {ind}. {tweak_clause}\n"
        "Return the JSON as specified."
    )
    raw = call_gpt(prompt)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = json.loads(call_gpt("Fix this to valid JSON only, no markdown: " + raw))
    return data

def download_image(url: str) -> Image.Image:
    r = requests.get(url)
    r.raise_for_status()
    return Image.open(io.BytesIO(r.content))

def generate_logo(name: str, primary_color: str) -> Image.Image:
    res = client.images.generate(
        model="dall-e-3",
        prompt=f"Minimalist vector logo for a startup named '{name}', primary color {primary_color}, no text, flat design",
        n=1,
        size="1024x1024",
    )
    return download_image(res.data[0].url)

def palette_swatches(colors: list[str]):
    cols = st.columns(len(colors))
    for hex_code, col in zip(colors, cols):
        col.markdown(
            f"<div style='background:{hex_code}; width:100%; padding-top:40px; border-radius:4px'></div><p style='text-align:center'>{hex_code}</p>",
            unsafe_allow_html=True,
        )

def make_zip(idea: dict, logo: Image.Image) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "idea.txt",
            f"{idea['startup_name']}\n\n{idea['product_description']}\n\nPitch:\n{idea['pitch']}\n\nTagline: {idea['tagline']}\n\nMVP Features:\n- "
            + "\n- ".join(idea["mvp_features"])
            + "\n\nScores:\n"
            + f"Novelty: {idea['scores']['novelty']}\nDifficulty: {idea['scores']['difficulty']}\nBusiness Potential: {idea['scores']['business_potential']}\n",
        )
        zf.writestr(
            "palette.json",
            json.dumps(
                {
                    "light_palette": idea["light_palette"],
                    "dark_palette": idea["dark_palette"],
                    "mood_keywords": idea["mood_keywords"],
                },
                indent=2,
            ),
        )
        zf.writestr("pitch.md", f"# {idea['startup_name']}\n\n> {idea['pitch']}")
        img_buf = io.BytesIO()
        logo.save(img_buf, format="PNG")
        zf.writestr("logo.png", img_buf.getvalue())
    buf.seek(0)
    return buf.read()

# ----------------- UI -----------------

st.sidebar.header("⚡ Quick Settings (Industry required)")
industries = st.sidebar.multiselect(
    "Industry Tags (select at least one)",
    ["AI", "Fintech", "Health", "Education", "E-commerce", "Sustainability", "Gaming", "Productivity"],
)
user_tweaks = st.sidebar.text_input("Prompt Tweaks (optional)")

st.title("🚀 AI Startup Idea Generator")
st.markdown("""
Welcome to the AI Startup Idea Generator! 💡

Here's how it works:
1. Enter a **keyword or problem** you want to solve.
2. Choose an **industry** to guide the idea.
3. Optionally, tweak the tone or style (e.g., "Make it funny" or "For Gen Z").
4. Click **Generate Idea Pack** to create:
   - A startup name
   - Pitch & tagline
   - Color palette & mood
   - MVP feature list
   - A generated logo using DALL·E
5. Click **Download Startup Pack** to export your files.
6. To start over, use the **Clear Idea** button below.
""")

keyword = st.text_input("Keyword or Problem", placeholder="e.g. remote team productivity")
col_generate, col_logo, col_clear = st.columns([1, 1, 1])

with col_generate:
    if st.button("🎉 Generate Idea Pack", use_container_width=True):
        if not industries:
            st.warning("Please select at least one Industry Tag.")
        elif not keyword.strip():
            st.warning("Please enter a keyword/problem first.")
        else:
            with st.spinner("Thinking up something brilliant…"):
                idea = generate_startup_idea(keyword, industries, user_tweaks)
                st.session_state.idea_data = idea
                logo_img = generate_logo(idea["startup_name"], idea["light_palette"][0])
                st.session_state.logo_variants = [logo_img]
                st.session_state.selected_logo_idx = 0
                st.session_state.history.append({
                    "name": idea["startup_name"],
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
                if len(st.session_state.history) > 5:
                    st.session_state.history = st.session_state.history[-5:]

with col_logo:
    if st.button("🔄 Regenerate Logo", use_container_width=True, disabled=st.session_state.idea_data is None):
        if st.session_state.idea_data:
            with st.spinner("Generating a new logo…"):
                new_logo = generate_logo(st.session_state.idea_data["startup_name"], st.session_state.idea_data["light_palette"][0])
                st.session_state.logo_variants = [new_logo]
                st.session_state.selected_logo_idx = 0

with col_clear:
    if st.button("🧹 Clear Idea & Start Over", use_container_width=True):
        st.session_state.idea_data = None
        st.session_state.logo_variants = []
        st.session_state.selected_logo_idx = None

# ----------------- DISPLAY IDEA -----------------
if st.session_state.idea_data:
    idea = st.session_state.idea_data
    st.subheader("📦 Startup Idea Pack")

    st.markdown(f"### {idea['startup_name']}")
    st.markdown(f"**Tagline:** {idea['tagline']}")
    st.write(idea["product_description"])

    st.markdown("#### Elevator Pitch")
    st.write(idea["pitch"])

    st.markdown("#### MVP Feature Suggestions")
    st.write("\n".join([f"• {feat}" for feat in idea["mvp_features"]]))

    st.markdown("#### Scores (1-10)")
    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("Novelty", idea["scores"]["novelty"])
    sc2.metric("Difficulty", idea["scores"]["difficulty"])
    sc3.metric("Business Potential", idea["scores"]["business_potential"])

    st.markdown("#### Mood Keywords")
    st.write(", ".join(idea["mood_keywords"]))

    st.markdown("#### Light Palette")
    palette_swatches(idea["light_palette"])

    st.markdown("#### Dark Palette")
    palette_swatches(idea["dark_palette"])

    if st.session_state.logo_variants:
        st.markdown("#### Generated Logo")
        st.image(st.session_state.logo_variants[0], use_container_width=True, width=300)

    zip_bytes = make_zip(idea, st.session_state.logo_variants[0])
    st.download_button(
        label="📥 Download Startup Pack (.zip)",
        data=zip_bytes,
        file_name=f"{idea['startup_name'].replace(' ', '_').lower()}_pack.zip",
        mime="application/zip",
    )
