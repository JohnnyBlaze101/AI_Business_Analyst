import sys
import time

sys.path.append("src")

import streamlit as st
import plotly.express as px

from insight_engine import generate_insight
from persona_engine import generate_persona_narrative
from security import filter_insight_for_role

from data_loader import load_data
from kpi_engine import calculate_revenue_kpi

from llm_engine import generate_narrative

# ============================================
# Page configuration
# ============================================

st.set_page_config(
    page_title="BusinessIntelligence.ai",
    page_icon="📊",
    layout="wide"
)


# ============================================
# Title
# ============================================

st.title("BusinessIntelligence.ai")

st.caption(
    "KPI Intelligence → Evidence → Action"
)


# ============================================
# Sidebar
# ============================================

st.sidebar.header("Analysis Controls")

role = st.sidebar.selectbox(
    "User Role",
    [
        "executive",
        "analyst",
        "regional_manager"
    ]
)

demo_mode = st.sidebar.selectbox(
    "Analysis Mode",
    [
        "Normal",
        "Low Evidence Demo"
    ]
)


# ============================================
# Generate insight
# ============================================

start_time = time.time()

insight = generate_insight()

analysis_time = time.time() - start_time


# ============================================
# Low-confidence demonstration
# ============================================

if demo_mode == "Low Evidence Demo":

    insight["driver_ranking"] = (
        insight["driver_ranking"].copy()
    )

    insight["driver_ranking"]["confidence"] = 35.0

    insight["driver_ranking"][
        "confidence_category"
    ] = "Low"

    insight["driver_ranking"][
        "abstain"
    ] = True

    st.warning(
        "⚠️ Low-confidence scenario enabled. "
        "The system will abstain from driver attribution."
    )


# ============================================
# Apply role-based security
# ============================================

filtered_insight = filter_insight_for_role(
    insight,
    role
)


# ============================================
# Persona narrative
# ============================================

# Regional managers use the executive-style
# narrative because their focus is action.

if role == "analyst":

    persona_key = "analyst"

else:

    persona_key = "executive"


narrative = generate_persona_narrative(
    insight,
    persona_key
)


# ============================================
# KPI cards
# ============================================

col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Revenue",
        f"₹{filtered_insight['kpi']['current']:,.0f}",
        f"{filtered_insight['kpi']['change']:.2f}%"
    )


with col2:

    st.metric(
        "Primary Region",
        filtered_insight["primary_region"]
    )


with col3:

    if "driver_ranking" in filtered_insight:

        top_driver = filtered_insight[
            "driver_ranking"
        ].iloc[0]

        st.metric(
            "Top Driver",
            top_driver["driver"]
            .replace("_", " ")
            .title()
        )

    else:

        st.metric(
            "Top Driver",
            "Restricted"
        )


# ============================================
# Narrative
# ============================================

st.header(
    narrative["headline"]
)

st.write(
    narrative["summary"]
)

st.info(
    narrative["action"]
)

# ============================================
# Gemini AI Narrative
# ============================================

st.subheader("AI Business Narrative")

if st.button("Generate Gemini Insight"):

    with st.spinner(
        "Gemini is synthesizing the insight..."
    ):

        ai_narrative = generate_narrative(
            insight,
            persona_key
        )

    st.write(ai_narrative)
    
# ============================================
# Abstention warning
# ============================================

if "driver_ranking" in filtered_insight:

    low_confidence = (
        filtered_insight[
            "driver_ranking"
        ]["abstain"].any()
    )

    if low_confidence:

        st.error(
            "⚠️ INSUFFICIENT EVIDENCE"
        )

        st.write(
            "The system cannot reliably attribute "
            "the KPI movement to a specific driver. "
            "Additional evidence or clarification "
            "is required before taking action."
        )

    else:

        st.success(
            "✓ Evidence sufficient for "
            "driver-level analysis"
        )


# ============================================
# Revenue chart
# ============================================

st.subheader("Revenue Trend")

sales, marketing, product = load_data()

monthly_revenue = calculate_revenue_kpi(
    sales
)

fig = px.line(
    monthly_revenue,
    x="date",
    y="revenue",
    markers=True,
    title="Monthly Revenue"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================
# Driver ranking
# ============================================

if "driver_ranking" in filtered_insight:

    st.subheader("Driver Evidence")

    driver_df = filtered_insight[
        "driver_ranking"
    ][
        [
            "rank",
            "driver",
            "combined_evidence",
            "confidence",
            "confidence_category"
        ]
    ].copy()

    driver_df["driver"] = (
        driver_df["driver"]
        .str.replace("_", " ")
        .str.title()
    )

    st.dataframe(
        driver_df,
        use_container_width=True,
        hide_index=True
    )


# ============================================
# Region analysis
# ============================================

if "region_analysis" in filtered_insight:

    st.subheader("Regional Contribution")

    region_df = filtered_insight[
        "region_analysis"
    ][
        [
            "region",
            "change",
            "percentage_change",
            "contribution_percentage"
        ]
    ]

    fig_region = px.bar(
        region_df,
        x="region",
        y="contribution_percentage",
        title="Share of Revenue Decline by Region"
    )

    st.plotly_chart(
        fig_region,
        use_container_width=True
    )


# ============================================
# Product analysis
# ============================================

if "product_analysis" in filtered_insight:

    st.subheader("Product Contribution")

    product_df = filtered_insight[
        "product_analysis"
    ][
        [
            "product",
            "change",
            "percentage_change",
            "contribution_percentage"
        ]
    ]

    st.dataframe(
        product_df,
        use_container_width=True,
        hide_index=True
    )


# ============================================
# Recommendations
# ============================================

if "recommendations" in filtered_insight:

    st.subheader("Recommended Actions")

    for recommendation in filtered_insight[
        "recommendations"
    ]:

        with st.expander(
            recommendation["driver"]
            .replace("_", " ")
            .title()
        ):

            if recommendation.get(
                "abstain",
                False
            ):

                st.warning(
                    "Recommendation withheld "
                    "because evidence is insufficient."
                )

            else:

                st.write(
                    recommendation["action"]
                )

                st.write(
                    f"**Owner:** "
                    f"{recommendation['owner']}"
                )

                st.write(
                    f"**Confidence:** "
                    f"{recommendation['confidence']:.1f}% "
                    f"({recommendation['confidence_category']})"
                )

                st.write(
                    f"**Monitoring:** "
                    f"{recommendation['monitoring']}"
                )


# ============================================
# Runtime telemetry
# ============================================

st.sidebar.divider()

st.sidebar.subheader(
    "Runtime Telemetry"
)

st.sidebar.metric(
    "Analysis latency",
    f"{analysis_time:.2f} sec"
)

st.sidebar.metric(
    "ML model calls",
    "1"
)

st.sidebar.metric(
    "LLM calls",
    "0"
)

st.sidebar.metric(
    "Estimated cost",
    "$0.00"
)


# ============================================
# Architecture note
# ============================================

st.sidebar.divider()

st.sidebar.caption(
    "Quantitative truth is generated by "
    "deterministic analytics and ML. "
    "LLM narrative generation is optional "
    "and does not determine KPI values."
)
