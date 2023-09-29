from classes.assessment_data import AssessmentData
from datetime import datetime
import dateutil.parser
from functools import reduce
import sys

# Get county name from user or use parameter if passed
if len(sys.argv) > 1:
	county_name = sys.argv[1]
else:
	county_name = input("Enter county name: ").lower().replace(" ", "_")

# Check if county package exists
try:
	exec("from counties import " + county_name + " as county")
except ModuleNotFoundError:
	raise Exception("County module not found")
	sys.exit()

# Get parcel number from user or use parameter if passed
if len(sys.argv) > 2:
	pin = sys.argv[2]
else:
	pin = input("Enter parcel number: ")

# Get closing date from user or use parameter if passed
if len(sys.argv) > 3:
	closing_date = sys.argv[3]
else:
	closing_date = input("Enter closing date: ")
closing_date = closing_date
try:
	closing_date = dateutil.parser.parse(closing_date)
except:
	pass
if not isinstance(closing_date, datetime):
	raise Exception("Invalid date")

# Get data from county package
data: AssessmentData = county.load(pin, closing_date.year)
assert isinstance(data, AssessmentData)

days_through_year = closing_date.timetuple().tm_yday
days_in_year = 365 + int(closing_date.year % 4 == 0 and (closing_date.year % 100 != 0 or closing_date.year % 400 == 0))

# Calculate taxes
exemptions = reduce(lambda a, x: (None, a[1] + x[1]), data.exemptions, (None, 0))[1]
total_tax = (data.assessed_value - exemptions) * data.tax_rate + data.flat_tax
prorated_tax = total_tax * days_through_year / days_in_year
# Pretty-print dollar amounts
print(f"Assessed value: ${data.assessed_value:,.0f}")
print(f"Exemptions: ${exemptions:,.0f}")
print(f"Taxed value: ${data.assessed_value - exemptions:,.2f}")
print(f"Tax rate: {data.tax_rate * 100:f}%")
print(f"Total tax: ${total_tax:,.2f}")
print(f"Prorated tax: ${prorated_tax:,.2f}")
