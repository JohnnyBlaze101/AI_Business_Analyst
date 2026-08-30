import pandas as pd

from data_loader import load_data

from confidence_engine import (
    calculate_confidence,
    classify_confidence,
    should_abstain
)

from ml_driver_engine import (
    train_driver_model,
    calculate_ml_evidence
)

def calculate_regional_drivers(sales, marketing, product):
    """
    Analyze all regions and identify the region with the
    largest material revenue decline.

    The function does NOT assume which region is the problem.
    It discovers the region from the data.
    """

    # =====================================================
    # 1. Prepare dates
    # =====================================================

    sales = sales.copy()
    marketing = marketing.copy()
    product = product.copy()

    sales["date"] = pd.to_datetime(sales["date"])
    marketing["week"] = pd.to_datetime(marketing["week"])
    product["date"] = pd.to_datetime(product["date"])

    sales["month"] = sales["date"].dt.to_period("M")
    marketing["month"] = marketing["week"].dt.to_period("M")
    product["month"] = product["date"].dt.to_period("M")

    # =====================================================
    # 2. Calculate revenue for every region
    # =====================================================

    regional_revenue = (
        sales
        .groupby(["month", "region"])["revenue"]
        .sum()
        .reset_index()
    )

    months = sorted(regional_revenue["month"].unique())

    previous_month = months[-2]
    current_month = months[-1]

    previous_revenue = regional_revenue[
        regional_revenue["month"] == previous_month
    ]

    current_revenue = regional_revenue[
        regional_revenue["month"] == current_month
    ]

    region_comparison = previous_revenue.merge(
        current_revenue,
        on="region",
        suffixes=("_previous", "_current")
    )

    region_comparison["revenue_change"] = (
        region_comparison["revenue_current"]
        - region_comparison["revenue_previous"]
    )

    region_comparison["percentage_change"] = (
        region_comparison["revenue_change"]
        / region_comparison["revenue_previous"]
    ) * 100

    # =====================================================
    # 3. Calculate contribution to total revenue movement
    # =====================================================

    total_change = region_comparison["revenue_change"].sum()

    region_comparison["contribution_percentage"] = (
        region_comparison["revenue_change"]
        / total_change
    ) * 100

    # =====================================================
    # 4. Identify the largest declining region
    # =====================================================

    declining_regions = region_comparison[
        region_comparison["revenue_change"] < 0
    ]

    if declining_regions.empty:
        primary_region = None
    else:
        primary_region = declining_regions.loc[
            declining_regions["revenue_change"].idxmin(),
            "region"
        ]

    # =====================================================
    # 5. Calculate drivers for the identified region
    # =====================================================

    if primary_region is not None:

        region_sales = sales[
            sales["region"] == primary_region
        ]

        region_marketing = marketing[
            marketing["region"] == primary_region
        ]

        # -------------------------
        # Units + Revenue
        # -------------------------

        monthly_sales = (
            region_sales
            .groupby("month")
            .agg(
                units_sold=("units_sold", "sum"),
                revenue=("revenue", "sum")
            )
            .reset_index()
        )

        # -------------------------
        # Marketing
        # -------------------------

        monthly_marketing = (
            region_marketing
            .groupby("month")
            .agg(
                marketing_spend=("marketing_spend", "sum"),
                website_traffic=("website_traffic", "sum")
            )
            .reset_index()
        )

        # -------------------------
        # Combine regional data
        # -------------------------

        drivers = monthly_sales.merge(
            monthly_marketing,
            on="month",
            how="left"
        )

        # -------------------------
        # Sales-to-traffic proxy
        #
        # IMPORTANT:
        # This is NOT true conversion rate.
        # It is a derived proxy because the
        # available conversion data has no region.
        # -------------------------

        drivers["sales_to_traffic_ratio"] = (
            drivers["units_sold"]
            / drivers["website_traffic"]
        )

    else:
        drivers = pd.DataFrame()

    # =====================================================
    # 6. Product conversion is global/product-level
    # =====================================================

    monthly_conversion = (
        product
        .groupby("month")["conversion_rate"]
        .mean()
        .reset_index()
    )

    return {
        "region_comparison": region_comparison,
        "primary_region": primary_region,
        "drivers": drivers,
        "conversion": monthly_conversion
    }

