ROLE_PERMISSIONS = {

    "executive": [
        "revenue",
        "region_summary",
        "recommendations"
    ],

    "analyst": [
        "revenue",
        "region_summary",
        "product_analysis",
        "driver_analysis",
        "recommendations"
    ],

    "regional_manager": [
        "revenue",
        "region_summary",
        "recommendations"
    ]
}


def has_access(role, resource):
    """
    Check whether a role can access a resource.
    """

    permissions = ROLE_PERMISSIONS.get(
        role,
        []
    )

    return resource in permissions


def filter_insight_for_role(
    insight,
    role
):
    """
    Return only information permitted
    for the selected role.
    """

    filtered = {
        "kpi": insight["kpi"],
        "primary_region": insight[
            "primary_region"
        ]
    }

    if has_access(
        role,
        "region_summary"
    ):

        filtered["region_analysis"] = (
            insight["region_analysis"]
        )

    if has_access(
        role,
        "product_analysis"
    ):

        filtered["product_analysis"] = (
            insight["product_analysis"]
        )

    if has_access(
        role,
        "driver_analysis"
    ):

        filtered["driver_ranking"] = (
            insight["driver_ranking"]
        )

    if has_access(
        role,
        "recommendations"
    ):

        filtered["recommendations"] = (
            insight["recommendations"]
        )

    return filtered
