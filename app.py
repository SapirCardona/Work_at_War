import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="הטבות בעבודה בזמן מלחמה", layout="wide")

st.markdown(
    """
    <style>
    .stTabs [data-baseweb="tab"] {
        font-size: 18px;
        font-weight: bold;
        padding: 10px 24px;
    }
    .stTabs [role="tablist"] {
        gap: 20px;
        direction: rtl;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <h1 style='text-align: center; font-size: 40px; margin-bottom: 10px;'>
    הטבות בעבודה בזמן מלחמה
    </h1>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style='direction: rtl; text-align: center; font-size:18px; font-weight: bold; color: #555; padding-bottom: 10px;'>
    שימו לב: הנתונים מבוססים על 65 דיווחים של עובדים שמילאו את השאלון – ייתכנו פערים לעומת המצב בפועל.  
    אין לראות במידע מקור רשמי מטעם החברות.
    </div>
    """,
    unsafe_allow_html=True
)

def load_data():
    df = pd.read_excel("Work_at_war_data.xlsx")
    df.columns = [
        "Company",
        "Benefits",
        "Additional_Comment",
        "Got_Nothing",
        "Num_Benefits"
    ]

    df = df[df["Company"] != "Uknown"].copy()

    def clean_benefits(benefits):
        if pd.isna(benefits):
            return None
        cleaned = [b.strip() for b in benefits.split(",") if b.strip() not in ["כלום", "פיטורים"]]
        return ", ".join(cleaned) if cleaned else None

    df["Benefits"] = df["Benefits"].apply(clean_benefits)

    df["Num_Benefits"] = df["Benefits"].apply(lambda x: len(x.split(",")) if pd.notna(x) else 0)

    return df

df = load_data()

tabs = st.tabs(["תמונת מצב כללית", "החברה שלי", "חברות בולטות", "מה מספרים העובדים?"])

with tabs[0]:
    st.markdown("<h2 style='text-align: center;'>תמונת מצב כללית</h2>", unsafe_allow_html=True)

    min_benefits = df["Num_Benefits"].min()
    max_benefits = df["Num_Benefits"].max()

    col_min, col_max = st.columns(2)

    with col_min:
        st.markdown(
            f"""
            <div dir="rtl" style="background-color:#ffe6e6; padding:20px; border-radius:10px; text-align:center;">
                <h3 style="color:#b30000;">🔻 מינימום הטבות מדווחות</h3>
                <h1 style="color:#b30000;">{min_benefits}</h1>
            </div>
            """, unsafe_allow_html=True
        )

    with col_max:
        st.markdown(
            f"""
            <div dir="rtl" style="background-color:#e6ffe6; padding:20px; border-radius:10px; text-align:center;">
                <h3 style="color:#006600;">🟢 מקסימום הטבות מדווחות</h3>
                <h1 style="color:#006600;">{max_benefits}</h1>
            </div>
            """, unsafe_allow_html=True
        )

    st.markdown("---")

    all_benefits = df["Benefits"].dropna()
    benefit_counts = {}
    for row in all_benefits:
        for benefit in row.split(","):
            b = benefit.strip()
            if b:
                benefit_counts[b] = benefit_counts.get(b, 0) + 1

    benefit_df = pd.DataFrame.from_dict(benefit_counts, orient="index", columns=["count"]).sort_values(by="count",
                                                                                                       ascending=False)
    benefit_df["%"] = (benefit_df["count"] / len(df) * 100).round(1)
    benefit_df = benefit_df.reset_index().rename(columns={"index": "סוגי הטבות"})

    fig = px.bar(
        benefit_df,
        x="%",
        y="סוגי הטבות",
        orientation="h",  # הופך את הגרף לאופקי
        labels={"%": "אחוז מהארגונים", "סוגי הטבות": ""},
        title="שכיחות ההטבות",
    )

    fig.update_layout(
        title_x=0.5,  # מרכז את הכותרת
        font=dict(family="Arial", size=16),
        yaxis=dict(autorange="reversed"),
        margin=dict(l=100, r=40, t=60, b=40),
    )

    st.plotly_chart(fig, use_container_width=True)


