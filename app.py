import gradio as gr

#calculate tax amount
    
def compute_tax(income, fiscal_part):
    income_per_part = income / fiscal_part

    brackets = [
        (181917, 0.45),
        (84577, 0.41),
        (29579, 0.30),
        (11600, 0.11),
        ]

    tax_per_part = 0

    for limit, rate in brackets:
        if income_per_part > limit:
                tax_per_part += (income_per_part - limit) * rate
                income_per_part = limit

    return tax_per_part * fiscal_part

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

def tax_amount(income, marital_status, children, disability, disability_couple,
                disability_children):
    if income < 0:
        raise gr.Error("Income must be greater than or equal to 0.")
    if marital_status is None:
        raise gr.Error("Please select your marital status.")
        
    #calculate fiscal part based on marital status and number of children
    #according to french tax rules
    fiscal_part = 1 if marital_status == "Single" else 2

    if children == 1:
        fiscal_part += 0.5
    elif children == 2:
            fiscal_part += 1
    elif children >= 3:
            fiscal_part += 1 + (children - 2)

    if disability:
        fiscal_part += 0.5
    if disability_couple: 
        fiscal_part += 0.5
    if disability_children:
        fiscal_part += disability_children * 0.5

    tax_amount = compute_tax(income, fiscal_part)
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