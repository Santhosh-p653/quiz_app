import streamlit as st
import json
import os
import random
from PIL import Image
from rapidfuzz import fuzz

# ─── CONFIG ─────────────────────────────────────────────
st.set_page_config(
    page_title="Who Is It?",
    page_icon="🎭",
    layout="centered"
)

ANSWERS_PATH = "dataset/answers.json"
IMAGES_DIR = "dataset/images"
THRESHOLD = 70

# ─── LOAD DATA ──────────────────────────────────────────
def load_answers():
    if not os.path.exists(ANSWERS_PATH):
        return {}
    with open(ANSWERS_PATH, "r") as f:
        return json.load(f)

answers = load_answers()
image_files = list(answers.keys())

# ─── INIT STATE ──────────────────────────────────────────
if "order" not in st.session_state:
    st.session_state.order = random.sample(image_files, len(image_files))
    st.session_state.i = 0
    st.session_state.score = 0
    st.session_state.done = False

# ─── END CHECK ───────────────────────────────────────────
if st.session_state.i >= len(st.session_state.order):
    st.session_state.done = True

if st.session_state.done:
    st.title(f"Score: {st.session_state.score}/{len(image_files)}")
    st.stop()

# ─── CURRENT QUESTION ────────────────────────────────────
filename = st.session_state.order[st.session_state.i]
img_path = os.path.join(IMAGES_DIR, filename)
correct = answers.get(filename, "")

st.title("Who is this?")

# ─── IMAGE LOAD (SAFE) ───────────────────────────────────
if os.path.exists(img_path):
    try:
        img = Image.open(img_path).convert("RGB")
        st.image(img, use_container_width=True)
    except Exception as e:
        st.error("Image load failed")
        st.exception(e)
else:
    st.error(f"Missing image: {img_path}")

# ─── INPUT ───────────────────────────────────────────────
user = st.text_input("Your answer")

if st.button("Submit") and user:
    score = fuzz.token_sort_ratio(user.lower(), correct.lower())

    if score >= THRESHOLD:
        st.success(f"Correct! ({correct})")
        st.session_state.score += 1
    else:
        st.error(f"Wrong! Answer: {correct}")

    st.session_state.i += 1
    st.rerun()

if st.button("Skip"):
    st.session_state.i += 1
    st.rerun()