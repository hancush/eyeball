import csv
from difflib import Differ
import io
from pathlib import Path

from lxml import etree
import requests

def scrape_metrics():
    """Retrieve table from data.gov/metrics and return it as list."""

    url = 'https://www.data.gov/metrics'
    response = requests.get(url)
    html = response.text
    tree = etree.HTML(html)
    table_rows = tree.xpath('//tr')
    return table_rows

def make_archive(archive_file):
    """Make an archive file if you don't have one already."""

    archive = Path(archive_file)
    if not archive.is_file():
        make_comparator(archive_file)

def make_comparator():
    """Coerce scraped table into format needed by difflib (list of
    lines with newlines, `\n`, preserved)."""

    parent_agency = None

    data_stream = io.StringIO()        
    writer = csv.writer(data_stream)
    writer.writerow(['parent_agency', 'agency', 'record_count', 'last_updated'])

    for row in scrape_metrics():
        row_data = []
        first = True
        for cell in row.iterchildren('td'):
            if cell.text == 'Total': # last, unnecessary row
                break
            if first:
                cell = cell.find('a')
                if (row.values()) and ('parent-agency' in row.values()[0]):
                    parent_agency = cell.text
                row_data.append(parent_agency)
                first = False
            row_data.append(cell.text.replace(',', ''))
        if row_data:
            writer.writerow(row_data)

    data_string = data_stream.getvalue().replace('\r', '')
    return data_string.splitlines(keepends=True)

def compare_files(archive_file):
    """Diff files & parse result into meaningful takeaways."""

    d = Differ()
    with open(archive_file, 'r') as f:
        diffs = list(d.compare(f.readlines(), make_comparator()))

    changed_agency = None
    old_value = None
    diff_count = 0

    for line in diffs:
        fields = tuple(line.split(','))
        if len(fields) != 4:
            continue
        parent_agency, agency, record_count, last_updated = fields
        if parent_agency.startswith('-'):
            changed_agency = agency
            old_value = record_count
        if parent_agency.startswith('+'):
            if agency == changed_agency:
                delta = int(record_count) - int(old_value)
                action = 'added' if delta > 0 else 'deleted'
                print('%s records from %s %s' % (abs(delta), agency, action))
                diff_count += 1

    if not diff_count:
        print('No changes to report')

