import xml.dom.minidom
import csv
import glob
from tqdm import tqdm


def get_text(nodelist):
	rc = []
	for node in nodelist:
		if node.nodeType == node.TEXT_NODE:
			rc.append(node.data)
	return ''.join(rc)

def parse_print_page(page=""):
	pages = page.split("-")
	return pages

def parse_pdf_page(page=""):
	page = page.lower()
	page = page.replace("f", '')
	pages = page.split("-")
	return pages

def parse_xml_file(filename=''):
	doc = xml.dom.minidom.parse(filename)
	records = doc.getElementsByTagName("marc:record")
	
	csv_array_complete = []
	csv_array_incomplete = []

	for record in tqdm(records):
		csv_row = {
			'title': '',
			'source_pdf': '',
			'print_start_page': '',
			'print_end_page': '',
			'pdf_start_page': '',
			'pdf_end_page': '',
			'keyword_control_numbers': []
		}
		datafields = record.getElementsByTagName("marc:datafield")
		for datafield in datafields:
			attribute = datafield.getAttribute('tag')

			# Title
			if attribute == "245":
				subfields = datafield.getElementsByTagName("marc:subfield")
				for subfield in subfields:
					subattribute = subfield.getAttribute('code')
					if subattribute == 'a':
						csv_row['title'] = get_text(subfield.childNodes)

			# Source file
			if attribute == "773": 
				subfields = datafield.getElementsByTagName("marc:subfield")
				for subfield in subfields:
					subattribute = subfield.getAttribute('code')
					if subattribute == 'w':
						csv_row['source_pdf'] = get_text(subfield.childNodes)

			# Print pages
			if attribute == "944":
				subfields = datafield.getElementsByTagName("marc:subfield")
				for subfield in subfields:
					subattribute = subfield.getAttribute('code')
					if subattribute == 'a':
						pages = parse_print_page(page=get_text(subfield.childNodes))
						if len(pages) == 2:
							csv_row['print_start_page'] = pages[0]
							csv_row['print_end_page'] = pages[1]

			# PDF pages
			if attribute == "983":
				subfields = datafield.getElementsByTagName("marc:subfield")
				for subfield in subfields:
					subattribute = subfield.getAttribute('code')
					if subattribute == 'a':
						pages = parse_pdf_page(page=get_text(subfield.childNodes))
						if len(pages) == 2:
							csv_row['pdf_start_page'] = pages[0]
							csv_row['pdf_end_page'] = pages[1]

			# Keyword control numbers
			if attribute in ["600", "610", "611", "630", "650", "651"]:
				subfields = datafield.getElementsByTagName("marc:subfield")
				for subfield in subfields:
					subattribute = subfield.getAttribute('code')
					if subattribute == '9':
						csv_row['keyword_control_numbers'].append(get_text(subfield.childNodes))

		if len(csv_row['pdf_start_page']) and len(csv_row['pdf_end_page']) and len(csv_row['keyword_control_numbers']):
			csv_array_complete.append(csv_row)
		else:
			if len(csv_row['print_start_page']) and len(csv_row['print_end_page']) and len(csv_row['keyword_control_numbers']):
				csv_array_incomplete.append(csv_row)

	return csv_array_complete, csv_array_incomplete


def filter_nonexisting_issues(csv_filename='', output_filename=''):
	file_dir = ""
	with_issues = []
	no_issues = []
	
	with open(csv_filename) as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		line_count = 0
		for row in csv_reader:
			csv_row = {
				'title': '',
				'source_pdf': '',
				'print_start_page': '',
				'print_end_page': '',
				'pdf_start_page': '',
				'pdf_end_page': '',
				'keyword_control_numbers': []
			}
			if line_count > 0:
				issue_filename = row[1]

				csv_row['title'] = row[0]
				csv_row['source_pdf'] = row[1]
				csv_row['print_start_page'] = row[2]
				csv_row['print_end_page'] = row[3]
				csv_row['pdf_start_page'] = row[4]
				csv_row['pdf_end_page'] = row[5]
				csv_row['keyword_control_numbers'] = row[6]

				subdir_1 = glob.iglob(file_dir + '**/*', recursive=True)
				for sd1 in subdir_1:
				     subdir_2 = glob.iglob(sd1 + '/', + issue_filename + '.pdf')
				     if len(subdir_2):
				     	with_issues.append(csv_row)
				     else:
				     	no_issues.append(csv_row)

				line_count += 1 
			else:
				line_count += 1
	
	with open(output_filename + '-with_issues', 'w') as csvfile:
		fieldnames = [
			'title',
			'source_pdf',
			'print_start_page',
			'print_end_page',
			'pdf_start_page',
			'pdf_end_page',
			'keyword_control_numbers'
		]
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()
		writer.writerows(with_issues)

	with open(output_filename + '-no_issues', 'w') as csvfile:
		fieldnames = [
			'title',
			'source_pdf',
			'print_start_page',
			'print_end_page',
			'pdf_start_page',
			'pdf_end_page',
			'keyword_control_numbers'
		]
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()
		writer.writerows(no_issues)

root_dir = "/home/rjrequina/Documents/projects/ATLIN_XML_Files"

subdir_1 = glob.iglob(root_dir + '**/*', recursive=True)

xml_files = []
csv_array_complete = []
csv_array_incomplete = []
for sd1 in subdir_1:
     subdir_2 = glob.iglob(sd1 + '**/*', recursive=True)
     for sd2 in subdir_2:
     	subdir_3 = glob.iglob(sd2 + '/For Transmission_*_Full Indexing-Articles')
     	for sd3 in subdir_3:
     		xmls = glob.iglob(sd3 + '/RDB_article_*_Full Indexing Articles.xml')   
     		for xml_file in xmls:
     			print(xml_file)
     			result = parse_xml_file(filename=xml_file)
     			csv_array_complete = csv_array_complete + result[0]
     			csv_array_incomplete = csv_array_incomplete + result[1]
     			print("\n")


with open('articles-complete.csv', 'w') as csvfile:
		fieldnames = [
			'title',
			'source_pdf',
			'print_start_page',
			'print_end_page',
			'pdf_start_page',
			'pdf_end_page',
			'keyword_control_numbers'
		]
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()
		writer.writerows(csv_array_complete)

with open('articles-incomplete.csv', 'w') as csvfile:
		fieldnames = [
			'title',
			'source_pdf',
			'print_start_page',
			'print_end_page',
			'pdf_start_page',
			'pdf_end_page',
			'keyword_control_numbers'
		]
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()
		writer.writerows(csv_array_incomplete)


