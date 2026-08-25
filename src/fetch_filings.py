from edgar import Company, set_identity

set_identity("Michael Cevallos michael.cevallos2602@gmail.com")

company = Company("AAPL")
filings = company.get_filings(form=["10-K", "10-Q"])

all_facts = company.facts.get_all_facts()

ocf_lookup = {
    (fact.accession, str(fact.period_end)): fact
    for fact in all_facts
    if fact.concept == "us-gaap:NetCashProvidedByUsedInOperatingActivities"
}

quarterly_ocf = {}


def get_reported_ocf(filing, ocf_lookup):
    key = (
        filing.accession_no,
        str(filing.period_of_report)
    )

    ocf_fact = ocf_lookup.get(key)

    if ocf_fact is None:
        return None

    return (
        ocf_fact.fiscal_year, 
        ocf_fact.fiscal_period, 
        ocf_fact.numeric_value
    )
    
reported_ocf = {}

for filing in filings:
    result = get_reported_ocf(filing, ocf_lookup)

    if result is None:
        continue

    fiscal_year, fiscal_period, ocf = result

    reported_ocf[(fiscal_year, fiscal_period)] = ocf

years = sorted({year for year, period in reported_ocf})

for year in years:
    q1_ytd = reported_ocf.get((year, "Q1"))
    q2_ytd = reported_ocf.get((year, "Q2"))
    q3_ytd = reported_ocf.get((year, "Q3"))
    full_year = reported_ocf.get((year, "FY"))

    if q1_ytd is not None:
        quarterly_ocf[(year, "Q1")] = q1_ytd

    if q1_ytd is not None and q2_ytd is not None:
        quarterly_ocf[(year, "Q2")] = q2_ytd - q1_ytd

    if q2_ytd is not None and q3_ytd is not None:
        quarterly_ocf[(year, "Q3")] = q3_ytd - q2_ytd

    if q3_ytd is not None and full_year is not None:
        quarterly_ocf[(year, "Q4")] = full_year - q3_ytd

print(quarterly_ocf)