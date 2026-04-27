import os
from fpdf import FPDF

def create_pdf(filename, title, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=15, style='B')
    pdf.cell(200, 10, txt=title, ln=1, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    
    for line in content.split('\n'):
        pdf.multi_cell(0, 10, txt=line)
    
    pdf.output(filename)
    print(f"Created {filename}")

if __name__ == "__main__":
    out_dir = "data/pdfs"
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Insulin
    create_pdf(
        f"{out_dir}/insulin_shipping_regulations.pdf",
        "Insulin Shipping Regulations",
        """McKesson Logistics - Standard Operating Procedure for Insulin

1. Temperature Control:
Insulin must be maintained at a temperature between 2°C and 8°C (36°F and 46°F) at all times during transit. IT MUST NEVER BE FROZEN. If insulin is frozen, it is considered destroyed and must be discarded.

2. Packaging:
Use insulated shipping containers with appropriate gel packs to maintain the 2-8°C range. Do not allow gel packs to touch the product directly.

3. Handling:
Handle with care. Avoid excessive shaking or exposure to direct sunlight.
"""
    )
    
    # 2. Amoxicillin
    create_pdf(
        f"{out_dir}/amoxicillin_storage.pdf",
        "Amoxicillin Storage Guidelines",
        """McKesson Logistics - Amoxicillin Guidelines

1. Temperature Control:
Amoxicillin oral suspension capsules and tablets should be stored at controlled room temperature, between 20°C to 25°C (68°F to 77°F).

2. Humidity:
Keep away from excess moisture.

3. Packaging:
Standard secure packaging suitable for dry goods. No refrigeration required.
"""
    )
    
    # 3. mRNA Vaccine
    create_pdf(
        f"{out_dir}/mrna_vaccine_protocol.pdf",
        "mRNA Vaccine Shipping Protocol",
        """McKesson Logistics - mRNA Vaccine Protocol (Ultra-Cold)

1. Temperature Control:
Must be stored and shipped in ultra-cold freezers between -90°C and -60°C (-130°F and -76°F). 

2. Packaging:
Requires specialized thermal shipping containers packed with dry ice. PPE (insulated gloves and safety glasses) must be worn when handling dry ice.

3. Unpacking:
Must be transferred immediately to ultra-cold storage upon arrival or kept in the thermal shipper with dry ice replenished every 5 days.
"""
    )
