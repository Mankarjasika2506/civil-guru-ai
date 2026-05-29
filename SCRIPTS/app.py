import streamlit as st
import os
import time

st.set_page_config(
    page_title="Civil Guru",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Rajdhani:wght@300;400;500;600;700&display=swap');

* { margin: 0; padding: 0; box-sizing: border-box; }

.stApp {
    background: linear-gradient(135deg,
        #FFF5E6 0%,
        #FFF8F0 20%,
        #F0F7FF 40%,
        #F0FFF4 60%,
        #FFF5E6 80%,
        #FFF0E0 100%);
    background-attachment: fixed;
    font-family: 'Rajdhani', sans-serif;
}

.tricolor-bar {
    height: 5px;
    background: linear-gradient(90deg,
        #FF9933 0%, #FF9933 33%,
        #FFFFFF 33%, #FFFFFF 66%,
        #138808 66%, #138808 100%);
    width: 100%;
}

.glass-card {
    background: rgba(255,255,255,0.6);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255,153,51,0.2);
    border-radius: 20px;
    padding: 28px;
    margin: 10px 0;
    box-shadow: 0 8px 32px rgba(255,153,51,0.08);
}

.glass-card-green {
    background: rgba(255,255,255,0.6);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(19,136,8,0.2);
    border-radius: 20px;
    padding: 28px;
    margin: 10px 0;
    box-shadow: 0 8px 32px rgba(19,136,8,0.08);
}

.step-box {
    background: rgba(255,255,255,0.7);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,153,51,0.25);
    border-radius: 14px;
    padding: 14px 20px;
    margin: 8px 0;
    display: flex;
    align-items: center;
    gap: 14px;
    animation: slideIn 0.4s ease forwards;
    box-shadow: 0 4px 15px rgba(255,153,51,0.06);
}

@keyframes slideIn {
    from { opacity: 0; transform: translateX(-20px); }
    to { opacity: 1; transform: translateX(0); }
}

.step-done {
    border-color: rgba(19,136,8,0.4) !important;
    background: rgba(240,255,244,0.8) !important;
}

.step-icon {
    font-size: 20px;
    width: 38px;
    height: 38px;
    background: rgba(255,153,51,0.12);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.step-done .step-icon {
    background: rgba(19,136,8,0.12);
}

.step-text {
    font-family: 'Rajdhani', sans-serif;
    font-size: 15px;
    color: #444;
    letter-spacing: 0.5px;
}

.gs-pill {
    display: inline-block;
    padding: 10px 32px;
    border-radius: 50px;
    font-family: 'Cinzel', serif;
    font-size: 22px;
    font-weight: 700;
    letter-spacing: 4px;
    backdrop-filter: blur(10px);
}

.gs1-pill { background: rgba(255,69,0,0.15); border: 2px solid rgba(255,69,0,0.4); color: #CC2200; }
.gs2-pill { background: rgba(0,85,204,0.12); border: 2px solid rgba(0,85,204,0.3); color: #003380; }
.gs3-pill { background: rgba(19,136,8,0.12); border: 2px solid rgba(19,136,8,0.3); color: #0A5C04; }
.gs4-pill { background: rgba(155,0,255,0.1); border: 2px solid rgba(155,0,255,0.25); color: #4A0080; }

.verdict-pass {
    background: rgba(19,136,8,0.12);
    border: 2px solid rgba(19,136,8,0.3);
    color: #0A5C04;
    padding: 16px 32px;
    border-radius: 50px;
    font-family: 'Cinzel', serif;
    font-size: 18px;
    font-weight: 700;
    text-align: center;
    letter-spacing: 3px;
    backdrop-filter: blur(10px);
    animation: pulse 2s infinite;
}

.verdict-fail {
    background: rgba(204,0,0,0.1);
    border: 2px solid rgba(204,0,0,0.3);
    color: #880000;
    padding: 16px 32px;
    border-radius: 50px;
    font-family: 'Cinzel', serif;
    font-size: 18px;
    font-weight: 700;
    text-align: center;
    letter-spacing: 3px;
    backdrop-filter: blur(10px);
}

@keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(19,136,8,0.3); }
    50% { box-shadow: 0 0 0 10px rgba(19,136,8,0); }
}

.answer-box {
    background: rgba(255,255,255,0.7);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,153,51,0.2);
    border-left: 4px solid #FF9933;
    border-radius: 0 16px 16px 0;
    padding: 28px;
    font-family: 'Rajdhani', sans-serif;
    font-size: 17px;
    line-height: 1.9;
    color: #222;
    white-space: pre-wrap;
    box-shadow: 0 8px 32px rgba(255,153,51,0.06);
}

.metric-card {
    background: rgba(255,255,255,0.65);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255,153,51,0.2);
    border-radius: 16px;
    padding: 22px;
    text-align: center;
    box-shadow: 0 4px 20px rgba(255,153,51,0.06);
}

.metric-value {
    font-family: 'Cinzel', serif;
    font-size: 24px;
    color: #FF6600;
    font-weight: 700;
}

.metric-label {
    font-size: 11px;
    color: #888;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 6px;
}

.tag {
    display: inline-block;
    background: rgba(255,153,51,0.1);
    border: 1px solid rgba(255,153,51,0.3);
    border-radius: 50px;
    padding: 5px 16px;
    font-size: 13px;
    color: #CC5500;
    margin: 4px;
    letter-spacing: 1px;
    backdrop-filter: blur(8px);
}

.source-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(19,136,8,0.08);
    border: 1px solid rgba(19,136,8,0.2);
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 12px;
    color: #0A5C04;
    margin: 4px;
    letter-spacing: 1px;
    backdrop-filter: blur(8px);
}

.divider-tricolor {
    height: 2px;
    background: linear-gradient(90deg,
        rgba(255,153,51,0.4),
        rgba(255,255,255,0.6),
        rgba(19,136,8,0.4));
    margin: 20px 0;
    border-radius: 2px;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(0,0,128,0.3) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(255,153,51,0.35) !important;
    border-radius: 12px !important;
    color: #fafafa !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 16px !important;
    box-shadow: 0 2px 12px rgba(255,153,51,0.06) !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #FF9933 !important;
    box-shadow: 0 0 0 3px rgba(255,153,51,0.15) !important;
}

.stButton > button {
    background: linear-gradient(135deg, #FF9933, #E8821A) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 14px 40px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    box-shadow: 0 4px 20px rgba(255,153,51,0.3) !important;
    transition: all 0.3s !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(255,153,51,0.4) !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.6);
    backdrop-filter: blur(16px);
    border-radius: 30px;
    padding: 8px;
    gap: 4px;
    justify-content: center;
    border: 3px solid rgba(255,153,51,0.2);
    box-shadow: 0 4px 20px rgba(255,153,51,0.08);
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #888 !important;
    border-radius: 50px !important;
    padding: 10px 28px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 16px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    border: none !important;
    font-weight: 600 !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #FF9933, #E8821A) !important;
    color: #fff !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 15px rgba(255,153,51,0.3) !important;
}

.stTabs [data-baseweb="tab-border"],
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }

