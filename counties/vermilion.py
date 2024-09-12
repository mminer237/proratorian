from bs4 import BeautifulSoup, Tag
from functools import cache
from classes.assessment_data import AssessmentData
import re
import requests

INCLUDES_CLOSING_DATE = False

def load(pin: str, year: int) -> AssessmentData:
	pin = pin.strip().replace("-", "")
	if not re.match(r"^\d{10}$", pin):
		raise Exception("Invalid PIN")

	# Get page
	page_soup = get_page_soup(pin, year)
	if not page_soup.find('h4', string=re.compile(' : ' + str(year))):
		raise Exception("Could not find property information for year " + str(year))

	# Get assessed value
	try:
		assessed_value = get_assessed_value(page_soup)
		assessment_year = year
	except:
		for i in range(1, 3):
			try:
				assessed_value = get_assessed_value(get_page_soup(pin, year - i))
				assessment_year = year - i
				break
			except:
				pass


	# Get tax rate
	try:
		tax_rate = get_tax_rate(page_soup)
		rate_year = year
	except:
		for i in range(1, 3):
			try:
				tax_rate = get_tax_rate(get_page_soup(pin, year - i))
				rate_year = year - i
				break
			except:
				pass

	# Get exemptions
	try:
		exemptions = get_exemptions(page_soup)
		exemptions_year = year
	except:
		for i in range(1, 3):
			try:
				exemptions = get_exemptions(get_page_soup(pin, year - i))
				exemptions_year = year - i
				break
			except:
				pass

	# Remove commas and convert to float
	assessed_value = float(assessed_value.replace(",", ""))

	return AssessmentData(
		assessed_value=assessed_value,
		assessment_year=assessment_year,
		tax_rate=tax_rate,
		rate_year=rate_year,
		exemptions=exemptions,
		exemptions_year=exemptions_year
	)

@cache
def get_page_soup(pin: str, year: int) -> BeautifulSoup:
	url = "https://vermilionil.devnetwedge.com/parcel/view/" + pin + "/" + str(year)
	page = requests.get(url).text
	if not page:
		raise Exception("Page is empty")
	page_soup = BeautifulSoup(page, 'html.parser')
	if not page_soup.find('body'):
		raise Exception("Page is corrupted")
	return page_soup

def get_assessed_value(page_soup: BeautifulSoup):
	board_of_review_cell = page_soup.find('td', string=re.compile('Board of Review'))
	if board_of_review_cell and board_of_review_cell.parent:
		board_of_review_row = board_of_review_cell.parent
		assessed_value = board_of_review_row.find_all('td')[-1].text
	else:
		raise Exception("Could not find Board of Review assessment")
	return assessed_value

def get_tax_rate(page_soup: BeautifulSoup) -> float:
	tax_rate_header = page_soup.find('div', text='Tax Rate')
	if not tax_rate_header:
		raise Exception("Could not find Tax Rate box")
	tax_rate = tax_rate_header.find_next_sibling('div')
	if not tax_rate:
		raise Exception("Could not find Tax Rate")
	return float(tax_rate.text) / 100

def get_exemptions(page_soup: BeautifulSoup) -> list[tuple[str, float]]:
	exemptions = []
	exemption_header = page_soup.find('h3', text='Exemptions')
	if exemption_header and exemption_header.parent and exemption_header.parent.parent:
		exemption_table = exemption_header.parent.parent.find_next('tbody')
		if isinstance(exemption_table, Tag):
			for row in exemption_table.find_all('tr'):
				row_cells = row.find_all('td')
				exemptions.append((row_cells[0].text, float(row_cells[-1].text.replace(",", ""))))
	return exemptions
