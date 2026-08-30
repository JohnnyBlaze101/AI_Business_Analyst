from data_loader import load_data

from kpi_engine import run_kpi_analysis

from driver_engine import (
    calculate_regional_drivers,
    build_driver_ranking
)

from recommendation_engine import (
    generate_recommendations
)


def generate_insight():
    """
    Run the complete KPI intelligence pipeline.
    """

    # ============================================
    # 1. Load data
    # ============================================

    sales, marketing, product = load_data()

    # ============================================
    # 2. KPI analysis
    # ============================================

    kpi_result = run_kpi_analysis(
        sales
    )

    # ============================================
    # 3. Regional + driver analysis
    # ============================================

    regional_result = calculate_regional_drivers(
        sales,
        marketing,
        product
    )

    primary_region = (
        regional_result["primary_region"]
    )

    drivers = regional_result["drivers"]

    # ============================================
    # 4. Driver ranking
    # ============================================

    driver_ranking = build_driver_ranking(
        drivers
    )

    # ============================================
    # 5. Recommendations
    # ============================================

    recommendations = generate_recommendations(
        primary_region,
        driver_ranking
    )

    # ============================================
    # 6. Return complete insight
    # ============================================

    return {
        "kpi": {
            "name": "Revenue",
            "previous": kpi_result[
                "previous_revenue"
            ],
            "current": kpi_result[
                "current_revenue"
            ],
            "change": kpi_result[
                "percentage_change"
            ],
            "material": kpi_result[
                "is_material"
            ]
        },

        "primary_region": primary_region,

        "region_analysis":
            kpi_result[
                "region_analysis"
            ],

        "product_analysis":
            kpi_result[
                "product_analysis"
            ],

        "driver_ranking":
            driver_ranking,

        "recommendations":
            recommendations
    }


if __name__ == "__main__":

    insight = generate_insight()

    print("\n================================")
    print(" BUSINESS INTELLIGENCE.AI")
    print("================================")

    print(
        f"\nRevenue change: "
        f"{insight['kpi']['change']:.2f}%"
    )

    print(
        f"Material movement: "
        f"{insight['kpi']['material']}"
    )

    print(
        f"\nPrimary region: "
        f"{insight['primary_region']}"
    )

    print("\nDRIVER RANKING")
    print("--------------------")

    print(
        insight["driver_ranking"][
            [
                "rank",
                "driver",
                "combined_evidence",
                "confidence",
                "confidence_category",
                "abstain"
            ]
        ]
    )

    print("\nRECOMMENDATIONS")
    print("--------------------")

    for recommendation in insight[
        "recommendations"
    ]:

        print(
            f"\n{recommendation['driver']}"
        )

        print(
            recommendation["action"]
        )

        print(
            f"Owner: "
            f"{recommendation['owner']}"
        )
