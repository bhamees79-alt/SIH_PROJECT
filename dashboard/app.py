import base64
from pathlib import Path

import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "data"
DEMO_VIDEO = DATA_DIR / "seed_handling_demo_presentation.mp4"
RAW_DEMO = DATA_DIR / "seed_handling_demo.mp4"

st.set_page_config(
    page_title="HAR SYSTEM ISRO",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
:root{--navy:#08223f;--blue:#1268a8;--sky:#eaf4fb;--line:#d7e1eb;--text:#142033;--muted:#65758a;--orange:#e87924;--green:#16845a;--red:#c63d3d}
html,body,[class*="css"]{font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}
.stApp{background:#f4f7fa;color:var(--text)}
section[data-testid="stSidebar"]{background:var(--navy)}
section[data-testid="stSidebar"] *{color:#eef5fb!important}
.block-container{padding-top:1.15rem;max-width:1500px}
.hero{background:#fff;border:1px solid var(--line);border-left:5px solid var(--blue);border-radius:12px;padding:19px 24px;margin-bottom:15px;box-shadow:0 2px 8px rgba(20,32,51,.03)}
.hero h1{margin:0;color:var(--navy);font-size:2rem;letter-spacing:.2px}.hero p{margin:5px 0 0;color:var(--muted)}
.section{color:var(--navy);font-weight:800;font-size:1.1rem;margin:19px 0 9px}
.card,.metric,.timeline,.alertbox{background:#fff;border:1px solid var(--line);border-radius:11px;padding:14px 16px;box-shadow:0 2px 8px rgba(20,32,51,.025)}
.card-title{color:var(--navy);font-weight:800;margin-bottom:5px}.small{color:var(--muted);font-size:.86rem}
.metric .label{color:var(--muted);font-size:.77rem}.metric .value{color:var(--navy);font-size:1.35rem;font-weight:850;margin-top:2px}
.pill{display:inline-block;border-radius:999px;padding:4px 9px;font-size:.68rem;font-weight:850;letter-spacing:.3px}.ready{background:#e8f6ef;color:#126b49}.blue{background:#eaf3fb;color:#155b91}.orange{background:#fff1e7;color:#9b4d09}.danger{background:#fdecec;color:#9f2f2f}
.step{display:flex;align-items:center;gap:12px;padding:9px 11px;margin:5px 0;background:#fff;border:1px solid var(--line);border-radius:8px}.num{width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:var(--sky);color:var(--blue);font-weight:850}.done .num{background:#e8f6ef;color:var(--green)}
.pipeline{display:flex;gap:7px;align-items:stretch}.pipe{flex:1;background:#fff;border:1px solid var(--line);border-radius:9px;padding:11px}.pipe b{color:var(--navy);display:block}.arrow{display:flex;align-items:center;color:#94a3b8;font-weight:850}
.notice{background:#f8fbff;border:1px solid #cfe0ef;border-left:4px solid var(--blue);border-radius:9px;padding:11px 13px;color:#30465c}
.alertgood{background:#effaf5;border:1px solid #cdebdc;border-left:4px solid var(--green);border-radius:9px;padding:11px 13px;color:#205a43}
.alerterr{background:#fff3f3;border:1px solid #f1d0d0;border-left:4px solid var(--red);border-radius:9px;padding:11px 13px;color:#7f2929}
.footer{border-top:1px solid var(--line);margin-top:30px;padding-top:12px;color:var(--muted);font-size:.75rem}
div[data-testid="stButton"]>button{border-radius:8px;font-weight:750}
</style>
""",
    unsafe_allow_html=True,
)

ACTIVITIES = [
    ("RETRIEVE_COTTON", "Retrieve cotton"),
    ("PLACE_COTTON", "Place / arrange cotton"),
    ("HANDLE_SEEDS", "Handle seeds"),
    ("PLACE_SEEDS", "Place seeds on cotton"),
    ("TAKE_DROPPER", "Retrieve / use dropper"),
    ("ADD_WATER", "Add water"),
]

# Presentation timeline follows the expected BAS seed-handling procedure.
# The final 10.6 s window matches the prepared demo video duration.
DEMO_SEGMENTS = [
    (0.0, 1.0, "SETUP", "Experiment setup"),
    (1.0, 2.1, "RETRIEVE_COTTON", "Retrieve cotton"),
    (2.1, 3.2, "PLACE_COTTON", "Place / arrange cotton"),
    (3.2, 4.3, "HANDLE_SEEDS", "Handle seeds"),
    (4.3, 5.2, "PLACE_SEEDS", "Place seeds on cotton"),
    (5.2, 6.0, "TAKE_DROPPER", "Retrieve / use dropper"),
    (6.0, 10.6, "ADD_WATER", "Add water"),
]

EXPECTED_ORDER = [x[2] for x in DEMO_SEGMENTS if x[2] != "SETUP"]


def header(title, subtitle):
    st.markdown(f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


def step_card(i, active=True):
    code, name = ACTIVITIES[i]
    cls = "step done" if active else "step"
    mark = "✓" if active else str(i + 1)
    st.markdown(
        f'<div class="{cls}"><div class="num">{mark}</div><div><b>{name}</b><br><span class="small">{code}</span></div></div>',
        unsafe_allow_html=True,
    )


def current_demo_segment(t):
    for start, end, code, name in DEMO_SEGMENTS:
        if start <= t < end:
            return code, name, start, end
    return DEMO_SEGMENTS[-1][2], DEMO_SEGMENTS[-1][3], DEMO_SEGMENTS[-1][0], DEMO_SEGMENTS[-1][1]


def expected_next(current_code):
    if current_code == "SETUP":
        return EXPECTED_ORDER[0]
    try:
        idx = EXPECTED_ORDER.index(current_code)
        return EXPECTED_ORDER[idx + 1] if idx + 1 < len(EXPECTED_ORDER) else "COMPLETE"
    except ValueError:
        return EXPECTED_ORDER[0]


def status_panel(current_code, expected_code):
    if current_code == expected_code or (current_code == "SETUP" and expected_code == "RETRIEVE_COTTON"):
        st.markdown(
            f'<div class="alertgood"><b>✓ PROCEDURE OK</b><br>Recognized activity: <b>{current_code}</b><br>Expected state: <b>{expected_code}</b><br><span class="small">No procedural deviation detected.</span></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="alerterr"><b>⚠ PROCEDURE DEVIATION</b><br>Recognized activity: <b>{current_code}</b><br>Expected state: <b>{expected_code}</b><br><span class="small">Operator guidance: return to the expected experiment step.</span></div>',
            unsafe_allow_html=True,
        )


with st.sidebar:
    st.markdown("# 🚀 HAR SYSTEM")
    st.caption("ISRO • On-board BAS Experiment Monitor")
    st.divider()
    page = st.radio(
        "Navigation",
        [
            "Mission Dashboard",
            "Upload Video",
            "Live Camera",
            "Demo Video",
            "Procedure & Alerts",
            "System Architecture",
            "Dataset & Model",
        ],
        label_visibility="collapsed",
    )
    st.divider()
    st.markdown("**SYSTEM STATUS**")
    st.markdown('<span class="pill ready">AI PIPELINE READY</span>', unsafe_allow_html=True)
    st.caption("SIH 2026 • SIH26174")


if page == "Mission Dashboard":
    header("HAR SYSTEM ISRO", "AI-assisted Human Activity Recognition for On-board BAS Experiments")
    a, b, c, d = st.columns(4)
    for col, label, value in [
        (a, "Experiment", "Seed Handling"),
        (b, "Activity classes", "6"),
        (c, "Frame features", "206"),
        (d, "Temporal window", "32 frames"),
    ]:
        with col:
            st.markdown(f'<div class="metric"><div class="label">{label}</div><div class="value">{value}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section">Mission demonstration</div>', unsafe_allow_html=True)
    left, right = st.columns([1.55, 1])
    with left:
        if DEMO_VIDEO.exists():
            st.video(str(DEMO_VIDEO))
        st.markdown('<div class="notice"><b>Demo mode:</b> the prepared video uses the expected experiment sequence to demonstrate the intended end-to-end judge experience. The production classifier can replace this demonstration layer without changing the dashboard workflow.</div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="card"><div class="card-title">Recognition → validation → alert</div>', unsafe_allow_html=True)
        for i in range(6):
            step_card(i, True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section">On-board processing chain</div>', unsafe_allow_html=True)
    cols = st.columns(7)
    pipe = [
        ("01", "VIDEO", "Input"),
        ("02", "YOLO", "Objects"),
        ("03", "BYTE TRACK", "Tracking"),
        ("04", "MEDIAPIPE", "Hands"),
        ("05", "206 FEATURES", "Frame vector"),
        ("06", "32-FRAME", "Temporal window"),
        ("07", "HAR + STATE", "Activity + alert"),
    ]
    for col, (n, t, s) in zip(cols, pipe):
        with col:
            st.markdown(f'<div class="pipe"><span class="small">{n}</span><b>{t}</b><span class="small">{s}</span></div>', unsafe_allow_html=True)


elif page == "Upload Video":
    header("Upload Video", "Run an experiment recording through the presentation-ready recognition interface")
    uploaded = st.file_uploader("Upload experiment video", type=["mp4", "mov", "avi", "mkv"])

    if uploaded is None:
        st.markdown('<div class="notice"><b>How this works:</b> select a BAS experiment recording. The dashboard displays the video, the recognized activity, the expected procedure state, and an alert whenever those states differ.</div>', unsafe_allow_html=True)
    else:
        st.video(uploaded)
        st.success(f"Video loaded: {uploaded.name}")
        st.markdown('<div class="section">AI recognition demonstration</div>', unsafe_allow_html=True)
        st.caption("The current dashboard demonstrates the intended recognition/validation behavior. Replace the expected-output layer with the final trained inference service when its accuracy is ready.")
        t = st.slider("Demo timeline position (seconds)", 0.0, 10.6, 2.5, 0.1)
        code, name, start, end = current_demo_segment(t)
        expected = code if code != "SETUP" else "RETRIEVE_COTTON"
        a, b, c = st.columns(3)
        with a:
            st.markdown(f'<div class="metric"><div class="label">AI activity</div><div class="value">{name}</div><div class="small">{code}</div></div>', unsafe_allow_html=True)
        with b:
            st.markdown(f'<div class="metric"><div class="label">Procedure state</div><div class="value">{expected}</div><div class="small">Expected next action</div></div>', unsafe_allow_html=True)
        with c:
            st.markdown(f'<div class="metric"><div class="label">Recognition confidence</div><div class="value">94%</div><div class="small">Demonstration value</div></div>', unsafe_allow_html=True)
        status_panel(code, expected)


elif page == "Live Camera":
    header("Live Camera", "Camera interface for real-time experiment observation")
    left, right = st.columns([1.2, 1])
    with left:
        camera = st.camera_input("Open camera / capture experiment frame")
        if camera is not None:
            st.image(camera, caption="Latest captured experiment frame", use_container_width=True)
    with right:
        st.markdown('<div class="card"><div class="card-title">Recognition preview</div><div class="small">This interface is ready for the live inference function. For the presentation, select the activity below to demonstrate the downstream procedure-validation behavior.</div></div>', unsafe_allow_html=True)
        selected = st.selectbox("Simulate recognized activity", ["SETUP"] + [x[0] for x in ACTIVITIES], format_func=lambda x: "Experiment setup" if x == "SETUP" else dict(ACTIVITIES)[x])
        expected = st.selectbox("Expected procedure state", [x[0] for x in ACTIVITIES], index=0, format_func=lambda x: dict(ACTIVITIES)[x])
        confidence = st.slider("Demonstration confidence", 0.50, 0.99, 0.94, 0.01)
        st.markdown(f'<div class="metric"><div class="label">Current AI activity</div><div class="value">{("Experiment setup" if selected == "SETUP" else dict(ACTIVITIES)[selected])}</div><div class="small">Confidence: {confidence:.0%}</div></div>', unsafe_allow_html=True)
        status_panel(selected, expected)
    st.markdown('<div class="notice" style="margin-top:14px"><b>Integration point:</b> the camera widget is the front-end input. The final YOLO + ByteTrack + MediaPipe + HAR inference service can feed its activity directly into this same recognition panel.</div>', unsafe_allow_html=True)


elif page == "Demo Video":
    header("Demo Video", "Complete seed-handling demonstration with expected AI recognition and procedure-state validation")
    if DEMO_VIDEO.exists():
        st.video(str(DEMO_VIDEO))
    st.markdown('<div class="section">AI recognition timeline</div>', unsafe_allow_html=True)
    t = st.slider("Move through the experiment timeline", 0.0, 10.6, 2.0, 0.1)
    code, name, start, end = current_demo_segment(t)
    expected = code if code != "SETUP" else "RETRIEVE_COTTON"
    next_action = expected_next(code)
    a, b, c = st.columns(3)
    with a:
        st.markdown(f'<div class="metric"><div class="label">Recognized activity</div><div class="value">{name}</div><div class="small">{code}</div></div>', unsafe_allow_html=True)
    with b:
        st.markdown(f'<div class="metric"><div class="label">Expected state</div><div class="value">{expected}</div><div class="small">Procedure validator</div></div>', unsafe_allow_html=True)
    with c:
        st.markdown(f'<div class="metric"><div class="label">Next expected action</div><div class="value">{next_action}</div><div class="small">State-machine output</div></div>', unsafe_allow_html=True)
    status_panel(code, expected)

    st.markdown('<div class="section">Expected recognition sequence</div>', unsafe_allow_html=True)
    rows = []
    for start, end, code, name in DEMO_SEGMENTS:
        rows.append([f"{start:.1f}–{end:.1f}s", code, name, "✓ Expected"])
    st.dataframe(pd.DataFrame(rows, columns=["Time", "Activity ID", "Activity", "Validation"]), use_container_width=True, hide_index=True)
    st.markdown('<div class="notice"><b>Judge-facing explanation:</b> “The video is the camera input. The HAR model identifies the human activity. A procedure-state validator checks whether that activity is the expected next step and raises an alert if it is not.”</div>', unsafe_allow_html=True)


elif page == "Procedure & Alerts":
    header("Procedure & Alerts", "State-machine view showing how activity recognition becomes experiment guidance")
    left, right = st.columns([1, 1.15])
    with left:
        st.markdown('<div class="section" style="margin-top:0">Canonical procedure</div>', unsafe_allow_html=True)
        for i in range(6):
            step_card(i, True)
    with right:
        st.markdown('<div class="section" style="margin-top:0">Alert demonstration</div>', unsafe_allow_html=True)
        actual = st.selectbox("Recognized activity", [x[0] for x in ACTIVITIES], format_func=lambda x: dict(ACTIVITIES)[x])
        expected = st.selectbox("Expected activity", [x[0] for x in ACTIVITIES], index=1, format_func=lambda x: dict(ACTIVITIES)[x])
        status_panel(actual, expected)
        st.markdown('<div class="section">Example operational logic</div>', unsafe_allow_html=True)
        st.markdown('<div class="card"><b>1. Observe</b><br><span class="small">Camera frame → object/hand detection → 206-dimensional feature vector.</span><br><br><b>2. Recognize</b><br><span class="small">32-frame temporal window → HAR activity.</span><br><br><b>3. Validate</b><br><span class="small">Current activity → expected experiment state.</span><br><br><b>4. Guide</b><br><span class="small">If states differ → operator alert / corrective instruction.</span></div>', unsafe_allow_html=True)


elif page == "System Architecture":
    header("System Architecture", "Edge-oriented processing path for on-board experiment monitoring")
    st.markdown('<div class="pipeline">' + ''.join([
        f'<div class="pipe"><span class="small">{n}</span><b>{t}</b><span class="small">{s}</span></div>' + ('<div class="arrow">→</div>' if n != "07" else '')
        for n, t, s in [
            ("01", "Video Input", "Experiment camera"),
            ("02", "Object Detection", "YOLO"),
            ("03", "Tracking + Pose", "ByteTrack + MediaPipe"),
            ("04", "Temporal Features", "32 × 206"),
            ("05", "Activity Recognition", "HAR classifier"),
            ("06", "Procedure Validation", "Experiment state"),
            ("07", "Operator Guidance", "Alerts / instructions"),
        ]
    ]) + '</div>', unsafe_allow_html=True)
    st.markdown('<div class="section">Implemented project contract</div>', unsafe_allow_html=True)
    st.dataframe(pd.DataFrame([
        ["Object classes", "5"],
        ["Hand landmarks", "126 / frame"],
        ["Object-object distances", "10 / frame"],
        ["Hand-object distances", "10 / frame"],
        ["Total frame features", "206"],
        ["Temporal window", "32 frames"],
        ["Activity classes", "6"],
    ], columns=["Component", "Value"]), use_container_width=True, hide_index=True)
    st.markdown('<div class="notice"><b>Deployment principle:</b> the detection, tracking, pose, feature extraction and recognition components can be stored locally on the target computing system, allowing the workflow to operate without depending on an internet connection.</div>', unsafe_allow_html=True)


elif page == "Dataset & Model":
    header("Dataset & Model", "Development artifacts and activity-recognition interface")
    a, b, c, d = st.columns(4)
    for col, label, value in [(a, "Recordings", "117"), (b, "Training sequences", "1,334"), (c, "Validation sequences", "313"), (d, "Test sequences", "294")]:
        with col:
            st.markdown(f'<div class="metric"><div class="label">{label}</div><div class="value">{value}</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="section">Activity classes</div>', unsafe_allow_html=True)
    st.dataframe(pd.DataFrame([[i, c, n] for i, (c, n) in enumerate(ACTIVITIES)], columns=["ID", "Activity ID", "Human-readable activity"]), use_container_width=True, hide_index=True)
    st.markdown('<div class="section">Model input contract</div>', unsafe_allow_html=True)
    st.code("X_train = (1334, 32, 206)\nX_val   = (313, 32, 206)\nX_test  = (294, 32, 206)\nframe features = 206\nsequence length = 32", language="text")
    st.markdown('<div class="notice"><b>Important:</b> dataset counts and feature dimensions are development artifacts. The dashboard deliberately separates the presentation demonstration from measured model-performance claims.</div>', unsafe_allow_html=True)


st.markdown('<div class="footer">HAR SYSTEM ISRO • SIH26174 • Human Activity Recognition for On-board BAS Experiments • Presentation Prototype</div>', unsafe_allow_html=True)
