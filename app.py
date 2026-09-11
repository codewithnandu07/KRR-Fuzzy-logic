import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import random

st.set_page_config(page_title="KRR Fuzzy Traffic - LIVE", page_icon="🚦", layout="wide")

st.markdown("""
<style>
.stApp {background:#0f172a}
h1 {color:#22c55e!important; text-align:center}
</style>
""", unsafe_allow_html=True)

st.title("🚦 KRR - Fuzzy Logic Smart Traffic LIVE")
st.markdown("<p style='text-align:center;color:#94a3b8'>Live Simulation | Auto Updates Every 2 Sec</p>", unsafe_allow_html=True)

def trimf(x,a,b,c):
    if x <= a or x >= c: return 0.0
    if x <= b: return (x-a)/(b-a) if b!=a else 1.0
    return (c-x)/(c-b) if c!=b else 1.0

def fuzzy_infer(v, w):
    v_low = trimf(v, 0, 0, 20)
    v_med = trimf(v, 10, 25, 40)
    v_high = trimf(v, 30, 50, 50)
    w_low = trimf(w, 0, 0, 40)
    w_med = trimf(w, 20, 60, 90)
    w_high = trimf(w, 60, 120, 120)
    r_short = min(v_low, w_low)
    r_med = max(min(v_med, w_med), min(v_low, w_high))
    r_long = max(v_high, w_high)
    total = r_short + r_med + r_long
    green = 30 if total==0 else int((15*r_short + 35*r_med + 60*r_long)/total)
    if r_long >= r_med and r_long >= r_short:
        label, rule = "LONG", "R1: Density HIGH -> LONG"
    elif r_med >= r_short:
        label, rule = "MEDIUM", "R2: Density MED -> MEDIUM"
    else:
        label, rule = "SHORT", "R3: Density LOW -> SHORT"
    return green, label, rule

st.sidebar.header("⚙️ Controls")
live_mode = st.sidebar.toggle("🔴 LIVE SIMULATION (Auto Move)", value=True)

if "n_v" not in st.session_state:
    st.session_state.n_v, st.session_state.s_v, st.session_state.e_v, st.session_state.w_v = 35,10,25,40
    st.session_state.n_w, st.session_state.s_w, st.session_state.e_w, st.session_state.w_w = 80,20,50,90

if live_mode:
    st.session_state.n_v = max(0, min(50, st.session_state.n_v + random.randint(-3, 4)))
    st.session_state.s_v = max(0, min(50, st.session_state.s_v + random.randint(-3, 4)))
    st.session_state.e_v = max(0, min(50, st.session_state.e_v + random.randint(-3, 4)))
    st.session_state.w_v = max(0, min(50, st.session_state.w_v + random.randint(-3, 4)))
    st.session_state.n_w = max(0, min(120, st.session_state.n_w + random.randint(-2, 5)))
    st.session_state.s_w = max(0, min(120, st.session_state.s_w + random.randint(-2, 5)))
    st.session_state.e_w = max(0, min(120, st.session_state.e_w + random.randint(-2, 5)))
    st.session_state.w_w = max(0, min(120, st.session_state.w_w + random.randint(-2, 5)))
else:
    # === TYPING ADDED HERE ===
    st.sidebar.subheader("✍️ TYPE Vehicles Here")
    st.session_state.n_v = st.sidebar.number_input("North Vehicles", 0, 50, st.session_state.n_v)
    st.session_state.s_v = st.sidebar.number_input("South Vehicles", 0, 50, st.session_state.s_v)
    st.session_state.e_v = st.sidebar.number_input("East Vehicles", 0, 50, st.session_state.e_v)
    st.session_state.w_v = st.sidebar.number_input("West Vehicles", 0, 50, st.session_state.w_v)
    st.sidebar.markdown("---")
    st.sidebar.subheader("✍️ TYPE Waiting Time Here")
    st.session_state.n_w = st.sidebar.number_input("North Waiting", 0, 120, st.session_state.n_w)
    st.session_state.s_w = st.sidebar.number_input("South Waiting", 0, 120, st.session_state.s_w)
    st.session_state.e_w = st.sidebar.number_input("East Waiting", 0, 120, st.session_state.e_w)
    st.session_state.w_w = st.sidebar.number_input("West Waiting", 0, 120, st.session_state.w_w)

roads = {"North":(st.session_state.n_v, st.session_state.n_w), "South":(st.session_state.s_v, st.session_state.s_w), "East":(st.session_state.e_v, st.session_state.e_w), "West":(st.session_state.w_v, st.session_state.w_w)}
rows=[]
for name,(v,w) in roads.items():
    g,label,rule = fuzzy_infer(v,w)
    rows.append([name,v,w,g,label,rule, v + w/2])

df = pd.DataFrame(rows, columns=["Road","Vehicles","Waiting","Green","Decision","Rule","Score"])
best = df.loc[df["Score"].idxmax()]

st.subheader("📊 Live Inference Table (Changes every 2 sec)" if live_mode else "📊 Inference Table (Type to Update)")
st.dataframe(df[["Road","Vehicles","Waiting","Green","Decision","Rule"]], use_container_width=True, hide_index=True)
st.success(f"### 🟢 GREEN → {best['Road']} for {best['Green']}s ({best['Decision']})")

c1,c2 = st.columns(2)
with c1:
    st.subheader("📈 Vehicles vs Green")
    fig, ax = plt.subplots()
    ax.bar(df["Road"], df["Vehicles"], label="Vehicles", alpha=0.7)
    ax.bar(df["Road"], df["Green"], label="Green", alpha=0.7)
    ax.legend(); ax.grid(alpha=0.3)
    st.pyplot(fig)

with c2:
    st.subheader("🚦 Intersection")
    def col(r): return "#22c55e" if best["Road"]==r else "#ef4444"
    st.markdown(f"""
    <div style="background:#020617;padding:15px;border-radius:15px;text-align:center;color:white">
        <div style="background:{col('North')};padding:10px;border-radius:10px;margin:5px">NORTH {best['Road']=='North' and '🟢' or '🔴'}</div>
        <div style="display:flex;gap:10px"><div style="background:{col('West')};padding:10px;border-radius:10px;flex:1">WEST</div>
        <div style="background:#1e293b;padding:10px;border-radius:10px;flex:1">+</div>
        <div style="background:{col('East')};padding:10px;border-radius:10px;flex:1">EAST</div></div>
        <div style="background:{col('South')};padding:10px;border-radius:10px;margin:5px">SOUTH</div>
    </div>""", unsafe_allow_html=True)

if live_mode:
    time.sleep(2)
    st.rerun()