def calculate_driver_changes(drivers):
    """
    Calculate July-to-August changes for the
    major regional business drivers.
    """

    if len(drivers) < 2:
        return pd.DataFrame()

    previous = drivers.iloc[-2]
    current = drivers.iloc[-1]

    driver_names = [
        "units_sold",
        "marketing_spend",
        "website_traffic",
        "sales_to_traffic_ratio"
    ]

    results = []

    for driver in driver_names:

        previous_value = previous[driver]
        current_value = current[driver]

        if previous_value == 0:
            percentage_change = 0
        else:
            percentage_change = (
                (current_value - previous_value)
                / previous_value
            ) * 100

        results.append({
            "driver": driver,
            "previous_value": previous_value,
            "current_value": current_value,
            "percentage_change": percentage_change
        })

    return pd.DataFrame(results)

def calculate_driver_scores(drivers):
    """
    Calculate evidence-based scores for regional drivers.

    The score combines:
    1. Historical correlation with revenue
    2. Magnitude of the current movement

    This is an analytical ranking, not proof of causality.
    """

    if len(drivers) < 3:
        return pd.DataFrame()

    driver_columns = [
        "units_sold",
        "marketing_spend",
        "website_traffic",
    ]

    results = []

    for driver in driver_columns:

        # ---------------------------------------
        # Historical relationship with revenue
        # ---------------------------------------

        correlation = drivers["revenue"].corr(
            drivers[driver]
        )

        if pd.isna(correlation):
            correlation = 0

        correlation_strength = abs(correlation)

        # ---------------------------------------
        # Current movement
        # ---------------------------------------

        previous_value = drivers.iloc[-2][driver]
        current_value = drivers.iloc[-1][driver]

        if previous_value == 0:
            percentage_change = 0
        else:
            percentage_change = (
                (current_value - previous_value)
                / previous_value
            ) * 100

        movement_strength = abs(
            percentage_change
        )

        results.append({
            "driver": driver,
            "correlation": correlation,
            "correlation_strength": correlation_strength,
            "current_change": percentage_change,
            "movement_strength": movement_strength
        })

    scores = pd.DataFrame(results)

    # ---------------------------------------
    # Normalize movement strength
    # ---------------------------------------

    max_movement = scores[
        "movement_strength"
    ].max()

    if max_movement == 0:
        scores["movement_score"] = 0
    else:
        scores["movement_score"] = (
            scores["movement_strength"]
            / max_movement
        )

    # ---------------------------------------
    # Evidence score
    # ---------------------------------------

    scores["evidence_score"] = (
        0.6 * scores["correlation_strength"]
        + 0.4 * scores["movement_score"]
    )

    # ---------------------------------------
    # Rank drivers
    # ---------------------------------------

    scores = scores.sort_values(
        "evidence_score",
        ascending=False
    ).reset_index(drop=True)

    scores["rank"] = (
        scores.index + 1
    )

    return scores