div[data-testid="stMarkdownContainer"] p {
    color: #333;
    font-family: 'Rajdhani', sans-serif;
    font-size: 15px;
}

.section-title {
    font-family: 'Cinzel', serif;
    font-size: 30px;
    color: #CC5500;
    letter-spacing: 3px;
    text-align: center;
}

.section-subtitle {
    color: #999;
    font-size: 13px;
    letter-spacing: 3px;
    text-align: center;
    text-transform: uppercase;
    margin-top: 8px;
}

/* Fix file uploader */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.7) !important;
    backdrop-filter: blur(10px) !important;
    border: 2px dashed rgba(255,153,51,0.4) !important;
    border-radius: 12px !important;
}

[data-testid="stFileUploader"] section {
    background: rgba(255,255,255,0.7) !important;
    border: none !important;
    border-radius: 12px !important;
}

[data-testid="stFileUploader"] button {
    background: linear-gradient(135deg, #FF9933, #E8821A) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
}

[data-testid="stFileUploader"] span {
    color: #006400 !important;
}

[data-testid="stFileDropzoneInstructions"] {
    color: #888 !important;
}

[data-testid="stFileUploaderDropzone"] {
    background: rgba(255,255,255,0.7) !important;
    border: 2px dashed rgba(255,153,51,0.4) !important;
    border-radius: 12px !important;
}

[data-testid="stAppViewContainer"] {
    border-left: 6px solid #FF9933;
    border-right: 6px solid #138808;
    border-top: 6px solid #FF9933;
    border-bottom: 6px solid #138808;
}

[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    top: 0;
    left: 6px;
    right: 6px;
    height: 6px;
    background: linear-gradient(90deg,
        #FF9933 0%, #FF9933 33%,
        #ffffff 33%, #ffffff 66%,
        #138808 66%, #138808 100%);
    z-index: 9999;
}

[data-testid="stAppViewContainer"]::after {
    content: '';
    position: fixed;
    bottom: 0;
    left: 6px;
    right: 6px;
    height: 6px;
    background: linear-gradient(90deg,
        #FF9933 0%, #FF9933 33%,
        #ffffff 33%, #ffffff 66%,
        #138808 66%, #138808 100%);
    z-index: 9999;
}
</style>
""", unsafe_allow_html=True)

# ── Hero ──
col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    st.image("logo_transparent.png", width=350)

st.markdown("""
<div style="text-align:center; padding:0 0 30px;">
    <div style="font-family:'Rajdhani',sans-serif; font-size:15px;
        color:#CC5500; letter-spacing:1px; text-transform:uppercase;">
        ज्ञान से सेवा , सेवा से उत्कृष्टता
    </div>
</div>
""", unsafe_allow_html=True)


# ── Tabs ──
tab1, tab2, tab3, tab4 = st.tabs([
    "Syllabus Mapper",
    "Fact Checker",
    "Answer Evaluator",
    "Answer Generator"
])

# ════════════════════════════════
# TAB 1 — SYLLABUS MAPPER
# ════════════════════════════════
with tab1:
    st.markdown("""
    <div style="padding:28px 0 20px;">
        <div class="section-title">SYLLABUS MAPPER</div>
        <div class="section-subtitle">Map Current Affairs → UPSC GS Papers</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        topic = st.text_input("", placeholder="Enter news headline or current affairs topic...", key="topic_input")

        if st.button("ANALYZE TOPIC →", use_container_width=True, key="analyze_btn"):
            if topic:
                step1 = st.empty()
                step1.markdown('<div class="step-box"><div class="step-icon">🔍</div><div class="step-text">Reading and understanding your query...</div></div>', unsafe_allow_html=True)
                time.sleep(0.8)

                step2 = st.empty()
                step2.markdown('<div class="step-box"><div class="step-icon">📚</div><div class="step-text">Searching documents from NCERT, PIB & PRS...</div></div>', unsafe_allow_html=True)
                time.sleep(0.6)

                step3 = st.empty()
                step3.markdown('<div class="step-box"><div class="step-icon">🧠</div><div class="step-text">AI agent analyzing UPSC syllabus mapping...</div></div>', unsafe_allow_html=True)

                from syllabus_mapper import map_to_syllabus
                result = map_to_syllabus(topic)

                if result is None:
                    result = {
                        "gs_paper": "GS2", "confidence": 0.0,
                        "subject": "GENERAL", "topic": topic,
                        "subtopic": "", "relevance": "Please try again.",
                        "question_types": [], "related_topics": [], "sources": []
                    }

                step4 = st.empty()
                step4.markdown('<div class="step-box step-done"><div class="step-icon">✅</div><div class="step-text">Analysis complete!</div></div>', unsafe_allow_html=True)
                time.sleep(0.4)

                step1.empty(); step2.empty(); step3.empty(); step4.empty()

                gs = result.get('gs_paper', 'GS1')
                gs_class = gs.lower().replace(" ", "")

                st.markdown(f"""
                <div style="text-align:center; margin:24px 0 20px;">
                    <div class="gs-pill {gs_class}-pill">{gs}</div>
                    <div style="color:#999; font-size:11px; letter-spacing:3px; margin-top:10px; text-transform:uppercase;">GS Paper Detected</div>
                </div>
                """, unsafe_allow_html=True)


                

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f'<div class="metric-card"><div class="metric-value">{result.get("subject","N/A")}</div><div class="metric-label">Subject</div></div>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<div class="metric-card"><div class="metric-value" style="font-size:17px">{result.get("topic","N/A")}</div><div class="metric-label">Topic</div></div>', unsafe_allow_html=True)

                st.markdown('<div class="divider-tricolor"></div>', unsafe_allow_html=True)

                st.markdown(f"""
                <div class="glass-card">
                    <div style="color:#999; font-size:11px; letter-spacing:3px; text-transform:uppercase; margin-bottom:10px;">WHY THIS MATTERS FOR UPSC</div>
                    <div style="color:#333; line-height:1.8; font-family:Rajdhani,sans-serif; font-size:16px;">{result.get("relevance","")}</div>
                </div>
                """, unsafe_allow_html=True)

                if result.get('related_topics'):
                    st.markdown('<div style="color:#999; font-size:11px; letter-spacing:3px; text-transform:uppercase; margin:16px 0 10px;">Related UPSC Topics</div>', unsafe_allow_html=True)
                    tags = "".join([f'<span class="tag">{t}</span>' for t in result.get('related_topics', [])])
                    st.markdown(tags, unsafe_allow_html=True)

                if result.get('sources'):
                    st.markdown('<div style="color:#999; font-size:11px; letter-spacing:3px; text-transform:uppercase; margin:16px 0 10px;">SOURCES USED</div>', unsafe_allow_html=True)
                    sources_html = "".join([f'<span class="source-badge">{s}</span>' for s in result.get('sources', [])])
                    st.markdown(sources_html, unsafe_allow_html=True)
                    
            else:
                st.warning("⚠️ Please enter a topic!")

# ════════════════════════════════
# TAB 2 — FACT CHECKER
# ════════════════════════════════
with tab2:
    st.markdown("""
    <div style="padding:28px 0 20px;">
        <div class="section-title">FACT CHECKER</div>
        <div class="section-subtitle">Verify Claims → PIB · PRS Official Sources</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        claim = st.text_area("", placeholder="Enter any news claim or statement to verify...", height=120, key="claim_input")

        st.markdown("""
        <div style="display:flex; gap:8px; margin-bottom:15px; flex-wrap:wrap;">
            <span class="source-badge">📰 PIB Press Releases</span>
            <span class="source-badge">⚖️ PRS Legislative</span>
            <span class="source-badge">🏛️ Official Govt Sources</span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("VERIFY CLAIM →", use_container_width=True, key="verify_btn"):
            if claim:
                step1 = st.empty()
                step1.markdown('<div class="step-box"><div class="step-icon">📥</div><div class="step-text">Receiving claim for verification...</div></div>', unsafe_allow_html=True)
                time.sleep(0.6)

                step2 = st.empty()
                step2.markdown('<div class="step-box"><div class="step-icon">🔎</div><div class="step-text">Searching PIB press releases...</div></div>', unsafe_allow_html=True)
                time.sleep(0.6)

                step3 = st.empty()
                step3.markdown('<div class="step-box"><div class="step-icon">⚖️</div><div class="step-text">Cross-referencing PRS legislative research...</div></div>', unsafe_allow_html=True)
                time.sleep(0.5)

                step4 = st.empty()
                step4.markdown('<div class="step-box"><div class="step-icon">🧠</div><div class="step-text">AI agent analyzing evidence...</div></div>', unsafe_allow_html=True)

                from fact_checker import verify_claim
                result = verify_claim(claim)

                step5 = st.empty()
                step5.markdown('<div class="step-box step-done"><div class="step-icon">✅</div><div class="step-text">Verification complete!</div></div>', unsafe_allow_html=True)
                time.sleep(0.3)

                step1.empty(); step2.empty(); step3.empty(); step4.empty(); step5.empty()

                verdict = result.get("verdict", "UNKNOWN")
                if verdict == "PASS":
                    st.markdown('<div class="verdict-pass">✅ VERIFIED — CLAIM IS ACCURATE</div>', unsafe_allow_html=True)
                elif verdict == "FAIL":
                    st.markdown('<div class="verdict-fail">❌ NOT VERIFIED — CLAIM IS INACCURATE</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="background:rgba(255,153,51,0.1); border:2px solid rgba(255,153,51,0.3); color:#CC5500; padding:16px 32px; border-radius:50px; text-align:center; font-family:Cinzel,serif; font-size:18px; font-weight:700; letter-spacing:3px;">⚠️ PARTIALLY VERIFIED</div>', unsafe_allow_html=True)

                st.markdown('<div class="divider-tricolor"></div>', unsafe_allow_html=True)

                st.markdown(f"""
                <div class="glass-card-green">
                    <div style="color:#999; font-size:11px; letter-spacing:3px; text-transform:uppercase; margin-bottom:10px;">Verification Report</div>
                    <div style="color:#222; line-height:1.8; white-space:pre-wrap; font-family:Rajdhani,sans-serif; font-size:15px;">{result.get("full_report","")}</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f'<div style="text-align:right; margin-top:10px; color:#aaa; font-size:12px; letter-spacing:2px;">{result.get("evidence_count",0)} OFFICIAL DOCUMENTS CHECKED</div>', unsafe_allow_html=True)
            else:
                st.warning("⚠️ Please enter a claim!")

# ════════════════════════════════
# TAB 3 — ANSWER EVALUATOR
# ════════════════════════════════
with tab3:
    st.markdown("""
    <div style="padding:28px 0 20px;">
        <div class="section-title">ANSWER EVALUATOR</div>
        <div class="section-subtitle">Upload Handwritten Answer → Get Instant Feedback</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        question = st.text_input("", placeholder="Enter the UPSC question...", key="eval_question")
        uploaded = st.file_uploader("📸 Upload photo of your handwritten answer", type=["jpg","jpeg","png"], key="eval_upload")

        if st.button("EVALUATE ANSWER →", use_container_width=True, key="eval_btn"):
            if uploaded and question:
                temp_path = "temp_eval.jpg"
                with open(temp_path, "wb") as f:
                    f.write(uploaded.getbuffer())

                ci, ct = st.columns([1, 1])
                with ci:
                    st.image(uploaded, caption="Your Answer", use_column_width=True)

                with ct:
                    step1 = st.empty()
                    step1.markdown('<div class="step-box"><div class="step-icon">📸</div><div class="step-text">Reading handwriting with OCR...</div></div>', unsafe_allow_html=True)
                    time.sleep(0.5)
                    step2 = st.empty()
                    step2.markdown('<div class="step-box"><div class="step-icon">📚</div><div class="step-text">Retrieving UPSC model context...</div></div>', unsafe_allow_html=True)
                    time.sleep(0.5)
                    step3 = st.empty()
                    step3.markdown('<div class="step-box"><div class="step-icon">🎓</div><div class="step-text">Evaluating as UPSC examiner...</div></div>', unsafe_allow_html=True)

                    from answer_evaluator_ocr import evaluate_handwritten_answer
                    result = evaluate_handwritten_answer(temp_path, question)

                    step4 = st.empty()
                    step4.markdown('<div class="step-box step-done"><div class="step-icon">✅</div><div class="step-text">Evaluation complete!</div></div>', unsafe_allow_html=True)
                    time.sleep(0.3)
                    step1.empty(); step2.empty(); step3.empty(); step4.empty()

                    if result:
                        import re
                        total_match = re.search(r"TOTAL\s*:\s*(\d+)/15", result)
                        total = int(total_match.group(1)) if total_match else 0
                        pct = int((total/15)*100)
                        color = "#138808" if total >= 10 else "#FF9933" if total >= 7 else "#CC0000"
                        label = 'EXCELLENT' if total>=12 else 'GOOD' if total>=9 else 'AVERAGE' if total>=6 else 'NEEDS IMPROVEMENT'

                        st.markdown(f"""
                        <div class="glass-card" style="text-align:center;">
                            <div style="font-family:'Cinzel',serif; font-size:64px; color:{color}; font-weight:700; line-height:1;">{total}</div>
                            <div style="color:#aaa; font-size:12px; letter-spacing:4px; margin:6px 0 14px;">OUT OF 15</div>
                            <div style="background:rgba(0,0,0,0.06); border-radius:50px; height:8px; overflow:hidden;">
                                <div style="background:linear-gradient(90deg,#FF9933,{color}); height:8px; width:{pct}%; border-radius:50px;"></div>
                            </div>
                            <div style="color:{color}; font-size:14px; letter-spacing:3px; margin-top:10px; font-family:'Cinzel',serif;">{label}</div>
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown('<div class="divider-tricolor"></div>', unsafe_allow_html=True)
                        st.text(result)

                if os.path.exists(temp_path):
                    os.remove(temp_path)
            else:
                st.warning("⚠️ Please upload image and enter question!")

# ════════════════════════════════
# TAB 4 — ANSWER GENERATOR
# ════════════════════════════════
with tab4:
    st.markdown("""
    <div style="padding:28px 0 20px;">
        <div class="section-title">ANSWER GENERATOR</div>
        <div class="section-subtitle">AI-Powered UPSC Mains Model Answers</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        question = st.text_area("", placeholder="Enter your UPSC mains question...", height=120, key="gen_question")

        if st.button("GENERATE ANSWER →", use_container_width=True, key="gen_btn"):
            if question:
                step1 = st.empty()
                step1.markdown('<div class="step-box"><div class="step-icon">🧩</div><div class="step-text">Detecting subject and GS paper...</div></div>', unsafe_allow_html=True)
                time.sleep(0.5)
                step2 = st.empty()
                step2.markdown('<div class="step-box"><div class="step-icon">📚</div><div class="step-text">Retrieving from NCERT + PIB + PRS...</div></div>', unsafe_allow_html=True)
                time.sleep(0.5)
                step3 = st.empty()
                step3.markdown('<div class="step-box"><div class="step-icon">⚡</div><div class="step-text">Reranking top relevant chunks...</div></div>', unsafe_allow_html=True)
                time.sleep(0.4)
                step4 = st.empty()
                step4.markdown('<div class="step-box"><div class="step-icon">✍️</div><div class="step-text">AI writing structured UPSC answer...</div></div>', unsafe_allow_html=True)

                import chromadb, ollama
                from sentence_transformers import SentenceTransformer, util
                from reranker import rerank_chunks

                MODEL = "llama3.2:3b"
                emb_model = SentenceTransformer("all-MiniLM-L6-v2")

                class EF:
                    def __call__(self, input): return emb_model.encode(input).tolist()
                    def name(self): return "all-MiniLM-L6-v2"
                    def embed_documents(self, input): return emb_model.encode(input).tolist()
                    def embed_query(self, input): return emb_model.encode(input).tolist()

                client = chromadb.PersistentClient(path="../db")
                collection = client.get_collection("civil_guru", embedding_function=EF())

                SUBJECTS = {
                    "ART&CULTURE": "art culture painting dance music sculpture cave prehistoric",
                    "HISTORY": "ancient medieval modern history mughal british empire dynasty",
                    "POLITY": "constitution parliament amendment president governor rights",
                    "ECONOMICS": "economy gdp inflation rbi monetary fiscal budget agriculture",
                    "GEOGRAPHY": "river mountain climate soil monsoon plateau environment disaster flood",
                    "ETHICS": "ethics integrity moral attitude aptitude governance values",
                    "SOCIOLOGY": "society caste tribe social culture religion community women",
                }

                q_emb = emb_model.encode(question, convert_to_tensor=True)
                best_sub, best_sc = "GENERAL", 0.0
                for sub, desc in SUBJECTS.items():
                    sc = util.cos_sim(q_emb, emb_model.encode(desc, convert_to_tensor=True)).item()
                    if sc > best_sc:
                        best_sc, best_sub = sc, sub

                try:
                    docs = collection.query(query_texts=[question], n_results=15, where={"subject": best_sub})["documents"][0]
                except:
                    docs = collection.query(query_texts=[question], n_results=15)["documents"][0]

                docs = rerank_chunks(question, docs, top_k=3)
                context = "\n\n".join(docs)

                response = ollama.chat(
                    model=MODEL,
                    messages=[{"role": "user", "content": f"""
You are a UPSC Mains topper. Write a complete structured answer.
RULES:
- Use only given context
- No references or bibliography
- Proper UPSC mains structure with Introduction, Body, Conclusion
- Include relevant facts and examples

Question: {question}
Context: {context}
"""}],
                    options={"num_predict": 800}
                )
                answer = response["message"]["content"]

                step5 = st.empty()
                step5.markdown('<div class="step-box step-done"><div class="step-icon">✅</div><div class="step-text">Answer generated!</div></div>', unsafe_allow_html=True)
                time.sleep(0.3)
                step1.empty(); step2.empty(); step3.empty(); step4.empty(); step5.empty()

                st.markdown(f"""
                <div style="display:flex; gap:10px; margin-bottom:20px; flex-wrap:wrap;">
                    <span class="source-badge">📚 {best_sub}</span>
                    <span class="source-badge">🎯 Confidence: {round(best_sc,2)}</span>
                    <span class="source-badge">📄 NCERT + PIB + PRS</span>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f'<div class="answer-box">{answer}</div>', unsafe_allow_html=True)

            else:
                st.warning("⚠️ Please enter a question!")

# ── Footer ──
st.markdown("""
<div style="
    height:2px;
    margin-top:40px;
    background: linear-gradient(
        90deg,
        transparent,
        #FFD700,
        #FFCC00,
        #FFD700,
        transparent
    );
    box-shadow: 0 0 12px rgba(255,215,0,0.7);
"></div>

<div style="
    text-align:center;
    padding:16px;
    color:#A020F0;
    font-family:'Rajdhani',sans-serif,bold;
    letter-spacing:2px;
    font-size:14px;
    text-shadow:0 0 10px rgba(255,215,0,0.5);
">
    CIVIL GURU · KNOW · ANALYZE · EXCEL
</div>
""", unsafe_allow_html=True)