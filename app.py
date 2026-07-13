import gradio as gr

# calculate annual tax amount for a taxpayer in France
# First file before improvements and optimizations (see tax_calculator.py)
    
def compute_tax(income, fiscal_part):
    """
    Calculate the tax amount based on income and fiscal parts.
    """
    income_per_part = income / fiscal_part

    # 2026 tax brackets (income 2025) for the French income tax. These brackets are updated annually
    TAX_BRACKETS = [
        (181917, 0.45),
        (84577, 0.41),
        (29579, 0.30),
        (11600, 0.11),
        ] 

    tax_per_part = 0

    for limit, rate in TAX_BRACKETS:
        if income_per_part > limit:
                tax_per_part += (income_per_part - limit) * rate
                income_per_part = limit

    return tax_per_part * fiscal_part

def apply_quotient_familial_cap(income, parts, marital_status):
    """
    Applies: le plafond du quotient familial.

    Tax is computed:
    - once with the actual number of fiscal parts;
    - once with the base number of fiscal parts (1 for single, 2 for married).

    If the tax reduction due to the additional fiscal parts exceeds the legal cap,
    the excess is added back.
    """
    fiscal_part = parts["total"]
    base_parts = parts["base"]
    children_parts = parts["children"]
    disability_parts = parts["disability"]
    # Tax with actual fiscal parts
    tax_actual = compute_tax(income, fiscal_part)

    # Base fiscal parts
    base_parts = 1 if marital_status == "Single" else 2

    # No additional fiscal parts → no cap
    if fiscal_part <= base_parts:
        return tax_actual

    # Tax without additional fiscal parts
    tax_base = compute_tax(income, base_parts)

    # Tax reduction obtained thanks to additional fiscal parts
    tax_saving = tax_base - tax_actual

    # Number of additional half-parts
    extra_half_parts = (fiscal_part - base_parts) * 2

    # 2026 ceiling (income 2025) for the tax reduction due to additional fiscal parts: €1,807 per half-part
    # to update one place every year.
    CAP_PER_HALF_PART = 1807 

    maximum_saving = extra_half_parts * CAP_PER_HALF_PART

    if tax_saving > maximum_saving:
        tax_actual += (tax_saving - maximum_saving)

    return tax_actual

def compute_cehr(income, marital_status):
    """
    Simplified CEHR(contribution exceptionnelle des hauts revenus) calculation.
    Assumes income ≈ Revenu Fiscal de Référence (RFR).
    """

    cehr = 0

    if marital_status == "Single":

        # 3% between €250,000 and €500,000
        if income > 250000:
            cehr += (min(income, 500000) - 250000) * 0.03

        # 4% above €500,000
        if income > 500000:
            cehr += (income - 500000) * 0.04

    else:  # Married

        # 3% between €500,000 and €1,000,000
        if income > 500000:
            cehr += (min(income, 1000000) - 500000) * 0.03

        # 4% above €1,000,000
        if income > 1000000:
            cehr += (income - 1000000) * 0.04

    return cehr

def compute_fiscal_parts(marital_status, children,
                         disability, disability_couple,
                         disability_children):

    base_parts = 1 if marital_status == "Single" else 2

    # Children
    children_parts = 0

    if children == 1:
        children_parts = 0.5
    elif children == 2:
        children_parts = 1
    elif children >= 3:
        children_parts = 1 + (children - 2)

    # Disability
    disability_parts = 0

    if disability:
        disability_parts += 0.5

    if disability_couple:
        disability_parts += 0.5

    disability_parts += disability_children * 0.5

    total_parts = base_parts + children_parts + disability_parts

    return {
        "base": base_parts,
        "children": children_parts,
        "disability": disability_parts,
        "total": total_parts,
    }

def tax_amount(income, marital_status, children, disability, disability_couple,
                disability_children):
    if income < 0:
        raise gr.Error("Income must be greater than or equal to 0.")
    if marital_status is None:
        raise gr.Error("Please select your marital status.")
        
    #calculate fiscal part based on marital status and number of children
    #according to french tax rules
    parts=compute_fiscal_parts(
        marital_status, 
        children, 
        disability, 
        disability_couple, 
        disability_children)
    
    fiscal_part = parts["total"]

    tax_amount = apply_quotient_familial_cap(
        income,
        parts,
        marital_status
    )

    # Apply discount ("décote")
    if income <= 84577:
        if marital_status == "Single" and tax_amount <= 1982:
            tax_amount = tax_amount - 897 + (tax_amount * 0.4525)

        elif marital_status == "Married" and tax_amount <= 3277:
            tax_amount = tax_amount - 1483 + (tax_amount * 0.4525)

    # Tax cannot be negative
    tax_amount = max(0, tax_amount)
    # Add the official CEHR
    tax_amount += compute_cehr(income, marital_status)

    return tax_amount
   

demo = gr.Interface(
    fn=tax_amount,
    inputs=[
        gr.Number(label="Income (€)"),
        gr.Radio(["Single", "Married"], label="Marital status"),
        gr.Slider(0, 10, step=1, label="Number of children"),
        gr.Checkbox(label="Disability"),
        gr.Checkbox(label="Disability of the couple"),
        gr.Slider(0, 10, step=1, label="Number of children with disability"),
    ],
    outputs=gr.Number(label="Annual tax amount")
)

demo.launch()