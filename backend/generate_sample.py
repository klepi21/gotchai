from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'RESIDENTIAL LEASE AGREEMENT', 0, 1, 'C')
        self.ln(10)

    def chapter_title(self, num, label):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Section %d : %s' % (num, label), 0, 1, 'L')
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 10, body)
        self.ln()

pdf = PDF()
pdf.add_page()

# Standard looking top part
pdf.chapter_title(1, 'Parties')
pdf.chapter_body('This Lease Agreement ("Lease") is made by and between LANDLORD ("Landlord") and TENANT ("Tenant").')

pdf.chapter_title(2, 'Term')
pdf.chapter_body('The term of this Lease shall begin on [START DATE] and end on [END DATE].')

# TRAP 1: Unilateral Change (Predatory)
pdf.chapter_title(3, 'Rent and Adjustments')
pdf.chapter_body('Tenant agrees to pay rent in the amount of $2,000 per month. Landlord reserves the right to increase the Rent at any time during the Term with 24 hours notice to Tenant, based on market conditions or Landlord\'s discretion.')

# TRAP 2: Hidden Fees (Predatory)
pdf.chapter_title(4, 'Maintenance and Fees')
pdf.chapter_body('Tenant shall be responsible for all maintenance of the property. In addition, an administrative convenience fee of $150 shall be added to each monthly payment for processing. A "Move-Out Assessment Fee" of $500 is mandatory upon termination.')

# TRAP 3: Liability Shift (Critical)
pdf.chapter_title(5, 'Indemnification')
pdf.chapter_body('Tenant agrees to indemnify and hold Landlord harmless from any claims, damages, or injuries occurring on the property, including those caused by Landlord\'s own negligence or failure to maintain the premises.')

# TRAP 4: Jury Waiver (Critical)
pdf.chapter_title(6, 'Dispute Resolution')
pdf.chapter_body('TENANT WAIVES KEY RIGHTS TO TRIAL BY JURY and agrees that any disputes shall be resolved by binding arbitration selected solely by the Landlord. Tenant waives any right to join a class action lawsuit.')

# Standard looking bottom part
pdf.chapter_title(7, 'Governing Law')
pdf.chapter_body('This Lease shall be governed by the laws of the State.')

output_path = "../frontend/public/sample_contract.pdf"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
pdf.output(output_path, 'F')
print(f"Generated sample contract at {output_path}")
