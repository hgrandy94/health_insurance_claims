# Health Insurance Claims Power BI Copilot Hackathon

This repository contains a deterministic, synthetic private health insurance dataset for a Microsoft Fabric and Power BI Copilot hackathon.

Participants will:

1. Download the CSV files.
2. Create a lakehouse in Microsoft Fabric.
3. Upload the files and load them into lakehouse tables.
4. Build a semantic model with the supplied relationships and measures.
5. Use Power BI Copilot to create report pages and explore the data.

## Start here

Follow the [Power BI Copilot hackathon instruction manual](./hackathon-guide/README.md). It includes:

- Fabric and Copilot prerequisites
- CSV download and lakehouse setup instructions
- Table and semantic-model configuration
- Recommended DAX measures
- Three report-page exercises with example Copilot prompts
- Ten prompts for report consumers
- Validation checks and troubleshooting guidance

The source files are in the [`data`](./data) folder:

- [`policyholders.csv`](./data/policyholders.csv): 300 synthetic policyholders and policy attributes
- [`claims.csv`](./data/claims.csv): 800 synthetic claims from 2022 through 2025
- [`claim_investigations.csv`](./data/claim_investigations.csv): 938 investigation review events

## Data model

Create these active, single-direction relationships:

| One side | Many side | Key |
|---|---|---|
| `policyholders` | `claims` | `policyholder_id` |
| `claims` | `claim_investigations` | `claim_id` |

```mermaid
erDiagram
    policyholders ||--o{ claims : policyholder_id
    claims ||--o{ claim_investigations : claim_id
```

Use `policyholders` for customer and policy attributes, `claims` for financial and historical analysis, and `claim_investigations` for review-stage and risk analysis.

## Important data notice

All records are synthetic. They do not represent real customers, providers, claims, diagnoses, or investigations. Use the data only for learning and demonstrations, not for underwriting, claims decisions, fraud allegations, medical analysis, or other real-world decisions.

The planted patterns are deliberately explainable and include high-value claims, repeated provider/member activity, duplicate-document signals, identity-mismatch signals, and simulated investigation outcomes.

## Research basis

The synthetic field choices are informed by the general UK insurance and healthcare context described by:

- [Association of British Insurers fraud guidance](https://www.abi.org.uk/products-and-issues/topics-and-issues/fraud/)
- [NHS hospital guidance](https://www.nhs.uk/nhs-services/hospitals/going-into-hospital/)
