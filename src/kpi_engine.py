import pandas as pd


def calculate_revenue_kpi(sales):
    """
    Calculate total monthly revenue.
    """

    sales = sales.copy()

    sales["date"] = pd.to_datetime(sales["date"])

    monthly_revenue = (
        sales
        .groupby(sales["date"].dt.to_period("M"))["revenue"]
        .sum()
        .reset_index()
    )

    monthly_revenue["date"] = (
        monthly_revenue["date"]
        .dt.to_timestamp()
    )

    return monthly_revenue


def calculate_kpi_change(current, previous):
    """
    Calculate absolute and percentage change
    between two KPI values.
    """

    absolute_change = current - previous

    if previous == 0:
        percentage_change = 0
    else:
        percentage_change = (
            absolute_change / previous
        ) * 100

    return absolute_change, percentage_change


def detect_material_movement(
    percentage_change,
    threshold=5
):
    """
    Determine whether a KPI movement is material.
    """

    return abs(percentage_change) >= threshold


def calculate_region_contribution(sales):
    """
    Compare revenue across ALL regions between
    the latest two months.

    The function does not assume a problem region.
    It calculates the evidence needed to identify one.
    """

    sales = sales.copy()

    sales["date"] = pd.to_datetime(sales["date"])

    sales["month"] = (
        sales["date"]
        .dt
        .to_period("M")
    )

    monthly_region = (
        sales
        .groupby(["month", "region"])["revenue"]
        .sum()
        .reset_index()
    )

    months = sorted(
        monthly_region["month"].unique()
    )

    if len(months) < 2:
        return pd.DataFrame()

    previous_month = months[-2]
    current_month = months[-1]

    previous = monthly_region[
        monthly_region["month"] == previous_month
    ]

    current = monthly_region[
        monthly_region["month"] == current_month
    ]

    comparison = previous.merge(
        current,
        on="region",
        suffixes=("_previous", "_current")
    )

    comparison["change"] = (
        comparison["revenue_current"]
        - comparison["revenue_previous"]
    )

    comparison["percentage_change"] = (
        comparison["change"]
        / comparison["revenue_previous"]
    ) * 100

    total_change = comparison["change"].sum()

    if total_change != 0:

        comparison["contribution_percentage"] = (
            comparison["change"]
            / total_change
        ) * 100

    else:

        comparison["contribution_percentage"] = 0

    return comparison


def identify_primary_region(region_analysis):
    """
    Identify the region with the largest revenue decline.

    The region is discovered from the data rather than
    being hard-coded.
    """

    if region_analysis.empty:
        return None

    declining_regions = region_analysis[
        region_analysis["change"] < 0
    ]

    if declining_regions.empty:
        return None

    primary_region = declining_regions.loc[
        declining_regions["change"].idxmin(),
        "region"
    ]

    return primary_region


def calculate_product_contribution(
    sales,
    region
):
    """
    Compare product revenue between the latest
    two months for a region selected by the engine.
    """

    sales = sales.copy()

    sales["date"] = pd.to_datetime(
        sales["date"]
    )

    sales["month"] = (
        sales["date"]
        .dt
        .to_period("M")
    )

    filtered = sales[
        sales["region"] == region
    ]

    monthly_product = (
        filtered
        .groupby(["month", "product"])["revenue"]
        .sum()
        .reset_index()
    )

    months = sorted(
        monthly_product["month"].unique()
    )

    if len(months) < 2:
        return pd.DataFrame()

    previous_month = months[-2]
    current_month = months[-1]

    previous = monthly_product[
        monthly_product["month"] == previous_month
    ]

    current = monthly_product[
        monthly_product["month"] == current_month
    ]

    comparison = previous.merge(
        current,
        on="product",
        suffixes=("_previous", "_current")
    )

    comparison["change"] = (
        comparison["revenue_current"]
        - comparison["revenue_previous"]
    )

    comparison["percentage_change"] = (
        comparison["change"]
        / comparison["revenue_previous"]
    ) * 100

    total_change = comparison["change"].sum()

    if total_change != 0:

        comparison["contribution_percentage"] = (
            comparison["change"]
            / total_change
        ) * 100

    else:

        comparison["contribution_percentage"] = 0

    return comparison


def run_kpi_analysis(sales):
    """
    Run the complete KPI analysis pipeline.

    Returns all analytical results needed by
    downstream components.
    """

    monthly_revenue = calculate_revenue_kpi(
        sales
    )

    if len(monthly_revenue) < 2:
        return {
            "monthly_revenue": monthly_revenue,
            "current_revenue": None,
            "previous_revenue": None,
            "percentage_change": None,
            "is_material": False,
            "region_analysis": pd.DataFrame(),
            "primary_region": None,
            "product_analysis": pd.DataFrame()
        }

    current_revenue = (
        monthly_revenue
        .iloc[-1]["revenue"]
    )

    previous_revenue = (
        monthly_revenue
        .iloc[-2]["revenue"]
    )

    absolute_change, percentage_change = (
        calculate_kpi_change(
            current_revenue,
            previous_revenue
        )
    )

    is_material = detect_material_movement(
        percentage_change
    )

    region_analysis = (
        calculate_region_contribution(
            sales
        )
    )

    primary_region = (
        identify_primary_region(
            region_analysis
        )
    )

    if primary_region is not None:

        product_analysis = (
            calculate_product_contribution(
                sales,
                primary_region
            )
        )

    else:

        product_analysis = pd.DataFrame()

    return {
        "monthly_revenue": monthly_revenue,
        "current_revenue": current_revenue,
        "previous_revenue": previous_revenue,
        "absolute_change": absolute_change,
        "percentage_change": percentage_change,
        "is_material": is_material,
        "region_analysis": region_analysis,
        "primary_region": primary_region,
        "product_analysis": product_analysis
    }


# =========================================================
# Test the module
# =========================================================

if __name__ == "__main__":

    from data_loader import load_data

    sales, marketing, product = load_data()

    result = run_kpi_analysis(sales)

    print("\nMONTHLY REVENUE")
    print("--------------------")
    print(result["monthly_revenue"])

    print("\nKPI ANALYSIS")
    print("--------------------")
    print(
        f"Previous revenue: "
        f"₹{result['previous_revenue']:,.2f}"
    )

    print(
        f"Current revenue: "
        f"₹{result['current_revenue']:,.2f}"
    )

    print(
        f"Change: "
        f"{result['percentage_change']:.2f}%"
    )

    print(
        f"Material movement: "
        f"{result['is_material']}"
    )

    print("\nREGION CONTRIBUTION")
    print("--------------------")

    print(
        result["region_analysis"][
            [
                "region",
                "change",
                "percentage_change",
                "contribution_percentage"
            ]
        ]
    )

    print("\nPRIMARY REGION")
    print("--------------------")
    print(result["primary_region"])

    print("\nPRODUCT CONTRIBUTION")
    print("--------------------")

    print(
        result["product_analysis"][
            [
                "product",
                "change",
                "percentage_change",
                "contribution_percentage"
            ]
        ]
    )