def build_driver_ranking(
    drivers,
    data_fresh=True,
    data_complete=True,
    contradictory=False
):
    """
    Combine statistical evidence, ML evidence,
    and confidence assessment into a final
    driver ranking.
    """

    # ---------------------------------------
    # Statistical evidence
    # ---------------------------------------

    statistical_scores = calculate_driver_scores(
        drivers
    )

    if statistical_scores.empty:
        return pd.DataFrame()

    # ---------------------------------------
    # ML evidence
    # ---------------------------------------

    ml_result = train_driver_model(
        drivers
    )

    if ml_result is None:
        return pd.DataFrame()

    ml_evidence = calculate_ml_evidence(
        ml_result
    )

    # ---------------------------------------
    # Combine statistical + ML evidence
    # ---------------------------------------

    combined = combine_driver_evidence(
        statistical_scores,
        ml_evidence
    )

    results = []

    for _, row in combined.iterrows():

        confidence = calculate_confidence(
            correlation=row["correlation"],
            evidence_score=row["combined_evidence"],
            history_count=len(drivers),
            data_fresh=data_fresh,
            data_complete=data_complete,
            contradictory=contradictory
        )

        confidence_category = (
            classify_confidence(
                confidence
            )
        )

        abstain = should_abstain(
            confidence
        )

        results.append({
            "driver": row["driver"],
            "correlation": row["correlation"],
            "current_change": row["current_change"],
            "statistical_evidence": row["evidence_score"],
            "ml_evidence": row["ml_evidence"],
            "combined_evidence": row["combined_evidence"],
            "confidence": confidence,
            "confidence_category": confidence_category,
            "abstain": abstain
        })

    ranking = pd.DataFrame(
        results
    )

    ranking = ranking.sort_values(
        "combined_evidence",
        ascending=False
    ).reset_index(drop=True)

    ranking["rank"] = (
        ranking.index + 1
    )

    return ranking

def combine_driver_evidence(
    statistical_scores,
    ml_evidence
):
    """
    Combine statistical evidence and ML evidence.

    Statistical evidence:
        Historical correlation + current movement

    ML evidence:
        Relative feature importance from regression

    This produces a combined evidence score.
    """

    combined = statistical_scores.merge(
        ml_evidence[
            [
                "driver",
                "ml_evidence"
            ]
        ],
        on="driver",
        how="left"
    )

    combined["ml_evidence"] = (
        combined["ml_evidence"]
        .fillna(0)
    )

    # ---------------------------------------
    # Combine the two evidence sources
    # ---------------------------------------

    combined["combined_evidence"] = (
        0.6 * combined["evidence_score"]
        + 0.4 * combined["ml_evidence"]
    )

    # ---------------------------------------
    # Rank drivers
    # ---------------------------------------

    combined = combined.sort_values(
        "combined_evidence",
        ascending=False
    ).reset_index(drop=True)

    combined["rank"] = (
        combined.index + 1
    )

    return combined

# =========================================================
# Test the engine
# =========================================================

sales, marketing, product = load_data()

result = calculate_regional_drivers(
    sales,
    marketing,
    product
)

print("\nREGIONAL ANALYSIS")
print("--------------------")

print(
    result["region_comparison"][
        [
            "region",
            "revenue_change",
            "percentage_change",
            "contribution_percentage"
        ]
    ]
)

print("\nPRIMARY REGION")
print("--------------------")
print(result["primary_region"])

print("\nDRIVER DATA")
print("--------------------")
print(result["drivers"])

driver_changes = calculate_driver_changes(
    result["drivers"]
)

print("\nDRIVER CHANGES")
print("--------------------")
print(driver_changes)

driver_scores = calculate_driver_scores(
    result["drivers"]
)

ml_result = train_driver_model(
    result["drivers"]
)

ml_evidence = calculate_ml_evidence(
    ml_result
)

combined_evidence = combine_driver_evidence(
    driver_scores,
    ml_evidence
)

print("\nCOMBINED DRIVER EVIDENCE")
print("--------------------")

print(
    combined_evidence[
        [
            "rank",
            "driver",
            "correlation",
            "current_change",
            "evidence_score",
            "ml_evidence",
            "combined_evidence"
        ]
    ]
)

print("\nDRIVER SCORES")
print("--------------------")

print(
    driver_scores[
        [
            "rank",
            "driver",
            "correlation",
            "current_change",
            "evidence_score"
        ]
    ]
)

print("\nPRODUCT-LEVEL CONVERSION")
print("--------------------")
print(result["conversion"])

driver_ranking = build_driver_ranking(
    result["drivers"]
)

print("\nFINAL DRIVER RANKING")
print("--------------------")

print(
    driver_ranking[
        [
            "rank",
            "driver",
            "statistical_evidence",
            "ml_evidence",
            "combined_evidence",
            "confidence",
            "confidence_category",
            "abstain"
        ]
    ]
)

