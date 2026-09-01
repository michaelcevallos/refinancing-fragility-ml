import pandas as pd
from edgar import Company, set_identity

set_identity("Michael Cevallos michael.cevallos2602@gmail.com")


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
        fact.numeric_value,
        str(filing.filing_date)
    )
    
def build_quarterly_series(filings, fact_lookup):
    reported_values = {}

    for filing in filings:
        result = get_reported_value(filing, fact_lookup)

        if result is None:
            continue

        fiscal_year, fiscal_period, value, filing_date = result

        reported_values[(fiscal_year, fiscal_period)] = {
            "value": value,
            "filing_date": filing_date
        }

    quarterly_values = {}

    years = sorted({year for year, period in reported_values})

    for year in years:
        q1 = reported_values.get((year, "Q1"))
        q2 = reported_values.get((year, "Q2"))
        q3 = reported_values.get((year, "Q3"))
        fy = reported_values.get((year, "FY"))

        if q1 is not None:
            quarterly_values[(year, "Q1")] = {
                "value": q1["value"],
                "filing_date": q1["filing_date"]
            }

        if q1 is not None and q2 is not None:
            quarterly_values[(year, "Q2")] = {
                "value": q2["value"] - q1["value"],
                "filing_date": q2["filing_date"]
            }

        if q2 is not None and q3 is not None:
            quarterly_values[(year, "Q3")] = {
                "value": q3["value"] - q2["value"],
                "filing_date": q3["filing_date"]
            }

        if q3 is not None and fy is not None:
            quarterly_values[(year, "Q4")] = {
                "value": fy["value"] - q3["value"],
                "filing_date": fy["filing_date"]
            }

    return quarterly_values

def build_snapshot_series(filings, fact_lookup):
    snapshot_values = {}

    for filing in filings:
        key = (filing.accession_no, str(filing.period_of_report))
        fact = fact_lookup.get(key)

        if fact is None:
            continue

        quarter = "Q4" if fact.fiscal_period == "FY" else fact.fiscal_period

        snapshot_values[(fact.fiscal_year, quarter)] = {
            "value": fact.numeric_value,
            "filing_date": str(filing.filing_date)
        }

    return snapshot_values

def build_fact_lookup(all_facts, concept):
    fact_lookup = {}

    for fact in all_facts:
        if fact.concept != concept:
            continue

        key = (fact.accession, str(fact.period_end))
        existing_fact = fact_lookup.get(key)

        if existing_fact is None or fact.period_start < existing_fact.period_start:
            fact_lookup[key] = fact

    return fact_lookup

def build_instant_fact_lookup(all_facts, concept):
    fact_lookup = {}

    for fact in all_facts:
        if fact.concept != concept:
            continue

        key = (fact.accession, str(fact.period_end))

        if key not in fact_lookup:
            fact_lookup[key] = fact

    return fact_lookup

def build_first_available_fact_lookup(all_facts, concepts):
    for concept in concepts:
        fact_lookup = build_fact_lookup(all_facts, concept)

        if fact_lookup:
            return fact_lookup

    return {}

def build_company_dataset(ticker):
    company = Company(ticker)
    filings = company.get_filings(form=["10-K", "10-Q"])
    all_facts = company.facts.get_all_facts()

    ocf_lookup = build_fact_lookup(all_facts, "us-gaap:NetCashProvidedByUsedInOperatingActivities")
    capex_lookup = build_fact_lookup(all_facts, "us-gaap:PaymentsToAcquirePropertyPlantAndEquipment")
    debt_repayment_lookup = build_first_available_fact_lookup(all_facts, [
    "us-gaap:RepaymentsOfLongTermDebt",
    "us-gaap:RepaymentsOfDebtMaturingInMoreThanThreeMonths"
    ])
    interest_paid_lookup = build_fact_lookup(all_facts, "us-gaap:InterestPaid")
    interest_paid_net_lookup = build_fact_lookup(all_facts, "us-gaap:InterestPaidNet")
    taxes_paid_lookup = build_fact_lookup(all_facts, "us-gaap:IncomeTaxesPaidNet")
    cash_lookup = build_instant_fact_lookup(all_facts, "us-gaap:CashAndCashEquivalentsAtCarryingValue")
    short_term_investments_lookup = build_instant_fact_lookup(all_facts, "us-gaap:ShortTermInvestments")
    liquid_assets_lookup = build_instant_fact_lookup(all_facts, "us-gaap:CashCashEquivalentsAndShortTermInvestments")

    quarterly_ocf = build_quarterly_series(filings, ocf_lookup)
    quarterly_capex = build_quarterly_series(filings, capex_lookup)
    quarterly_debt_repayments = build_quarterly_series(filings, debt_repayment_lookup)
    quarterly_interest_paid = build_quarterly_series(filings, interest_paid_lookup)
    quarterly_interest_paid_net = build_quarterly_series(filings, interest_paid_net_lookup)
    quarterly_taxes_paid = build_quarterly_series(filings, taxes_paid_lookup)
    quarterly_cash = build_snapshot_series(filings, cash_lookup)
    quarterly_short_term_investments = build_snapshot_series(filings, short_term_investments_lookup)
    quarterly_liquid_assets = build_snapshot_series(filings, liquid_assets_lookup)

    all_quarters = sorted(
        set(quarterly_ocf)
        | set(quarterly_capex)
        | set(quarterly_debt_repayments)
        | set(quarterly_interest_paid)
        | set(quarterly_interest_paid_net)
        | set(quarterly_taxes_paid)
        | set(quarterly_cash)
        | set(quarterly_short_term_investments)
        | set(quarterly_liquid_assets)
    )

    rows = []

    for fiscal_year, quarter in all_quarters:
        rows.append({
            "ticker": ticker, 
            "fiscal_year": fiscal_year,
            "quarter": quarter,
            "filing_date": quarterly_ocf.get((fiscal_year, quarter), {}).get("filing_date"),
            "ocf": quarterly_ocf.get((fiscal_year, quarter), {}).get("value"),
            "capex": quarterly_capex.get((fiscal_year, quarter), {}).get("value"),
            "debt_repayments": quarterly_debt_repayments.get((fiscal_year, quarter), {}).get("value"),
            "interest_paid": quarterly_interest_paid.get((fiscal_year, quarter), {}).get("value"),
            "interest_paid_net": quarterly_interest_paid_net.get((fiscal_year, quarter), {}).get("value"),
            "taxes_paid": quarterly_taxes_paid.get((fiscal_year, quarter), {}).get("value"),
            "cash": quarterly_cash.get((fiscal_year, quarter), {}).get("value"),
            "short_term_investments": quarterly_short_term_investments.get((fiscal_year, quarter), {}).get("value"),
            "liquid_assets": quarterly_liquid_assets.get((fiscal_year, quarter), {}).get("value")
        })

    df = pd.DataFrame(rows)

    df["filing_date"] = pd.to_datetime(df["filing_date"])
    df["information_year"] = df["filing_date"].dt.year.astype("Int64")
    df["information_quarter"] = "Q" + df["filing_date"].dt.quarter.astype("Int64").astype(str)

    return df

df = build_company_dataset("MSFT")

print(df.tail(20).to_string(index=False))