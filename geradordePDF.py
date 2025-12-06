from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

text = """Ficha de Admissão de Funcionário

Nome: João da Silva
Data de Nascimento: 15/04/1990

Documentos:
- RG: 12.345.678-9
- CPF: 123.456.789-00

Endereço:
Rua Exemplo, 123
Bairro Central
Cidade Exemplar - SP
CEP: 12345-678

Contato:
Telefone: (11) 91234-5678
E-mail: joao.silva@example.com
"""

for line in text.split("\n"):
    pdf.cell(0, 10, txt=line, ln=True)

pdf.output("ficha_admissao.pdf")
print("PDF gerado com sucesso: ficha_admissao.pdf")
