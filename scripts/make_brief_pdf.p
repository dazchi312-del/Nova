from fpdf import FPDF

class NovaBriefPDF(FPDF):
    def header(self):
        # Setting up the header with Nova branding style
        self.set_font('Arial', 'B', 16)
        self.set_text_color(40, 44, 52)
        self.cell(0, 10, 'PROJECT NOVA: NOE EDUCATIONAL BRIEF', 0, 1, 'C')
        self.set_draw_color(0, 122, 204) # Nova Blue
        self.line(10, 22, 200, 22)
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Phase 12 Configuration - Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, label):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 10, label, 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, text):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 6, text)
        self.ln()

# Initialize PDF
pdf = NovaBriefPDF()
pdf.add_page()

# --- CONTENT SECTIONS ---
sections = [
    ("Executive Summary", 
     "Nova is a self-improving AI output system utilizing a secondary AI to judge and refine outputs. "
     "This creates a deterministic feedback loop where the system recognizes limitations and improves "
     "autonomously without human intervention."),
    
    ("The Architecture (Primary vs. Reflector)", 
     "• Primary Node: Lenovo Legion Pro 7i (Nemotron 70B) - The Generator.\n"
     "• Validation Node: MacBook Pro M4 (Llama 3.1 8B) - The Reflector.\n"
     "Logic: Evaluation is computationally 'cheaper' than generation. The smaller Llama model "
     "acts as a high-speed critic for the larger Nemotron model."),
    
    ("The Scoring Matrix", 
     "Every output is scored 0.0 to 1.0 across five dimensions:\n"
     "1. Quality (30%): Overall technical excellence.\n"
     "2. Clarity (25%): Ease of understanding.\n"
     "3. Structure (20%): Logical organization.\n"
     "4. Hallucination Risk (15%): Fact-checking (Inverted score).\n"
     "5. Identity Alignment (10%): Persona consistency."),
    
    ("The Processing Loop", 
     "1. Generate: Nemotron creates the draft.\n"
     "2. Score: Reflector evaluates the draft.\n"
     "3. Decide: If Score < 0.85, trigger Refinement.\n"
     "4. Refine: Feedback is injected back into the prompt for a second, better pass."),
    
    ("Technical Insight: Defensive JSON Extraction", 
     "LLMs are probabilistic and often fail to format JSON perfectly. NOE uses a 'Defense in Depth' "
     "parsing strategy with 6 fallback layers (Regex, Markdown stripping, etc.) to ensure the "
     "scoring data is captured even if the AI gets chatty.")
]

for title, body in sections:
    pdf.chapter_title(title)
    pdf.chapter_body(body)

# Output to your project folder
output_path = "Nova_Output_Engine_Brief.pdf"
pdf.output(output_path)
print(f"Success: {output_path} generated.")