import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler


def prepare_ml_data(drivers):
    """
    Prepare historical driver data for machine learning.

    Target:
        revenue

    Features:
        units_sold
        marketing_spend
        website_traffic
    """

    features = [
        "units_sold",
        "marketing_spend",
        "website_traffic"
    ]

    data = drivers[
        ["revenue"] + features
    ].dropna()

    X = data[features]
    y = data["revenue"]

    return X, y


def train_driver_model(drivers):
    """
    Train an interpretable linear regression model
    using historical regional data.
    """

    X, y = prepare_ml_data(drivers)

    if len(X) < 5:
        return None

    # Standardize features so coefficients can
    # be compared on the same scale.
    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(X)

    # Train regression model
    model = LinearRegression()

    model.fit(
        X_scaled,
        y
    )

    # Create coefficient table
    coefficients = pd.DataFrame({
        "driver": X.columns,
        "coefficient": model.coef_
    })

    # Absolute coefficient = importance magnitude
    coefficients["importance"] = (
        coefficients["coefficient"]
        .abs()
    )

    coefficients = coefficients.sort_values(
        "importance",
        ascending=False
    ).reset_index(drop=True)

    coefficients["rank"] = (
        coefficients.index + 1
    )

    return {
        "model": model,
        "scaler": scaler,
        "coefficients": coefficients,
        "r_squared": model.score(
            X_scaled,
            y
        )
    }

def calculate_ml_evidence(ml_result):
    """
    Convert ML coefficient importance into
    normalized 0-1 evidence scores.
    """

    coefficients = ml_result["coefficients"].copy()

    total_importance = coefficients["importance"].sum()

    if total_importance == 0:
        coefficients["ml_evidence"] = 0
    else:
        coefficients["ml_evidence"] = (
            coefficients["importance"]
            / total_importance
        )

    return coefficients

# =========================================================
# Test the ML model
# =========================================================

if __name__ == "__main__":

    from data_loader import load_data
    from driver_engine import (
        calculate_regional_drivers
    )

    sales, marketing, product = load_data()

    result = calculate_regional_drivers(
        sales,
        marketing,
        product
    )

    drivers = result["drivers"]

    ml_result = train_driver_model(
        drivers
    )

    ml_evidence = calculate_ml_evidence(
    ml_result
    )

    print("\nML EVIDENCE")
    print("--------------------")

    print(
        ml_evidence[
            [
                "driver",
                "coefficient",
                "importance",
                "ml_evidence"
            ]
        ]
    )

    if ml_result is None:

        print(
            "\nNot enough historical data "
            "to train the model."
        )

    else:

        print("\nML DRIVER MODEL")
        print("--------------------")

        print(
            ml_result["coefficients"][
                [
                    "rank",
                    "driver",
                    "coefficient",
                    "importance"
                ]
            ]
        )

        print(
            f"\nR² score: "
            f"{ml_result['r_squared']:.3f}"
        )
