import streamlit as st
import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt

st.set_page_config(page_title="Fuzzy Smart Traffic - KRR", page_icon="🚦", layout="wide")

# --- Custom CSS like FOAI/DS ---
st.markdown("""
<style>
.stApp{background:#0f172a;color:white}
h1{color:#22c55e!important;text-align:center}
.card{background:#1e293b;padding:20px;border-radius:15px;border:1px solid #22c55e}
.badge{padding:6px 15px;border-radius:20px;font-weight:bold}
</style>
""", unsafe_allow_html=True)

st.title("🚦 Fuzzy Logic - Smart Traffic Management")
st.markdown("<p style='text-align:center;color:#94a3b8'>KRR Project | Knowledge Representation & Reasoning | Forward Chaining + Fuzzy Inference</p>", unsafe_allow_html=True)

# --- FUZZY ENGINE (KRR CORE) ---
def tri(x,a,b,c):
    if x<=a or x>=c: return 0.0
    if x<=b: return (x-a)/(b-a) if b!=a else 1
    return (c-x)/(c-b) if c!=b else 1

def infer(vehicles, waiting):
    vL, vM, vH = tri(vehicles,0,0,20), tri(vehicles,10,25,40), tri(vehicles,30,50,50)
    wL, wM, wH = tri(waiting,0,0,40), tri(waiting,20,60,90), tri(waiting,60,120,120)
    short = min(vL,wL)
    med = max(min(vM,wM), min(wH,vL))
    long = max(vH,wH, min(vH,wM))
    total = short+med+long
    if total==0: return 30, "MEDIUM", "Default", {"L":0,"M":1,"H":0}
    green = int((15*short + 35*med + 60*long)/total)
    if long>=med and long>=short:
        label, rule = "LONG", "R1: IF Density HIGH OR Waiting HIGH → Green LONG"
    elif med>=short:
        label, rule = "MEDIUM", "R2: IF Density MEDIUM → Green MEDIUM"
    else:
        label, rule = "SHORT", "R3: IF Density LOW → Green SHORT"
    return green, label, rule, {"L":vL,"M":vM,"H":vH}

# --- SIDEBAR = KNOWLEDGE BASE ---
st.sidebar.header("📥 KNOWLEDGE BASE (Facts)")
st.sidebar.markdown("**Ontology:** Road, Vehicle, Signal")

north = st.sidebar.slider("North - Vehicles", 0, 50, 35)
south = st.sidebar.slider("South - Vehicles", 0, 50, 10)
east = st.sidebar.slider("East - Vehicles", 0, 50, 25)
west = st.sidebar.slider("West - Vehicles", 0, 50, 40)

st.sidebar.markdown("---")
st.sidebar.subheader("Rule Base")
st.sidebar.code("""
R1: IF Density=High OR Waiting=High THEN Green=Long
R2: IF Density=Medium AND Waiting=Medium THEN Green=Medium
R3: IF Density=Low THEN Green=Short
R4: IF Waiting=High AND Density=Low THEN Green=Medium
""", language="text")

# Waiting time - dynamic fact
if 'waiting' not in st.session_state:
    st.session_state.waiting = {"North":80, "South":20, "East":50, "West":90}

roads_data = {
    "North": {"v":north, "w":st.session_state.waiting["North"]},
    "South": {"v":south, "w":st.session_state.waiting["South"]},
    "East": {"v":east, "w":st.session_state.waiting["East"]},
    "West": {"v":west, "w":st.session_state.waiting["West"]},
}

# --- MAIN AREA ---
col1, col2 = st.columns([2,1])

with col1:
    st.subheader("🧠 Inference Engine Output")
    results = []
    best_road = None
    max_score = -1

    for road, d in roads_data.items():
        green, label, rule, fuzzy = infer(d["v"], d["w"])
        score = d["v"] + d["w"]/2
        if score>max_score:
            max_score=score
            best_road=road
        results.append([road, d["v"], d["w"], green, label, rule, "🟢 GREEN" if road==best_road else "🔴 RED"])

    df = pd.DataFrame(results, columns=["Road","Vehicles (Fact)","Waiting (Fact)","Green(s) [Inferred]","Decision","Rule Fired","Signal"])
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.success(f"### ✅ FINAL DECISION: Give GREEN to **{best_road} ROAD**")
    st.info(f"**Reasoning (Conflict Resolution):** {best_road} has Max(Vehicles + Waiting/2) = {max_score:.1f} | **Justification:** Highest priority fact")

    # Update waiting for next cycle
    if st.button("▶ NEXT CYCLE (Update Knowledge Base)"):
        for r in roads_data:
            if r==best_road:
                st.session_state.waiting[r]=0
            else:
                st.session_state.waiting[r]+=10
        st.rerun()

    # Graph
    st.subheader("📊 Density vs Green Time")
    fig, ax = plt.subplots()
    x = [r[1] for r in results]
    y = [r[3] for r in results]
    roads = [r[0] for r in results]
    ax.bar(roads, x, label="Vehicles", alpha=0.6)
    ax.bar(roads, y, label="Green Time", alpha=0.6)
    ax.legend()
    ax.set_facecolor("#1e293b")
    fig.patch.set_facecolor("#1e293b")
    st.pyplot(fig)

with col2:
    st.subheader("🚦 Intersection Simulation")
    canvas_html = f"""
    <div style="background:#020617;padding:20px;border-radius:15px;text-align:center">
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px">
            <div></div>
            <div style="background:{'#22c55e' if best_road=='North' else '#ef4444'};padding:15px;border-radius:10px">NORTH<br>{'🟢' if best_road=='North' else '🔴'}</div>
            <div></div>
            <div style="background:{'#22c55e' if best_road=='West' else '#ef4444'};padding:15px;border-radius:10px">WEST<br>{'🟢' if best_road=='West' else '🔴'}</div>
            <div style="background:#334155;padding:20px;border-radius:10px">+<br>INTERSECTION</div>
            <div style="background:{'#22c55e' if best_road=='East' else '#ef4444'};padding:15px;border-radius:10px">EAST<br>{'🟢' if best_road=='East' else '🔴'}</div>
            <div></div>
            <div style="background:{'#22c55e' if best_road=='South' else '#ef4444'};padding:15px;border-radius:10px">SOUTH<br>{'🟢' if best_road=='South' else '🔴'}</div>
            <div></div>
        </div>
    </div>
    """
    st.markdown(canvas_html, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📄 Download Report")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download KB + Inference CSV", csv, "krr_traffic_kb.csv", "text/csv")

    st.markdown("**For Viva:**")
    st.markdown("""
    - **Representation:** Fuzzy Sets + Production Rules
    - **Inference:** Forward Chaining (MIN-MAX)
    - **Defuzzification:** Weighted Average
    - **Advantage:** Handles uncertainty like human
    """)
