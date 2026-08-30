def generate_recommendations(
    primary_region,
    driver_ranking
):
    """
    Generate business recommendations from
    evidence-ranked drivers.

    Recommendations are based on detected drivers,
    not hard-coded regions.
    """

    recommendations = []

    if primary_region is None:
        return recommendations

    for _, row in driver_ranking.iterrows():

        driver = row["driver"]
        confidence = row["confidence"]
        confidence_category = row["confidence_category"]
        abstain = row["abstain"]
        current_change = row["current_change"]

        # ---------------------------------------
        # Do not recommend action when evidence
        # is insufficient.
        # ---------------------------------------

        if abstain:
            recommendations.append({
                "driver": driver,
                "region": primary_region,
                "action": "Insufficient evidence for a reliable recommendation.",
                "owner": "Analyst",
                "confidence": confidence,
                "confidence_category": confidence_category,
                "monitoring": "Collect additional data before taking action."
            })

            continue

        # ---------------------------------------
        # Units sold
        # ---------------------------------------

        if driver == "units_sold":

            action = (
                f"Investigate the {primary_region} sales funnel "
                f"and identify the source of the unit-volume decline."
            )

            owner = "Regional Sales Manager"

            monitoring = (
                "Track weekly units sold and revenue "
                "for the affected region."
            )

        # ---------------------------------------
        # Website traffic
        # ---------------------------------------

        elif driver == "website_traffic":

            action = (
                f"Review digital traffic acquisition for "
                f"the {primary_region} region and identify "
                f"the channels responsible for the decline."
            )

            owner = "Marketing Manager"

            monitoring = (
                "Track weekly website traffic, campaign "
                "performance and conversion."
            )

        # ---------------------------------------
        # Marketing spend
        # ---------------------------------------

        elif driver == "marketing_spend":

            action = (
                f"Review the {primary_region} marketing "
                f"budget and identify whether reduced spend "
                f"affected demand generation."
            )

            owner = "Marketing Manager"

            monitoring = (
                "Track marketing spend, traffic and revenue "
                "after any budget adjustment."
            )

        # ---------------------------------------
        # Unknown driver
        # ---------------------------------------

        else:

            action = (
                f"Investigate the {driver} movement "
                f"within the {primary_region} region."
            )

            owner = "Business Analyst"

            monitoring = (
                "Monitor the driver and affected KPI "
                "for the next reporting period."
            )

        recommendations.append({
            "driver": driver,
            "region": primary_region,
            "action": action,
            "owner": owner,
            "confidence": confidence,
            "confidence_category": confidence_category,
            "current_change": current_change,
            "monitoring": monitoring
        })

    return recommendations

if __name__ == "__main__":

    from data_loader import load_data
    from driver_engine import (
        calculate_regional_drivers,
        calculate_driver_scores,
        build_driver_ranking
    )

    sales, marketing, product = load_data()

    result = calculate_regional_drivers(
        sales,
        marketing,
        product
    )

    driver_ranking = build_driver_ranking(
        result["drivers"]
    )

    recommendations = generate_recommendations(
        result["primary_region"],
        driver_ranking
    )

    print("\nRECOMMENDATIONS")
    print("--------------------")

    for recommendation in recommendations:

        print(
            f"\nDriver: "
            f"{recommendation['driver']}"
        )

        print(
            f"Region: "
            f"{recommendation['region']}"
        )

        print(
            f"Action: "
            f"{recommendation['action']}"
        )

        print(
            f"Owner: "
            f"{recommendation['owner']}"
        )

        print(
            f"Confidence: "
            f"{recommendation['confidence']:.2f}% "
            f"({recommendation['confidence_category']})"
        )

        print(
            f"Monitoring: "
            f"{recommendation['monitoring']}"
        )