with tabs[1]:
    st.markdown("<h2 style='text-align: center;'>?מה נתנה החברה שלי לעובדים</h2>", unsafe_allow_html=True)

    col2, col1 = st.columns(2)

    def extract_benefits(data, company):
        benefits_raw = data[data["Company"] == company]["Benefits"].dropna()
        benefits = set()
        for b in benefits_raw:
            for item in b.split(","):
                benefits.add(item.strip())
        if "כלום" in benefits and len(benefits) == 1:
            return []
        return sorted(benefits)

    benefits_1 = []
    benefits_2 = []

    with col2:
        company_1 = st.selectbox("בחר/י חברה לבדיקה:", [""] + sorted(df["Company"].dropna().unique()), key="main_company")
        if company_1:
            benefits_1 = extract_benefits(df, company_1)
            st.markdown(f"**הטבות שדווחו ב-{company_1}:**")
            if not benefits_1:
                st.write("לא דווחו הטבות")
            else:
                for i, b in enumerate(benefits_1, 1):
                    st.markdown(f"{i}. {b}")
            st.metric("כמות הטבות מדווחת", len(benefits_1))

    with col1:
        company_2 = st.selectbox("בחר/י חברה להשוואה (לא חובה):", [""] + sorted(df["Company"].dropna().unique()), key="compare_company")
        if company_2 and company_2 != company_1:
            benefits_2 = extract_benefits(df, company_2)
            st.markdown(f"**הטבות שדווחו ב-{company_2}:**")
            if not benefits_2:
                st.write("לא דווחו הטבות")
            else:
                for i, b in enumerate(benefits_2, 1):
                    st.markdown(f"{i}. {b}")
            st.metric("כמות הטבות מדווחת", len(benefits_2))

    if company_1 and company_2 and company_1 != company_2:
        st.markdown("<h2 style='text-align: center;'>השוואת הטבות בין חברות</h2>", unsafe_allow_html=True)
        all_benefits = sorted(set(benefits_1) | set(benefits_2))
        table_data = {
            "הטבה": all_benefits,
            company_1: ["✅" if b in benefits_1 else "❌" for b in all_benefits],
            company_2: ["✅" if b in benefits_2 else "❌" for b in all_benefits],
        }
        comparison_df = pd.DataFrame(table_data).set_index("הטבה")
        styled_html = comparison_df.to_html(escape=False, classes="comparison-table")

        html_output = f"""
        <div style="display: flex; justify-content: center; padding-top: 20px;">
          <div style="width: 70%;">
            <style>
              .comparison-table {{
                width: 100%;
                border-collapse: collapse;
                direction: rtl;
                font-size: 18px;
                color: #eee;
              }}
              .comparison-table th, .comparison-table td {{
                border: 1px solid #444;
                padding: 10px;
                text-align: center;
              }}
              .comparison-table th {{
                background-color: #d0f0f9;
                font-size: 20px;
                color: #000; /* 
              }}
            </style>
            {styled_html}
          </div>
        </div>
        """
        st.markdown(html_output, unsafe_allow_html=True)


