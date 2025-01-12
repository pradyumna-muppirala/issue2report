import json
import argparse
from core.pdf import PDF
from datetime import date
from core.build import Build
from core.github import Github
from core.template import Template
from PyPDF4 import PdfFileMerger

from datetime import datetime

now = datetime.now() # current date and time


token = open(".token","r").read().strip()
output_dir = "output"

parser = argparse.ArgumentParser(description = "Issue2Report - Pentest report generator")
parser.add_argument("-t", "--template", action = "store", dest = "template",required = True, help = "Report template name")
parser.add_argument("-gu", "--github-user", action = "store", dest = "github_user",required = True, help = "Github Username")
parser.add_argument("-gr", "--github-repo", action = "store", dest = "github_repo",required = True, help = "Github Repository name")

args = parser.parse_args()

g = Github(token,args.github_user,args.github_repo)
t = Template(args.template,output_dir,g)
p = PDF(output_dir,t)

css_file = "templates/{}/vulnerabilities.css".format(args.template)
customer = json.loads(g.get_file("infos.json"))
template_frozen_opts = t.get_frozen_opts()
frozen_opts = {"{{DATE}}":date.today().strftime("%d/%m/%Y") }
frozen_opts.update(customer)
frozen_opts.update(template_frozen_opts)
strNow = now.strftime("%m-%d-%Y-%H-%M-%S")
report_name = "OWASP_webGoat-pentest-final-report-by-ASTICI.pdf"
print(frozen_opts)
b = Build(output_dir,frozen_opts,p,g,t)

b.build_templates(frozen_opts["{{CUSTOMER}}"])

issues = g.get_issues_by_repo()
merger = PdfFileMerger(strict=False)
# Add cover into merger
merger.append(fileobj=open(output_dir + "/cover.pdf", 'rb'), import_bookmarks=True)
# Add intro pdf into merger
merger.append(fileobj=open(output_dir + "/intro.pdf", 'rb'), import_bookmarks=True)

for issue in issues:
    pdf_file = "{}/{}-{}.pdf".format(output_dir, issue["number"], issue["title"].strip().replace(" ","_").lower())
    md = b.generate_report_md(issue)
    p.md_to_pdf(pdf_file,md,css_file)
    merger.append(fileobj=open(pdf_file, 'rb'), import_bookmarks=True)

# Add conclusion pdf into merger
merger.append(fileobj=open(output_dir + "/conclusion.pdf", 'rb'), import_bookmarks=True)

print(report_name)
merger.write(fileobj=open(report_name, 'wb'))
merger.close()