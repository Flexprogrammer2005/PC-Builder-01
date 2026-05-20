import streamlit as st


def apply_theme():
    st.markdown(
        """
        <style>
        .stApp {
            background:
                linear-gradient(135deg, rgba(247, 250, 252, 0.94), rgba(235, 244, 241, 0.96)),
                radial-gradient(circle at top left, rgba(15, 139, 141, 0.14), transparent 34%),
                radial-gradient(circle at bottom right, rgba(199, 144, 37, 0.12), transparent 32%);
            color: #17202a;
        }
        .stApp, .stApp p, .stApp span, .stApp label, .stApp div,
        .stMarkdown, .stMarkdown p, .stCaptionContainer,
        [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p,
        [data-testid="stMetricLabel"], [data-testid="stMetricValue"],
        [data-testid="stMarkdownContainer"], [data-testid="stExpander"] {
            color: #111111 !important;
        }
        input, textarea, select,
        [data-baseweb="input"], [data-baseweb="input"] input,
        [data-baseweb="select"], [data-baseweb="select"] > div,
        [data-baseweb="select"] input, [data-baseweb="base-input"],
        [data-baseweb="base-input"] input, [data-baseweb="tag"],
        [data-baseweb="tag"] span {
            background: #ffffff !important;
            color: #111111 !important;
        }
        [data-baseweb="input"], [data-baseweb="select"] > div,
        [data-baseweb="base-input"] {
            border: 1px solid #cfd8dc !important;
            border-radius: 8px !important;
            box-shadow: none !important;
        }
        [data-baseweb="tag"] {
            background: #ffffff !important;
            border: 1px solid #0f8b8d !important;
            border-radius: 8px !important;
        }
        [data-baseweb="tag"] svg, [data-baseweb="select"] svg, button svg {
            color: #111111 !important;
            fill: #111111 !important;
        }
        [data-baseweb="popover"], [role="listbox"], [role="option"] {
            background: #ffffff !important;
            color: #111111 !important;
        }
        [role="option"]:hover, [aria-selected="true"] {
            background: #e9f4f3 !important;
            color: #111111 !important;
        }
        .block-container {
            max-width: 1220px;
            padding-top: 1.4rem;
            padding-bottom: 3rem;
        }
        h1, h2, h3 {
            letter-spacing: 0;
        }
        h1 {
            font-size: 3.3rem !important;
            line-height: 1.02 !important;
            margin-bottom: 0.4rem !important;
        }
        [data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #d7dde3;
            border-radius: 8px;
            padding: 14px 16px;
            box-shadow: 0 10px 30px rgba(23, 32, 42, 0.08);
        }
        [data-testid="stVerticalBlockBorderWrapper"] {
            border-color: #d7dde3 !important;
            border-radius: 8px !important;
            box-shadow: 0 12px 32px rgba(23, 32, 42, 0.08);
            background: rgba(255, 255, 255, 0.92);
        }
        div.stButton > button {
            background: #0f8b8d;
            color: white;
            border: 0;
            border-radius: 8px;
            min-height: 3rem;
            font-weight: 800;
        }
        div.stButton > button:hover {
            background: #0b6769;
            color: white;
            border: 0;
        }
        div[data-testid="stLinkButton"] a,
        div[data-testid="stLinkButton"] a:visited,
        div[data-testid="stLinkButton"] a:hover,
        div[data-testid="stLinkButton"] a:active {
            background: #ffffff !important;
            color: #111111 !important;
            border: 1px solid #0f8b8d !important;
            border-radius: 8px !important;
            box-shadow: none !important;
            font-weight: 800 !important;
            min-height: 2.4rem;
        }
        div[data-testid="stLinkButton"] a *,
        div[data-testid="stLinkButton"] a p,
        div[data-testid="stLinkButton"] a span {
            color: #111111 !important;
        }
        .hero-copy {
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid #d7dde3;
            border-radius: 8px;
            padding: 24px;
            box-shadow: 0 20px 50px rgba(23, 32, 42, 0.1);
        }
        .hero-kicker {
            color: #0b6769;
            font-weight: 900;
            text-transform: uppercase;
            font-size: 0.78rem;
        }
        .hero-subtext {
            color: #111111;
            font-size: 1.05rem;
            line-height: 1.6;
        }
        img {
            border-radius: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