with tabs[2]:
    max_benefits_df = df.groupby("Company", as_index=False)["Num_Benefits"].max()
    max_benefits_df.columns = ["Company", "Max Number of Benefits"]

    top_companies = max_benefits_df.sort_values(by="Max Number of Benefits", ascending=False).head(5)
    bottom_companies = max_benefits_df.sort_values(by="Max Number of Benefits", ascending=True).head(5)

    st.markdown("""
    <style>
    .benefit-text {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 6px;
        direction: rtl;
        text-align: right;
    }
    .green-text {
        color: #007700;
    }
    .red-text {
        color: #cc0000;
    }
    .benefits-box ol {
        font-size: 16px;
        line-height: 1.6;
        padding-right: 24px;
        margin: 0;
    }
    .benefits-box li {
        color: #007700;
    }
    @media (prefers-color-scheme: dark) {
        .green-text {
            color: #90ee90;
        }
        .red-text {
            color: #ffaaaa;
        }
        .benefits-box li {
            color: #90ee90;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h3 style='text-align: center;'>🏆 הכי הרבה הטבות</h3>", unsafe_allow_html=True)
        for _, row in top_companies.iterrows():
            company_name = row["Company"]
            num_benefits = row["Max Number of Benefits"]

            st.markdown(
                f"<div class='benefit-text green-text'>{company_name} – {num_benefits} הטבות</div>",
                unsafe_allow_html=True
            )

            benefits = df[df["Company"] == company_name]["Benefits"].dropna()
            unique_benefits = set()
            for item in benefits:
                for b in item.split(","):
                    b = b.strip()
                    if b and b not in ["כלום", "פיטורים"]:
                        unique_benefits.add(b)

            if unique_benefits:
                benefit_list = sorted(unique_benefits)
                styled_list = "".join(f"<li>{b}</li>" for b in benefit_list)

                with st.expander("לצפייה ברשימת ההטבות"):
                    st.markdown(f"""
                        <div class='benefits-box'>
                            <ol>{styled_list}</ol>
                        </div>
                    """, unsafe_allow_html=True)

    with col2:
        st.markdown("<h3 style='text-align: center;'>🔻 הכי מעט הטבות</h3>", unsafe_allow_html=True)
        for _, row in bottom_companies.iterrows():
            company_name = row["Company"]
            num_benefits = row["Max Number of Benefits"]

            st.markdown(
                f"<div class='benefit-text red-text'>{company_name} – {num_benefits} הטבות</div>",
                unsafe_allow_html=True
            )

            if num_benefits == 0:
                st.markdown("<div class='red-text' style='direction: rtl; text-align: right;'>לא דווחו הטבות כלל.</div>", unsafe_allow_html=True)
            else:
                benefits = df[df["Company"] == company_name]["Benefits"].dropna()
                unique_benefits = set()
                for item in benefits:
                    for b in item.split(","):
                        b = b.strip()
                        if b and b not in ["כלום", "פיטורים"]:
                            unique_benefits.add(b)

                if unique_benefits:
                    benefit_list = sorted(unique_benefits)
                    styled_list = "".join(f"<li>{b}</li>" for b in benefit_list)

                    with st.expander("לצפייה ברשימת ההטבות"):
                        st.markdown(f"""
                            <div class='benefits-box'>
                                <ol>{styled_list}</ol>
                            </div>
                        """, unsafe_allow_html=True)

with tabs[3]:
    st.markdown("<h2 style='text-align: center;'>?מה מספרים העובדים</h2>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("""
    <style>
    .feedback-box {
        padding: 12px 0;
        direction: rtl;
        text-align: right;
    }
    .feedback-text {
        font-size: 16px;
        line-height: 1.7;
        margin: 0 0 6px 0;
    }
    .feedback-source {
        font-weight: bold;
        font-size: 15px;
        text-align: left;
        margin: 0;
    }
    .green-text {
        color: #007700;
    }
    .red-text {
        color: #cc0000;
    }
    @media (prefers-color-scheme: dark) {
        .green-text {
            color: #90ee90;
        }
        .red-text {
            color: #ff9999;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    col_pos, col_neg = st.columns(2)

    with col_pos:
        st.markdown("<h4 style='text-align: center;' class='green-text'>💚 פידבקים חיוביים</h4>", unsafe_allow_html=True)
        positive_quotes = [
            ("Gotfriends", "הייתה הבנה שיש קושי בתפוקה ונירמלו את זה, מה שעזר לי באופן אישי לא לחשוש מה יקרה אם התפוקה תרד ובכל- בחלק מהימים התפוקה אפילו הייתה מעל הממוצע"),
            ("Apple", "אחרי שיחה קצרה על הקשיים אושר מענק כספי מכובד"),
            ("LinkedIn", "המון הכלה והבנה למצב"),
            ("Mastercard", "פינוי למלון לאילת למעוניינים"),
        ]
        for company, quote in positive_quotes:
            st.markdown(f"""
            <div class='feedback-box green-text'>
                <p class='feedback-text'>{quote}</p>
                <p class='feedback-source'>— {company}</p>
            </div>
            """, unsafe_allow_html=True)

    with col_neg:
        st.markdown("<h4 style='text-align: center;' class='red-text'>🔻 פידבקים שליליים</h4>", unsafe_allow_html=True)
        negative_quotes = [
            ("The Phoenix", "כל עוד הנחיות פיקוד העורף מאפשרות הגעה פיזית הם נצמדים לזה. תחושה לא נעימה כי גם כשאפשר להגיע אנשים לא רוצים תמיד לבוא כי הם מפחדים"),
            ("Metropoline", "הייתי מצפה למתן מענה אנושי יותר לצרכים ולא רק עבודה מהבית"),
            ("Cato Networks", "נתקעתי בחו\"ל. המנהל שלי לא עדכן אף אחד. HR דיברו איתי פעם אחת כחלק מסבב טלפונים שעשו לכל הישראלים."),
        ]
        for company, quote in negative_quotes:
            st.markdown(f"""
            <div class='feedback-box red-text'>
                <p class='feedback-text'>{quote}</p>
                <p class='feedback-source'>— {company}</p>
            </div>
            """, unsafe_allow_html=True)