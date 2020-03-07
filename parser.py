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
	
	csv_array = []
	

	for record in tqdm(records):
		csv_row = {
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

		csv_array.append(csv_row)

	return csv_array


root_dir = "/home/rjrequina/Documents/projects/ATLIN_XML_Files"

subdir_1 = glob.iglob(root_dir + '**/*', recursive=True)

xml_files = []
csv_array = []
for sd1 in subdir_1:
     subdir_2 = glob.iglob(sd1 + '**/*', recursive=True)
     for sd2 in subdir_2:
     	subdir_3 = glob.iglob(sd2 + '/For Transmission_*_Full Indexing-Articles')
     	for sd3 in subdir_3:
     		xmls = glob.iglob(sd3 + '/RDB_article_*_Full Indexing Articles.xml')   
     		for xml_file in xmls:
     			print(xml_file)
     			result = parse_xml_file(filename=xml_file)
     			csv_array = csv_array + result
     			print("\n")


with open('articles.csv', 'w') as csvfile:
		fieldnames = [
			'source_pdf',
			'print_start_page',
			'print_end_page',
			'pdf_start_page',
			'pdf_end_page',
			'keyword_control_numbers'
		]
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()
		writer.writerows(csv_array)



