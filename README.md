# BusinessIntelligence.ai

BusinessIntelligence.ai is a prototype KPI intelligence-to-action engine that helps
business users move beyond traditional dashboards that only show what happened.

The system detects material KPI movements, identifies the business segments
contributing to those movements, ranks potential drivers using statistical and
machine-learning evidence, communicates confidence and uncertainty, recommends
practical actions, and generates persona-specific business narratives using Gemini.

A core design principle is that the LLM is **not treated as the source of quantitative
truth**. KPI calculations, statistical analysis, machine-learning outputs, confidence
scoring, recommendations, and access controls are handled by analytical and
deterministic components. Gemini is used downstream for narrative synthesis.

## Table of contents

* Problem statement
* Solution overview
* Requirements
* Data sources
* KPI semantic configuration
* Material KPI movement detection
* Regional contribution analysis
* Product contribution analysis
* Driver analysis
* Machine learning component
* Evidence fusion
* Confidence and abstention
* Recommendation engine
* Persona-specific insights
* Role-based access
* LLM integration
* Runtime telemetry
* Technology stack
* Project structure
* Installation
* Configuration
* Troubleshooting
* Prototype limitations
* Future roadmap
* Conclusion

## Problem statement

Businesses often track KPIs across multiple systems with different data grains,
refresh patterns, and business contexts.

A conventional dashboard may show:

> Revenue decreased by 19.94%.

However, a decision-maker still needs to understand:

* Where did the movement occur?
* Which drivers contributed to the movement?
* How strong is the evidence?
* Should the business act immediately or investigate further?
* Who should own the response?
* When should the system abstain from making an attribution?

BusinessIntelligence.ai addresses this gap by creating an intelligence-to-action
workflow:

```text
What happened?
      ↓
Where did it happen?
      ↓
Why might it have happened?
      ↓
How strong is the evidence?
      ↓
What should we do?
      ↓
Who should act?
```

## Solution overview

The prototype follows a hybrid analytical architecture:

```text
Multiple Data Sources
        ↓
Data Loading & Preparation
        ↓
KPI Calculation
        ↓
Material Movement Detection
        ↓
Regional Contribution Analysis
        ↓
Product Contribution Analysis
        ↓
Statistical Driver Analysis
        ↓
Machine Learning Driver Analysis
        ↓
Evidence Fusion
        ↓
Confidence & Abstention
        ↓
Recommendations
        ↓
Persona-Specific Narrative
        ↓
Gemini LLM
        ↓
Streamlit Dashboard
```

The system intentionally separates quantitative reasoning from language generation.
The LLM receives verified analytical outputs instead of independently calculating
business metrics.

## Requirements

The prototype requires:

* Python 3.x
* Pandas
* NumPy
* scikit-learn
* Streamlit
* Plotly
* Google Gemini API access
* python-dotenv
* Internet access for Gemini API calls

All Python dependencies are listed in `requirements.txt`.

## Data sources

The prototype uses three connected synthetic data sources.

### Sales data

Contains:

* Date
* Region
* Product
* Units sold
* Revenue
* Returns

### Marketing data

Contains:

* Week
* Region
* Marketing spend
* Website traffic

### Product data

Contains:

* Date
* Product
* Price
* Conversion rate

The sources use different grains:

* Sales: daily
* Marketing: weekly
* Product: daily

The analytical engine aggregates these datasets to a common monthly level where
appropriate.

## KPI semantic configuration

The prototype contains a lightweight KPI configuration layer describing KPI
definitions, calculations, data sources, grains, materiality thresholds,
candidate drivers, and access permissions.

Example:

```text
KPI:
Revenue

Definition:
Total sales revenue

Calculation:
SUM(sales.revenue)

Grain:
Daily → Monthly

Source:
sales.csv

Materiality threshold:
5%

Candidate drivers:
- units_sold
- marketing_spend
- website_traffic
- conversion_rate
```

This provides a basic semantic contract between the business definition and the
analytical implementation.

## Material KPI movement detection

The KPI engine compares the latest two available monthly observations.

Current prototype result:

```text
Previous revenue: ₹3,128,927.03

Current revenue: ₹2,504,943.48

Revenue change: -19.94%

Material movement: TRUE
```

The configured materiality threshold is 5%.

Because the observed movement exceeds the threshold, the system initiates deeper
driver analysis.

## Regional contribution analysis

The system does not assume which region is responsible for the decline.

Instead, it compares revenue movement across all regions.

Current prototype result:

| Region | Revenue Change | Percentage Change | Contribution |
| ------ | -------------: | ----------------: | -----------: |
| East   |   -₹118,662.91 |           -12.48% |       19.02% |
| North  |   -₹405,129.85 |           -35.42% |       64.93% |
| South  |   -₹100,190.79 |            -9.69% |       16.06% |

The engine dynamically identifies **North** as the primary declining region because
it has the largest absolute revenue decline.

This prevents the analytical pipeline from hard-coding the answer in advance.

## Product contribution analysis

After identifying the primary region, the engine evaluates product-level revenue
movement within that region.

For North:

