# UI: Gradio interface

import gradio as gr
import spaces

# Dummy GPU placeholder function to satisfy ZeroGPU startup check on free-tier Spaces
# using Gradio in new Hugging Face Spaces created
@spaces.GPU
def _dummy_gpu_placeholder():
    """Unused function required so ZeroGPU startup check passes on this free-tier Space."""
    return None


# 2026 tax brackets (income 2025) for the French income tax:
# maximum income for each bracket and the corresponding tax rate.
# low income related to low tax rates, high income related to high tax rates.
TAX_BRACKETS=[(181917,0.45),(84577,0.41),(29579,0.30),(11600,0.11)]

# The maximum tax saving per half part is 1807€ in 2026 (income 2025)
CAP_PER_HALF_PART=1807

def taxable_income(gross,deduction_type,actual=0):
    """computes the taxable income after applying the professional expense deduction.
    The deduction can be either:
    - a flat 10% of the gross income (default)
    - the actual professional expenses (if provided). No maximum is applied according to the tax income law, but the user must provide the actual expenses."""
    if deduction_type=="10%":
        deduction=gross*0.10
    else:
        deduction=actual
    return max(0,gross-deduction),deduction

def compute_tax(income,parts):
    """Computes the tax based on the taxable income and the number of fiscal parts
    using the French tax brackets."""
    x=income/parts
    t=0
    for lim,rate in TAX_BRACKETS:
        if x>lim:
            t+=(x-lim)*rate
            x=lim
    return t*parts

def apply_quotient_familial_cap(income,parts,status):
    """Applies the quotient familial cap to the computed tax based on income,
    fiscal parts, and marital status."""
    tax_actual=compute_tax(income,parts)
    base=1 if status=="Single" else 2
    if parts<=base:return tax_actual
    tax_base=compute_tax(income,base)
    saving=tax_base-tax_actual
    maxsave=(parts-base)*2*CAP_PER_HALF_PART
    if saving>maxsave:
        tax_actual+=saving-maxsave
    return tax_actual

def compute_cehr(income,status):
    """Computes the Contribution Exceptionnelle sur les Hauts Revenus (CEHR)
    based on highest income and marital status."""
    c=0
    if status=="Single":
        if income>250000:c+=(min(income,500000)-250000)*0.03
        if income>500000:c+=(income-500000)*0.04
    else:
        if income>500000:c+=(min(income,1000000)-500000)*0.03
        if income>1000000:c+=(income-1000000)*0.04
    return c

def compute_decote(tax,income,status):
    """Computes the décote (tax reduction) based on the tax amount,
    income, and marital status."""
    if income>84577:return 0
    if status=="Single" and tax<=1982:
        return max(0,897-tax*0.4525)
    if status=="Married" and tax<=3277:
        return max(0,1483-tax*0.4525)
    return 0

def compute_fiscal_parts(status,children,dis1,dis2,dis_child):
    """Computes the number of fiscal parts based on marital status,
    number of children, and disabilities."""
    base=1 if status=="Single" else 2
    cp=0
    if children==1: cp=.5
    elif children==2: cp=1
    elif children>=3: cp=1+(children-2)
    dp=(0.5 if dis1 else 0)+(0.5 if dis2 else 0)+0.5*dis_child
    return base+cp+dp

def tax_amount(income,status,children,dis1,dis2,dis_child,deduction_type,actual_expenses):
    """Computes the final tax amount based on the provided parameters."""
    if income<0: raise gr.Error("Income must be >=0")
    parts=compute_fiscal_parts(status,children,dis1,dis2,dis_child)
    taxable,deduction=taxable_income(income,deduction_type,actual_expenses)
    before=apply_quotient_familial_cap(taxable,parts,status)
    decote=compute_decote(before,taxable,status)
    after=max(0,before-decote)
    cehr=compute_cehr(income,status)
    final=after+cehr
    return f"""### French Income Tax Summary

**Income:** €{income:,.2f}

**Professional deduction ({deduction_type}):** €{deduction:,.2f}

**Taxable income:** €{taxable:,.2f}

**Fiscal parts:** {parts}

**Tax before décote:** €{before:,.2f}

**Décote:** €{decote:,.2f}

**CEHR:** €{cehr:,.2f}

## Final tax: €{final:,.2f}
"""

#Gradio interface
demo=gr.Interface(
fn=tax_amount,
inputs=[
gr.Number(label="Gross income (€)"),
gr.Radio(["Single","Married"],label="Marital status"),
gr.Slider(0,10,step=1,label="Children"),
gr.Checkbox(label="Disability"),
gr.Checkbox(label="Disability of spouse"),
gr.Slider(0,10,step=1,label="Disabled children"),
gr.Radio(["10%","Actual expenses"],value="10%",label="Professional expense deduction"),
gr.Number(value=0,label="Actual expenses (€)")
],
outputs=gr.Markdown(label="Tax summary"),
title="French Income Tax Calculator"
)
if __name__=="__main__":
    demo.launch()