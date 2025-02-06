from weasyprint import HTML
from datetime import datetime as dt


def html_to_pdf(html_content, output_path):
    HTML(string=html_content).write_pdf(output_path)

# HTML content
with open(f"/home/rob/AWSLambdaScripts/Umbrella-Reports/reports/umbrella_report {dt.now().date()}.html",'r', encoding='utf-8') as f:
    html_content = f.read()
print(html_content)

output_path = f"/home/rob/AWSLambdaScripts/Umbrella-Reports/pdfs/umbrella_report {dt.now().date()}.pdf"
html_to_pdf(html_content, output_path)