| Product | Revenue Change | Percentage Change | Contribution |
| ------- | -------------: | ----------------: | -----------: |
| A       |   -₹126,720.26 |           -32.98% |       31.28% |
| B       |   -₹154,435.71 |           -39.92% |       38.12% |
| C       |   -₹123,973.88 |           -33.26% |       30.60% |

Product B contributes the largest share of the decline within North, while all
three products show significant deterioration.

## Driver analysis

The system evaluates candidate drivers using multiple forms of evidence.

Current candidate drivers include:

* Units sold
* Website traffic
* Marketing spend

The engine evaluates:

1. Historical statistical relationship with revenue
2. Current driver movement
3. Statistical evidence
4. Machine-learning evidence
5. Combined evidence
6. Confidence

## Machine learning component

The prototype uses **scikit-learn Linear Regression** as an interpretable
machine-learning evidence source.

### Features

```text
units_sold
marketing_spend
website_traffic
```

### Target

```text
revenue
```

The model uses feature scaling before regression so that the resulting coefficients
can be compared more meaningfully.

Example output:

```text
ML DRIVER MODEL

1. units_sold
2. website_traffic
3. marketing_spend

R² score: 0.988
```

The model identifies `units_sold` as the strongest feature in the prototype
dataset.

### Interpretation

The ML model is treated as an evidence source rather than proof of causality.

The prototype contains a small synthetic dataset and limited historical
observations. Therefore, regression relationships are not interpreted as
established causal relationships.

## Evidence fusion

The system combines statistical and machine-learning evidence.

Current prototype:

| Driver          | Statistical Evidence | ML Evidence | Combined Evidence |
| --------------- | -------------------: | ----------: | ----------------: |
| Units sold      |                0.996 |       0.836 |             0.932 |
| Website traffic |                0.326 |       0.103 |             0.237 |
| Marketing spend |                0.321 |       0.060 |             0.217 |

The prototype combines the evidence using:

```text
60% Statistical Evidence
40% ML Evidence
```

This weighting is a prototype design choice intended to prevent the small-sample
ML model from completely dominating the analytical assessment.

## Confidence and abstention

The system converts the combined evidence into a confidence assessment.

Current prototype ranking:

| Rank | Driver          | Combined Evidence | Confidence | Category |
| ---- | --------------- | ----------------: | ---------: | -------- |
| 1    | Units sold      |             0.932 |      94.7% | High     |
| 2    | Website traffic |             0.237 |      53.4% | Medium   |
| 3    | Marketing spend |             0.217 |      52.4% | Medium   |

The system also supports abstention when evidence is insufficient.

The Streamlit dashboard contains a **Low Evidence Demo** mode that demonstrates
the intended behavior:

```text
INSUFFICIENT EVIDENCE

The system cannot reliably attribute the KPI movement
to a specific driver.

Additional evidence or clarification is required before
taking action.
```

This prevents the system from forcing a driver attribution when the evidence does
not justify one.

## Recommendation engine

The recommendation engine converts analytical findings into practical business
actions.

Example:

```text
Driver:
Units sold

Region:
North

Action:
Investigate the North sales funnel and identify the
source of the unit-volume decline.

Owner:
Regional Sales Manager

Monitoring:
Track weekly units sold and revenue for the affected region.
```

Recommendations follow the structure:

```text
Driver
  ↓
Business lever
  ↓
Action
  ↓
Owner
  ↓
Confidence
  ↓
Monitoring plan
```

## Persona-specific insights

The same analytical evidence can be presented differently depending on the
business user's role.

### Executive

The executive view emphasizes:

* Business impact
* Priority
* Key driver
* Recommended action

Example:

> Revenue declined 19.9%, primarily concentrated in the North region.
> Units sold is the strongest evidence-backed candidate driver. Prioritize
> investigation of the North sales funnel.

### Analyst

The analyst view emphasizes:

* Driver evidence
* Statistical relationships
* ML evidence
* Confidence
* Methodological limitations

Example:

> North is the largest regional contributor to the movement. Units sold is
> the top-ranked driver with 94.7% evidence confidence. The result should
> be interpreted as evidence of association rather than established causality.

## Role-based access

The prototype includes a lightweight role-based entitlement layer.

### Executive

Access to:

* Revenue
* Regional summary
* Recommendations

### Analyst

Access to:

* Revenue
* Regional summary
* Product analysis
* Driver analysis
* Recommendations

### Regional manager

Access to:

* Revenue
* Regional summary
* Recommendations

This demonstrates the concept of role-specific information exposure.

The prototype does not claim to implement production-grade enterprise
authentication or row-level security.

## LLM integration

Gemini is used as the final narrative synthesis layer.

The LLM receives verified analytical outputs such as:

```text
Revenue change: -19.94%

Primary region: North

Top driver: Units sold

Driver change: -29.67%

Statistical evidence: 0.996

ML evidence: 0.836

Combined evidence: 0.932

Confidence: 94.7%
```

Gemini then generates a concise business narrative.

### LLM responsibility

Gemini is responsible for:

* Narrative generation
* Business-language synthesis
* Persona-aware communication
* Explanation of verified evidence

