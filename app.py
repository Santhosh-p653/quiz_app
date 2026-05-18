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
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Mono:wght@300;400;500&display=swap');

  html, body, [class*="css"] {
    font-family: 'DM Mono', monospace;
    background-color: #0d0d0d;
    color: #e8e0d0;
  }

  .stApp { background: #0d0d0d; }

  [data-testid="stSidebar"] {
    background: #111111;
    border-right: 1px solid #2a2a2a;
  }
  [data-testid="stSidebar"] * {
    font-family: 'DM Mono', monospace !important;
    color: #e8e0d0 !important;
  }

  .quiz-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 2.8rem;
    letter-spacing: -0.03em;
    color: #f0e6d0;
    line-height: 1.1;
    margin-bottom: 0.2rem;
  }

  .quiz-subtitle {
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    color: #5a5a5a;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 2rem;
  }

  .stat-card {
    background: #161616;
    border: 1px solid #2a2a2a;
    border-radius: 4px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.8rem;
  }

  .stat-label {
    font-size: 0.65rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #4a4a4a;
    margin-bottom: 0.3rem;
  }

  .stat-value {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #c8b89a;
  }

  .image-frame {
    border: 1px solid #2a2a2a;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 1.5rem;
    background: #111;
  }

  .question-badge {
    display: inline-block;
    background: #1e1e1e;
    border: 1px solid #333;
    border-radius: 2px;
    padding: 0.25rem 0.75rem;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #6a6a6a;
    margin-bottom: 1rem;
  }

  .feedback-correct {
    background: #0d1f0f;
    border: 1px solid #1a4020;
    border-left: 3px solid #3d8b4a;
    border-radius: 2px;
    padding: 0.9rem 1.2rem;
    margin: 0.8rem 0;
    font-size: 0.85rem;
    color: #7bc98a;
  }

  .feedback-wrong {
    background: #1a0d0d;
    border: 1px solid #3d1515;
    border-left: 3px solid #8b3a3a;
    border-radius: 2px;
    padding: 0.9rem 1.2rem;
    margin: 0.8rem 0;
    font-size: 0.85rem;
    color: #c97b7b;
  }

  .final-score-wrap {
    text-align: center;
    padding: 3rem 1rem;
  }

  .final-big {
    font-family: 'Syne', sans-serif;
    font-size: 6rem;
    font-weight: 800;
    color: #c8b89a;
    line-height: 1;
    letter-spacing: -0.04em;
  }

  .final-label {
    font-size: 0.75rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #4a4a4a;
    margin-top: 0.5rem;
    margin-bottom: 2rem;
  }

  .grade-badge {
    display: inline-block;
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    padding: 0.5rem 1.5rem;
    border-radius: 2px;
    margin-bottom: 2.5rem;
    letter-spacing: 0.05em;
  }

  .stTextInput > div > div > input {
    background: #161616 !important;
    border: 1px solid #333 !important;
    border-radius: 2px !important;
    color: #e8e0d0 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.9rem !important;
    padding: 0.75rem 1rem !important;
  }
  .stTextInput > div > div > input:focus {
    border-color: #c8b89a !important;
    box-shadow: 0 0 0 1px #c8b89a22 !important;
  }

  .stButton > button {
    background: #1e1e1e !important;
    border: 1px solid #333 !important;
    border-radius: 2px !important;
    color: #e8e0d0 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.15s ease !important;
  }
  .stButton > button:hover {
    background: #c8b89a !important;
    border-color: #c8b89a !important;
    color: #0d0d0d !important;
  }

  .stProgress > div > div > div > div { background: #c8b89a !important; }
  .stProgress > div > div > div { background: #1e1e1e !important; }

  div[data-testid="stMarkdownContainer"] p {
    font-family: 'DM Mono', monospace;
    color: #e8e0d0;
  }

  .divider {
    border: none;
    border-top: 1px solid #1e1e1e;
    margin: 1.5rem 0;
  }
</style>
""", unsafe_allow_html=True)

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
    score = fuzz.token_sort_ratio(user_answer.lower().strip(), correct_answer.lower().strip())
    return score >= FUZZY_THRESHOLD

def grade_label(score: int, total: int) -> tuple[str, str]:
    pct = score / total if total > 0 else 0
    if pct == 1.0:   return "Perfect Score", "#3d8b4a"
    elif pct >= 0.8: return "Excellent",     "#5a8b6a"
    elif pct >= 0.6: return "Good",          "#8b7a3a"
    elif pct >= 0.4: return "Fair",          "#8b5a3a"
    else:            return "Keep Practicing","#8b3a3a"

def init_state(answers: dict, image_files: list[str]):
    shuffled = image_files.copy()
    random.shuffle(shuffled)
    st.session_state.order        = shuffled
    st.session_state.current      = 0
    st.session_state.score        = 0
    st.session_state.answers_map  = answers
    st.session_state.feedback     = None
    st.session_state.submitted    = False
    st.session_state.finished     = False
    st.session_state.input_key    = 0

# ─── Load data ───────────────────────────────────────────────────────────────
answers     = load_answers()
image_files = get_image_paths(answers)

if "order" not in st.session_state or not st.session_state.order:
    if image_files:
        init_state(answers, image_files)

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="quiz-title" style="font-size:1.6rem;">WHO IS IT?</div>', unsafe_allow_html=True)
    st.markdown('<div class="quiz-subtitle">Celebrity Edition</div>', unsafe_allow_html=True)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    if "score" in st.session_state and "order" in st.session_state:
        total   = len(st.session_state.order)
        current = st.session_state.current
        score   = st.session_state.score

        st.markdown(f"""
        <div class="stat-card">
          <div class="stat-label">Score</div>
          <div class="stat-value">{score}/{total}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Question</div>
          <div class="stat-value">{min(current + 1, total)}/{total}</div>
        </div>
        """, unsafe_allow_html=True)

        if total > 0:
            st.progress(min(current / total, 1.0))

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    if st.button("↺  Restart Quiz"):
        if image_files:
            init_state(answers, image_files)
        st.rerun()

    st.markdown('<div style="margin-top:2rem;font-size:0.65rem;color:#3a3a3a;letter-spacing:0.1em;">FUZZY MATCH ≥ 70%</div>', unsafe_allow_html=True)

# ─── No dataset guard ────────────────────────────────────────────────────────
if not image_files:
    st.markdown('<div class="quiz-title">Dataset Not Found</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="color:#5a5a5a;font-size:0.85rem;margin-top:1rem;">
    Run <code style="background:#1e1e1e;padding:2px 6px;border-radius:2px;color:#c8b89a;">python generate_dataset.py</code> first.
    </div>
    """, unsafe_allow_html=True)
    st.stop()

order = st.session_state.order
total = len(order)

# ─── FINISHED ────────────────────────────────────────────────────────────────
if st.session_state.get("finished", False):
    score        = st.session_state.score
    grade, color = grade_label(score, total)

    st.markdown(f"""
    <div class="final-score-wrap">
      <div class="final-big">{score}</div>
      <div class="final-label">out of {total} correct</div>
      <div class="grade-badge" style="background:{color}22;color:{color};border:1px solid {color}44;">{grade}</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Play Again →"):
            init_state(answers, image_files)
            st.rerun()
    st.stop()

# ─── QUIZ ────────────────────────────────────────────────────────────────────
idx = st.session_state.current
if idx >= total:
    st.session_state.finished = True
    st.rerun()

filename       = order[idx]
correct_answer = st.session_state.answers_map.get(filename, "Unknown")
img_path       = os.path.join(IMAGES_DIR, filename)

st.markdown(f'<div class="question-badge">Question {idx + 1} of {total}</div>', unsafe_allow_html=True)
st.markdown('<div class="quiz-title">Who Is This?</div>', unsafe_allow_html=True)
st.markdown('<div class="quiz-subtitle">Type the name below · Fuzzy matching enabled</div>', unsafe_allow_html=True)

try:
    img = Image.open(img_path)
    st.markdown('<div class="image-frame">', unsafe_allow_html=True)
    st.image(img, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
except Exception:
    st.error(f"Could not load image: {img_path}")

if not st.session_state.submitted:
    user_input = st.text_input(
        "Your answer",
        key=f"answer_input_{st.session_state.input_key}",
        placeholder="e.g. Elon Musk",
        label_visibility="collapsed",
    )

    col_a, col_b = st.columns([3, 1])
    with col_a:
        submit = st.button("Submit Answer →", use_container_width=True)
    with col_b:
        skip = st.button("Skip", use_container_width=True)

    if submit and user_input.strip():
        correct = is_correct(user_input, correct_answer)
        if correct:
            st.session_state.score += 1
        st.session_state.feedback  = (correct, correct_answer, user_input.strip())
        st.session_state.submitted = True
        st.rerun()

    if skip:
        st.session_state.feedback  = (False, correct_answer, "(skipped)")
        st.session_state.submitted = True
        st.rerun()

else:
    correct, ca, ua = st.session_state.feedback
    if correct:
        st.markdown(f'<div class="feedback-correct">✓ &nbsp; Correct! &nbsp;·&nbsp; <strong>{ca}</strong></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="feedback-wrong">✗ &nbsp; The answer was <strong>{ca}</strong> &nbsp;·&nbsp; You said: <em>{ua}</em></div>', unsafe_allow_html=True)

    next_label = "Next Question →" if idx + 1 < total else "See Results →"
    if st.button(next_label, use_container_width=True):
        st.session_state.current  += 1
        st.session_state.submitted = False
        st.session_state.feedback  = None
        st.session_state.input_key += 1
        if st.session_state.current >= total:
            st.session_state.finished = True
        st.rerun()
