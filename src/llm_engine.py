import os
from xmlrpc import client

from dotenv import load_dotenv
from google import genai


load_dotenv()


def generate_narrative(insight, persona):
    """
    Use Gemini only for narrative synthesis.

    Quantitative values are produced by the
    deterministic and ML engines.
    """

    api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    if not api_key:
        return (
            "Gemini API key not found. "
            "Please configure GEMINI_API_KEY "
            "in the .env file."
        )

    client = genai.Client(
        api_key=api_key
    )

    kpi = insight["kpi"]

    region = insight[
        "primary_region"
    ]

    drivers = insight[
        "driver_ranking"
    ]

    top_driver = drivers.iloc[0]

    driver_name = (
        top_driver["driver"]
        .replace("_", " ")
        .title()
    )

    confidence = (
        top_driver["confidence"]
    )

    recommendation = (
        insight["recommendations"][0]
    )

    prompt = f"""
You are an enterprise business intelligence analyst.

Generate a concise business narrative using
ONLY the verified evidence provided below.

IMPORTANT RULES:

- Do not invent numbers.
- Do not change numerical values.
- Do not calculate new metrics.
- Do not claim causality as proven.
- Clearly distinguish statistical evidence
  from causal certainty.
- Mention uncertainty when appropriate.

VERIFIED ANALYTICAL EVIDENCE

KPI:
Revenue

Previous revenue:
{kpi['previous']}

Current revenue:
{kpi['current']}

Revenue change:
{kpi['change']:.2f}%

Primary region:
{region}

Top candidate driver:
{driver_name}

Driver change:
{top_driver['current_change']:.2f}%

Statistical evidence:
{top_driver['statistical_evidence']:.3f}

ML evidence:
{top_driver['ml_evidence']:.3f}

Combined evidence:
{top_driver['combined_evidence']:.3f}

Evidence confidence:
{confidence:.1f}%

Recommended action:
{recommendation['action']}

Recommended owner:
{recommendation['owner']}

PERSONA:
{persona}

If the persona is executive:
Focus on business impact, priority and action.
Keep the explanation concise.

If the persona is analyst:
Focus on evidence, methodology and uncertainty.

Structure the response as:

1. What happened
2. What the evidence suggests
3. Recommended action

Use professional business language.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:

        return (
            "Gemini is temporarily unavailable. "
            "The quantitative analysis is still available "
            "from the deterministic and ML engines.\n\n"
            f"Technical status: {str(e)}"
        )

if __name__ == "__main__":

    from insight_engine import generate_insight

    insight = generate_insight()

    result = generate_narrative(
        insight,
        "executive"
    )

    print("\nGEMINI NARRATIVE")
    print("--------------------")
    print(result)