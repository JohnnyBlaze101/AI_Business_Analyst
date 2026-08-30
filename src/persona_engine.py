def generate_persona_narrative(
    insight,
    persona
):
    """
    Generate a persona-specific narrative
    from verified analytical results.
    """

    change = insight["kpi"]["change"]
    region = insight["primary_region"]

    ranking = insight["driver_ranking"]

    top_driver = ranking.iloc[0]

    driver = top_driver["driver"]
    confidence = top_driver["confidence"]
    confidence_category = (
        top_driver["confidence_category"]
    )

    if persona == "executive":

        return {
            "persona": "Executive",

            "headline": (
                f"Revenue declined {abs(change):.1f}%"
            ),

            "summary": (
                f"The primary impact is concentrated "
                f"in the {region} region. "
                f"{driver.replace('_', ' ').title()} "
                f"is the strongest evidence-backed "
                f"driver."
            ),

            "action": (
                "Prioritize investigation of the "
                f"{region} region and the "
                f"{driver.replace('_', ' ')} driver."
            ),

            "confidence": confidence_category
        }

    elif persona == "analyst":

        return {
            "persona": "Analyst",

            "headline": (
                f"Revenue movement: {change:.2f}%"
            ),

            "summary": (
                f"{region} is the largest regional "
                f"contributor to the movement. "
                f"The top-ranked driver is "
                f"{driver.replace('_', ' ')} "
                f"with evidence confidence of "
                f"{confidence:.1f}%."
            ),

            "action": (
                "Review the historical driver "
                "relationships, current movement "
                "and underlying source data before "
                "attributing causality."
            ),

            "confidence": confidence_category
        }

    else:

        return {
            "persona": persona,
            "headline": "Insight unavailable",
            "summary": "Unsupported persona.",
            "action": "Contact an analyst.",
            "confidence": "Low"
        }
