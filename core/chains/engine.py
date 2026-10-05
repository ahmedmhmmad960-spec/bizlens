def build_diagnosis_chains(diagnoses: list[dict]) -> list[dict]:
    """
    Connect related diagnoses into business cause-and-effect chains.
    """

    diagnosis_names = {
        diagnosis.get("diagnosis")
        for diagnosis in diagnoses
    }

    chains = []

    # Cost + margin + profit chain
    if (
        "Cost Pressure" in diagnosis_names
        and "Margin Decline" in diagnosis_names
        and "Revenue Up / Profit Down" in diagnosis_names
    ):
        chains.append({
            "chain": "Cost Pressure → Margin Decline → Profit Decline",
            "type": "profitability",
            "diagnoses": [
                "Cost Pressure",
                "Margin Decline",
                "Revenue Up / Profit Down",
            ],
            "explanation": (
                "Costs increased faster than revenue, "
                "which put pressure on gross margin and "
                "contributed to a decline in gross profit."
            ),
            "recommended_action": (
                "Investigate the products and cost drivers "
                "responsible for the increase before pursuing "
                "additional sales growth."
            ),
        })

    # Discount + margin + profit chain
    if (
        "Discount Pressure" in diagnosis_names
        and "Margin Decline" in diagnosis_names
    ):
        chains.append({
            "chain": "Discount Pressure → Margin Decline",
            "type": "pricing",
            "diagnoses": [
                "Discount Pressure",
                "Margin Decline",
            ],
            "explanation": (
                "Discounting increased faster than revenue, "
                "while gross margin declined."
            ),
            "recommended_action": (
                "Review promotional discounts and determine "
                "whether they are generating enough additional "
                "revenue to justify the margin reduction."
            ),
        })

    return chains