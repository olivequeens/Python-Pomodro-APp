# main.py
import streamlit as st
import time
import base64
import os
from streamlit_autorefresh import st_autorefresh
from streamlit.components.v1 import html
import matplotlib.pyplot as plt

POMODOROS_PER_CYCLE = 4
TIME_OPTIONS = [15, 25, 40, 50]  # minutes

# ---------- initialize session state ----------
if "running" not in st.session_state:
    st.session_state.running = False
if "mode" not in st.session_state:
    st.session_state.mode = "focus"  # 'focus', 'short_break', 'long_break'
if "initial_seconds" not in st.session_state:
    st.session_state.initial_seconds = 25 * 60
if "remaining" not in st.session_state:
    st.session_state.remaining = st.session_state.initial_seconds
if "end_time" not in st.session_state:
    st.session_state.end_time = None
if "session_count" not in st.session_state:
    st.session_state.session_count = 0
if "task" not in st.session_state:
    st.session_state.task = ""
if "alarm_bytes" not in st.session_state:
    alarm_path = "alarm.mp3"
    if os.path.exists(alarm_path):
        with open(alarm_path, "rb") as f:
            st.session_state.alarm_bytes = f.read()
    else:
        st.session_state.alarm_bytes = None

# ---------- UI ----------
st.title("Pomodoro Timer (Streamlit)")

col1, col2 = st.columns([3, 1])
with col1:
    st.session_state.task = st.text_input("Task name", value=st.session_state.task)
    choose_min = st.selectbox("Focus duration (min)", TIME_OPTIONS,
                              index=TIME_OPTIONS.index(st.session_state.initial_seconds // 60)
                              if (st.session_state.initial_seconds // 60) in TIME_OPTIONS else 1)

with col2:
    st.markdown("**Sessions**")
    st.metric(label="Completed", value=st.session_state.session_count)

# handle change of chosen focus duration (only allowed while stopped)
if not st.session_state.running and choose_min * 60 != st.session_state.initial_seconds:
    st.session_state.initial_seconds = choose_min * 60
    st.session_state.remaining = st.session_state.initial_seconds
    st.session_state.mode = "focus"
    st.session_state.end_time = None

start_label = "Pause" if st.session_state.running else "Start"
start = st.button(start_label)
skip = st.button("Skip")
reset = st.button("Reset")

# ---------- Controls behavior ----------
if start:
    if not st.session_state.running:
        # start timer
        st.session_state.end_time = time.time() + st.session_state.remaining
        st.session_state.running = True
    else:
        # pause
        if st.session_state.end_time:
            st.session_state.remaining = max(0, st.session_state.end_time - time.time())
        st.session_state.end_time = None
        st.session_state.running = False

if reset:
    st.session_state.running = False
    st.session_state.mode = "focus"
    st.session_state.initial_seconds = 25 * 60
    st.session_state.remaining = st.session_state.initial_seconds
    st.session_state.session_count = 0
    st.session_state.end_time = None

def advance_phase():
    if st.session_state.mode == "focus":
        st.session_state.session_count += 1
        if st.session_state.session_count % POMODOROS_PER_CYCLE == 0:
            st.session_state.mode = "long_break"
            st.session_state.initial_seconds = 15 * 60
        else:
            st.session_state.mode = "short_break"
            st.session_state.initial_seconds = 5 * 60
    else:
        st.session_state.mode = "focus"
        st.session_state.initial_seconds = choose_min * 60
    st.session_state.remaining = st.session_state.initial_seconds
    # auto-start the next phase
    st.session_state.end_time = time.time() + st.session_state.remaining
    st.session_state.running = True

if skip:
    # move to next phase immediately
    advance_phase()

# ---------- auto-refresh every second (client-driven) ----------
st_autorefresh(interval=1000, limit=None, key="timer_refresh")

# ---------- timer update ----------
if st.session_state.running and st.session_state.end_time:
    st.session_state.remaining = max(0, st.session_state.end_time - time.time())

if st.session_state.remaining <= 0 and st.session_state.running:
    # play alarm (autoplay via embedded base64 audio; browsers may block autoplay)
    if st.session_state.alarm_bytes:
        b64 = base64.b64encode(st.session_state.alarm_bytes).decode()
        # embeds an <audio autoplay> element
        html(f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>')
    else:
        # fallback: display a visual alert
        st.balloons()
    # advance to next phase
    advance_phase()

# ---------- display ----------
minutes = int(st.session_state.remaining) // 60
seconds = int(st.session_state.remaining) % 60
st.subheader(f"{st.session_state.mode.replace('_',' ').title()}")
st.markdown(f"### {minutes:02d}:{seconds:02d}")

percent = int((1 - (st.session_state.remaining / st.session_state.initial_seconds)) * 100)
if percent < 0: percent = 0
if percent > 100: percent = 100
st.progress(percent)

# simple donut chart for visual progress
fig, ax = plt.subplots(figsize=(3,3))
ax.pie([st.session_state.remaining, max(0, st.session_state.initial_seconds - st.session_state.remaining)],
       startangle=90, counterclock=False)
centre_circle = plt.Circle((0, 0), 0.70, fc='white')
fig.gca().add_artist(centre_circle)
ax.axis("equal")
st.pyplot(fig)

st.write("Controls: Start/Pause, Skip, Reset. Optionally include `alarm.mp3` in the repo to get a sound.")
