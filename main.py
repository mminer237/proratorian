from classes.assessment_data import AssessmentData
from datetime import datetime
import dateutil.parser
from functools import reduce
import glob
import os
import platformdirs
import sys
import yaml

# Check if config file exists
script_dir = sys.path[0]
try:
	with open(script_dir + "/config.yaml") as f:
		config = yaml.safe_load(f)
except Exception:
	config_dir = platformdirs.user_config_dir("proratorian")
	try:
		with open(config_dir + "/config.yaml") as f:
			config = yaml.safe_load(f)
	except Exception:
		pass
	
if "config" in locals():
	if "clients_directories" in config:
		client_name = input("Enter client name: ")
		if client_name:
			for clients_directory in config["clients_directories"]:
				folders = list(filter(lambda x: os.path.isdir(x), glob.glob(clients_directory + "/*" + client_name + "*")))
				folders.sort(key=lambda x: os.path.getmtime(x), reverse=True)
				for folder in folders:
					response = input(folder + "? (Y/n): ")
					if not response or response[0].lower() == "y":
						client_directory = folder
						break
				if "client_directory" in locals():
					break
			if "client_directory" not in locals():
				raise Exception("Client not found")

# Get county name from user or use parameter if passed
if len(sys.argv) > 1:
	county_name = sys.argv[1]
else:
	county_name = input("Enter county name: ")
county_name = county_name.lower().replace(" ", "_")

# Check if county package exists
try:
	exec("from counties import " + county_name + " as county")
except ModuleNotFoundError:
	raise Exception("County module not found")

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
if hasattr(county, "INCLUDES_CLOSING_DATE"):
	if not county.INCLUDES_CLOSING_DATE:
		days_through_year -= 1
days_in_year = 365 + int(closing_date.year % 4 == 0 and (closing_date.year % 100 != 0 or closing_date.year % 400 == 0))

# Calculate taxes
exemptions = reduce(lambda a, x: (None, a[1] + x[1]), data.exemptions, (None, 0))[1]
taxed_value = data.assessed_value - exemptions
total_tax = taxed_value * data.tax_rate + data.flat_tax
total_tax_explanation = f"${taxed_value:,.2f} × {data.tax_rate * 100:f}%"
if data.flat_tax > 0:
	total_tax_explanation += f" + ${data.flat_tax:,.2f}"
prorated_tax = total_tax * days_through_year / days_in_year

# Pretty-print dollar amounts
stdout = sys.stdout
sys.stdout = sys.stdout if "client_directory" not in locals() else open(f"{client_directory}/prorations.txt", "w")
print(f"Assessed value ({data.assessment_year}): ${data.assessed_value:,.0f}")
print(f"Exemptions ({data.exemptions_year}): ${exemptions:,.0f}")
print(f"Taxed value: ${data.assessed_value - exemptions:,.2f}")
print(f"Tax rate ({data.rate_year}): {data.tax_rate * 100:f}%")
print(f"Total tax: ${total_tax:,.2f} ({total_tax_explanation})")
print(f"Prorated tax: ${prorated_tax:,.2f} (${total_tax:,.2f} × {days_through_year} ÷ {days_in_year})")
if "client_directory" in locals():
	sys.stdout.close()
	sys.stdout = stdout
