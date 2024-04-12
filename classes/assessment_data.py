class AssessmentData:
	def __init__(self,
	             assessed_value: float,
				 assessment_year: int,
	             tax_rate: float,
				 rate_year: int,
	             exemptions: list[tuple[str, float]] = [],
				 exemptions_year: int | None = None,
	             flat_tax: float = 0,
				 flat_tax_year: int | None = None):
		self.assessed_value = assessed_value
		self.assessment_year = assessment_year
		self.tax_rate = tax_rate
		self.rate_year = rate_year
		self.exemptions = exemptions
		self.exemptions_year = exemptions_year
		self.flat_tax = flat_tax
		self.flat_tax_year = flat_tax_year
