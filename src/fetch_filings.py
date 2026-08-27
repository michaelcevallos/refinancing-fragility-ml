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

capex_lookup = {
    (fact.accession, str(fact.period_end)): fact
    for fact in all_facts
    if fact.concept == "us-gaap:PaymentsToAcquirePropertyPlantAndEquipment"
}

debt_repayment_lookup = {
    (fact.accession, str(fact.period_end)): fact
    for fact in all_facts
    if fact.concept == "us-gaap:RepaymentsOfLongTermDebt"
}

interest_paid_lookup = {
    (fact.accession, str(fact.period_end)): fact
    for fact in all_facts
    if fact.concept == "us-gaap:InterestPaid"
}

interest_paid_net_lookup = {
    (fact.accession, str(fact.period_end)): fact
    for fact in all_facts
    if fact.concept == "us-gaap:InterestPaidNet"
}


def get_reported_value(filing, fact_lookup):
    key = (
        filing.accession_no,
        str(filing.period_of_report)
    )

    fact = fact_lookup.get(key)

    if fact is None:
        return None

    return (
        fact.fiscal_year, 
        fact.fiscal_period, 
        fact.numeric_value
    )
    
def build_quarterly_series(filings, fact_lookup):
    reported_values = {}

    for filing in filings:
        result = get_reported_value(filing, fact_lookup)

        if result is None:
            continue

        fiscal_year, fiscal_period, value = result

        reported_values[(fiscal_year, fiscal_period)] = value

    quarterly_values = {}

    years = sorted({year for year, period in reported_values})

    for year in years:
        q1_ytd = reported_values.get((year, "Q1"))
        q2_ytd = reported_values.get((year, "Q2"))
        q3_ytd = reported_values.get((year, "Q3"))
        full_year = reported_values.get((year, "FY"))

        if q1_ytd is not None:
            quarterly_values[(year, "Q1")] = q1_ytd

        if q1_ytd is not None and q2_ytd is not None:
            quarterly_values[(year, "Q2")] = q2_ytd - q1_ytd

        if q2_ytd is not None and q3_ytd is not None:
            quarterly_values[(year, "Q3")] = q3_ytd - q2_ytd

        if q3_ytd is not None and full_year is not None:
            quarterly_values[(year, "Q4")] = full_year - q3_ytd

    return quarterly_values

quarterly_ocf = build_quarterly_series(filings, ocf_lookup)
# print(quarterly_ocf)

quarterly_capex = build_quarterly_series(filings, capex_lookup)
# print(quarterly_capex)

quarterly_debt_repayments = build_quarterly_series(filings, debt_repayment_lookup)
# print(quarterly_debt_repayments)

quarterly_interest_paid = build_quarterly_series(filings, interest_paid_lookup)
# print(quarterly_interest_paid)

quarterly_interest_paid_net = build_quarterly_series(filings, interest_paid_net_lookup)
# print(quarterly_interest_paid_net)