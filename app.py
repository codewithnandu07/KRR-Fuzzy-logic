import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Fuzzy Traffic KRR", page_icon="🚦", layout="wide")

st.title("🚦 Fuzzy Logic Smart Traffic Management - KRR")
st.markdown("KRR Project | Knowledge Base + Inference | Fully Interactive")

def tri(x,a,b,c):
    if x<=a or x>=c: return 0
    if x<=b: return (x-a)/(b-a) if b!=a else 1
    return (c-x)/(c-b)

def infer(v,w):
    vL,vM,vH = tri(v,0,0,20), tri(v,10,25,40), tri(v,30,50,50)
    wL,wM,wH = tri(w,0,0,40), tri(w,20,60,90), tri(w,60,120,120)
    short = min(vL,wL)
    med = max(min(vM,wM), min(wH,vL))
    long = max(vH,wH)
    total = short+med+long
    if total==0: green=30
    else: green = int((15*short + 35*med + 60*long)/total)
    label = "LONG" if long>=med and long>=short else "MEDIUM" if med>=short else "SHORT"
    rule = "R1: Density HIGH -> LONG" if label=="LONG" else "R2: Density MED -> MEDIUM" if label=="MEDIUM" else "R3: Density LOW -> SHORT"
    return green, label, rule

# SIDEBAR - KB
st.sidebar.header("📥 Knowledge Base - Move Sliders")
north = st.sidebar.slider("North Vehicles", 0, 50, 35)
south = st.sidebar.slider("South Vehicles", 0, 50, 10)
east = st.sidebar.slider("East Vehicles", 0, 50, 25)
west = st.sidebar.slider("West Vehicles", 0, 50, 40)

st.sidebar.markdown("---")
w_n = st.sidebar.slider("North Waiting (s)", 0, 120, 80)
w_s = st.sidebar.slider("South Waiting (s)", 0, 120, 20)
w_e = st.sidebar.slider("East Waiting (s)", 0, 120, 50)
w_w = st.sidebar.slider("West Waiting (s)", 0, 120, 90)

roads = {"North":(north,w_n), "South":(south,w_s), "East":(east,w_e), "West":(west,w_w)}

# INFERENCE
results=[]
for road,(v,w) in roads.items():
    green,label,rule = infer(v,w)
    score = v + w/2
    results.append([road,v,w,green,label,rule,score])

df = pd.DataFrame(results, columns=["Road","Vehicles","Waiting","Green(s)","Decision","Rule Fired","Score"])
best_row = df.loc[df['Score'].idxmax()]

# MAIN
col1, col2 = st.columns([2,1])

with col1:
    st.subheader("📊 Inference Table (Auto Updates)")
    st.dataframe(df[["Road","Vehicles","Waiting","Green(s)","Decision","Rule Fired"]], use_container_width=True, hide_index=True)
    st.success(f"### 🟢 GREEN -> {best_row['Road']} for {best_row['Green(s)']}s ({best_row['Decision']})")

    st.subheader("📈 Graph - Vehicles vs Green Time")
    fig, ax = plt.subplots()
    ax.bar(df["Road"], df["Vehicles"], label="Vehicles", alpha=0.7)
    ax.bar(df["Road"], df["Green(s)"], label="Green Time", alpha=0.7)
    ax.legend()
    st.pyplot(fig)

    st.subheader("🔺 Fuzzy Membership - Vehicle Density")
    x = np.linspace(0,50,100)
    fig2, ax2 = plt.subplots()
    ax2.plot(x, [tri(i,0,0,20) for i in x], label='Low')
    ax2.plot(x, [tri(i,10,25,40) for i in x], label='Medium')
    ax2.plot(x, [tri(i,30,50,50) for i in x], label='High')
    ax2.set_xlabel("Vehicles"); ax2.legend(); ax2.grid(True)
    st.pyplot(fig2)

with col2:
    st.subheader("🚦 Live Intersection")
    html = f"""
    <div style="background:#020617;padding:20px;border-radius:15px;text-align:center;color:white">
        <div style="background:{'#22c55e' if best_row['Road']=='North' else '#ef4444'};padding:15px;border-radius:10px;margin:5px">NORTH {'🟢' if best_row['Road']=='North' else '🔴'}</div>
        <div style="display:flex;justify-content:space-between">
            <div style="background:{'#22c55e' if best_row['Road']=='West' else '#ef4444'};padding:15px;border-radius:10px">WEST {'🟢' if best_row['Road']=='West' else '🔴'}</div>
            <div style="background:#334155;padding:15px;border-radius:10px">INTERSECTION</div>
            <div style="background:{'#22c55e' if best_row['Road']=='East' else '#ef4444'};padding:15px;border-radius:10px">EAST {'🟢' if best_row['Road']=='East' else '🔴'}</div>
        </div>
        <div style="background:{'#22c55e' if best_row['Road']=='South' else '#ef4444'};padding:15px;border-radius:10px;margin:5px">SOUTH {'🟢' if best_row['Road']=='South' else '🔴'}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    st.metric("North", f"{north} veh", f"{infer(north,w_n)[0]}s green")
    st.metric("South", f"{south} veh", f"{infer(south,w_s)[0]}s green")
    st.metric("East", f"{east} veh", f"{infer(east,w_e)[0]}s green")
    st.metric("West", f"{west} veh", f"{infer(west,w_w)[0]}s green")

st.download_button("📄 Download Full Report CSV", df.to_csv(index=False), "krr_traffic_report.csv")
