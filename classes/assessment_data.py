class AssessmentData:
	def __init__(self,
	             assessed_value: float,
	             tax_rate: float,
	             exemptions: list[tuple[str, float]] = [],
	             flat_tax: float = 0):
		self.assessed_value = assessed_value
		self.tax_rate = tax_rate
		self.exemptions = exemptions
		self.flat_tax = flat_tax