### Non-LLM responsibility

The analytical pipeline is responsible for:

* KPI calculation
* Aggregation
* Materiality detection
* Contribution analysis
* Statistical analysis
* Machine learning
* Confidence
* Abstention
* Recommendations
* Access control

This separation reduces the risk of the LLM becoming the source of quantitative
truth.

## Runtime telemetry

The dashboard exposes basic prototype telemetry:

```text
Analysis latency
ML model calls
LLM calls
Estimated cost
```

This demonstrates awareness of:

* Latency
* Model usage
* LLM economics
* Runtime observability

## Technology stack

| Technology        | Purpose                                 |
| ----------------- | --------------------------------------- |
| Python            | Core implementation                     |
| Pandas            | Data processing                         |
| NumPy             | Numerical operations                    |
| scikit-learn      | Machine learning                        |
| Streamlit         | Interactive dashboard                   |
| Plotly            | Data visualization                      |
| Google Gemini API | Narrative synthesis                     |
| python-dotenv     | Environment configuration               |
| Git / GitHub      | Version control and source distribution |

## Project structure

```text
AI_Business_Analyst/
│
├── app.py
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── data/
│   ├── sales.csv
│   ├── marketing.csv
│   └── product.csv
│
└── src/
    ├── data_loader.py
    ├── kpi_config.py
    ├── kpi_engine.py
    ├── driver_engine.py
    ├── ml_driver_engine.py
    ├── confidence_engine.py
    ├── recommendation_engine.py
    ├── persona_engine.py
    ├── security.py
    ├── insight_engine.py
    └── llm_engine.py
```

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd AI_Business_Analyst
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
```

### 3. Activate the virtual environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

### 5. Configure the Gemini API

Create a `.env` file in the project root:

```text
GEMINI_API_KEY=your_api_key_here
```

Do not commit `.env` to the public repository.

### 6. Run the application

```powershell
streamlit run app.py
```

The Streamlit dashboard will open in a browser.

## Configuration

The application uses environment variables for API credentials.

The expected configuration is:

```text
GEMINI_API_KEY=your_api_key_here
```

A `.env.example` file should be included in the repository as a safe configuration
template.

The actual `.env` file containing the API key must remain private.

## Troubleshooting

### Streamlit does not start

Ensure the virtual environment is activated and dependencies are installed:

```powershell
pip install -r requirements.txt
```

Then run:

```powershell
streamlit run app.py
```

### Gemini narrative does not generate

Check that:

* `GEMINI_API_KEY` exists in `.env`
* The API key is valid
* Internet connectivity is available
* The selected Gemini model is available to the API account

The quantitative analytical pipeline remains usable even when Gemini is temporarily
unavailable.

### Import errors

Ensure the application is being run from the project root:

```text
AI_Business_Analyst/
```

The application adds the `src` directory to the Python path.

## Prototype limitations

This project is a working prototype rather than a production enterprise deployment.

Current limitations include:

* Small synthetic dataset
* Limited historical observations
* Regression evaluated primarily as an evidence source
* No production-grade causal inference
* Lightweight role-based access implementation
* Prototype-level telemetry
* No production data lineage platform
* No full model or data drift monitoring
* Feedback learning is planned rather than fully implemented
* Confidence calibration requires larger validation datasets

These limitations define areas for future development rather than claims of
production readiness.

## Future roadmap

### Phase 1 — Prototype

* Multi-source KPI analysis
* Material movement detection
* Driver identification
* Statistical and ML evidence
* Confidence scoring
* Abstention
* Recommendations
* Persona-specific narratives
* Interactive dashboard

### Phase 2 — Pilot

* Real enterprise data
* Governed KPI semantic layer
* Enterprise identity and access management
* Data-quality monitoring
* Analyst feedback capture
* Improved model validation
* Automated lineage

### Phase 3 — Production

* Scalable data infrastructure
* Advanced causal inference
* Model and data drift monitoring
* Continuous evaluation
* Feedback-driven model improvement
* Enterprise-grade security
* Cost and latency optimization
* Proactive alerts and decision workflows

## Key design principles

### Quantitative truth stays outside the LLM

The LLM does not calculate or determine KPI values.

### Evidence before explanation

The system establishes analytical evidence before generating a narrative.

### Confidence before action

Recommendations are tied to evidence confidence.

### Abstention is a feature

When evidence is insufficient, the system can avoid making a strong attribution.

### Persona-aware intelligence

Different users receive information appropriate to their decision-making needs.

### Action over observation

The system is designed to move from:

```text
What happened?
      ↓
Why might it have happened?
      ↓
How confident are we?
      ↓
What should we do?
```

## Conclusion

BusinessIntelligence.ai demonstrates a hybrid approach to KPI intelligence that
combines deterministic analytics, statistical reasoning, traditional machine
learning, confidence scoring, business rules, role-aware presentation, and
LLM-assisted narrative generation.

The prototype is built around a simple principle:

> **A business intelligence system should not merely tell a user what changed.
> It should provide evidence for why it may have changed, communicate how strong
> that evidence is, and help the user decide what to do next.**

```
```
