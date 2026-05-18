import streamlit as st
import json
import os
import random
from PIL import Image
from rapidfuzz import fuzz

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Who Is It? · Celebrity Quiz",
    page_icon="🎭",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""<style>
/* (UNCHANGED CSS - keep as you already have) */
</style>""", unsafe_allow_html=True)

# ─── Constants ───────────────────────────────────────────────────────────────
ANSWERS_PATH = "dataset/answers.json"
IMAGES_DIR = "dataset/images"
FUZZY_THRESHOLD = 70

# ─── Helpers ─────────────────────────────────────────────────────────────────
def load_answers() -> dict:
    if not os.path.exists(ANSWERS_PATH):
        return {}
    with open(ANSWERS_PATH, "r") as f:
        return json.load(f)

def get_image_paths(answers: dict) -> list[str]:
    paths = []
    for filename in answers:
        full = os.path.join(IMAGES_DIR, filename)
        if os.path.exists(full):
            paths.append(filename)
    return paths

def is_correct(user_answer: str, correct_answer: str) -> bool:
    score = fuzz.token_sort_ratio(
        user_answer.lower().strip(),
        correct_answer.lower().strip()
    )
    return score >= FUZZY_THRESHOLD

def grade_label(score: int, total: int) -> tuple[str, str]:
    pct = score / total if total > 0 else 0
    if pct == 1.0: return "Perfect Score", "#3d8b4a"
    elif pct >= 0.8: return "Excellent", "#5a8b6a"
    elif pct >= 0.6: return "Good", "#8b7a3a"
    elif pct >= 0.4: return "Fair", "#8b5a3a"
    else: return "Keep Practicing", "#8b3a3a"

def init_state(answers: dict, image_files: list[str]):
    shuffled = image_files.copy()
    random.shuffle(shuffled)
    st.session_state.order = shuffled
    st.session_state.current = 0
    st.session_state.score = 0
    st.session_state.answers_map = answers
    st.session_state.feedback = None
    st.session_state.submitted = False
    st.session_state.finished = False
    st.session_state.input_key = 0

# ─── Load data ───────────────────────────────────────────────────────────────
answers = load_answers()
image_files = get_image_paths(answers)

if "order" not in st.session_state or not st.session_state.order:
    if image_files:
        init_state(answers, image_files)

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("WHO IS IT?")
    st.markdown("Celebrity Edition")

    if "order" in st.session_state:
        total = len(st.session_state.order)
        current = st.session_state.current
        score = st.session_state.score

        st.write(f"Score: {score}/{total}")
        st.write(f"Question: {min(current+1, total)}/{total}")

        if total > 0:
            st.progress(min(current / total, 1.0))

    if st.button("Restart"):
        init_state(answers, image_files)
        st.rerun()

# ─── Guard ───────────────────────────────────────────────────────────────────
if not image_files:
    st.error("Dataset not found")
    st.stop()

order = st.session_state.order
total = len(order)

# ─── FINISH ──────────────────────────────────────────────────────────────────
if st.session_state.get("finished", False):
    score = st.session_state.score
    grade, color = grade_label(score, total)

    st.markdown(f"### Score: {score}/{total}")
    st.markdown(f"### {grade}")
    st.stop()

# ─── QUIZ ────────────────────────────────────────────────────────────────────
idx = st.session_state.current
if idx >= total:
    st.session_state.finished = True
    st.rerun()

filename = order[idx]
correct_answer = st.session_state.answers_map.get(filename, "Unknown")
img_path = os.path.join(IMAGES_DIR, filename)

st.write(f"Loading: {img_path}")

# ─── FIXED IMAGE LOADING ─────────────────────────────────────────────────────
try:
    if not os.path.exists(img_path):
        raise FileNotFoundError(f"Missing file: {img_path}")

    img = Image.open(img_path)
    img.verify()

    img = Image.open(img_path).convert("RGB")

    st.image(img, use_container_width=True)

except Exception as e:
    st.error(f"Could not load image: {img_path}")
    st.exception(e)

# ─── INPUT ───────────────────────────────────────────────────────────────────
if not st.session_state.submitted:
    user_input = st.text_input("Your answer", key=f"input_{st.session_state.input_key}")

    if st.button("Submit") and user_input.strip():
        correct = is_correct(user_input, correct_answer)

        if correct:
            st.session_state.score += 1

        st.session_state.feedback = (correct, correct_answer, user_input)
        st.session_state.submitted = True
        st.rerun()

else:
    correct, ca, ua = st.session_state.feedback

    if correct:
        st.success(f"Correct! {ca}")
    else:
        st.error(f"Wrong! Answer: {ca}, You: {ua}")

    if st.button("Next"):
        st.session_state.current += 1
        st.session_state.submitted = False
        st.session_state.feedback = None
        st.session_state.input_key += 1

        if st.session_state.current >= total:
            st.session_state.finished = True

        st.rerun()