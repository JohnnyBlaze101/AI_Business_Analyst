KPI_CONFIG = {

    "revenue": {
        "definition": "Total sales revenue",
        "calculation": "SUM(sales.revenue)",
        "grain": "daily → monthly",
        "source": "sales.csv",
        "materiality_threshold": 5,
        "candidate_drivers": [
            "units_sold",
            "marketing_spend",
            "website_traffic",
            "conversion_rate"
        ],
        "access": [
            "executive",
            "analyst",
            "regional_manager"
        ]
    },

    "units_sold": {
        "definition": "Total number of units sold",
        "calculation": "SUM(sales.units_sold)",
        "grain": "daily → monthly",
        "source": "sales.csv",
        "materiality_threshold": 5,
        "candidate_drivers": [
            "website_traffic",
            "marketing_spend",
            "conversion_rate"
        ],
        "access": [
            "executive",
            "analyst",
            "regional_manager"
        ]
    },

    "marketing_spend": {
        "definition": "Total marketing expenditure",
        "calculation": "SUM(marketing.marketing_spend)",
        "grain": "weekly → monthly",
        "source": "marketing.csv",
        "materiality_threshold": 5,
        "candidate_drivers": [
            "website_traffic"
        ],
        "access": [
            "executive",
            "analyst",
            "regional_manager"
        ]
    },

    "website_traffic": {
        "definition": "Total website visits",
        "calculation": "SUM(marketing.website_traffic)",
        "grain": "weekly → monthly",
        "source": "marketing.csv",
        "materiality_threshold": 5,
        "candidate_drivers": [
            "marketing_spend"
        ],
        "access": [
            "executive",
            "analyst",
            "regional_manager"
        ]
    },

    "conversion_rate": {
        "definition": "Average product conversion rate",
        "calculation": "MEAN(product.conversion_rate)",
        "grain": "daily → monthly",
        "source": "product.csv",

        # Important limitation:
        # product.csv does not contain region,
        # so this KPI cannot currently support
        # region-specific attribution.

        "scope": "product-level",
        "materiality_threshold": 5,

        "candidate_drivers": [
            "website_traffic",
            "marketing_spend"
        ],

        "access": [
            "executive",
            "analyst"
        ]
    }
}
