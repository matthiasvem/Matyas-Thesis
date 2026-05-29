import time
import random
from typing import Dict, List
import pandas as pd
from pytrends.request import TrendReq

# Country dictionary

country_dict= {
    "Albania": "AL",
    "Algeria": "DZ",
    "Angola": "AO",
    "Argentina": "AR",
    "Armenia": "AM",
    "Australia": "AU",
    "Austria": "AT",
    "Azerbaijan": "AZ",
    "Bahamas, The": "BS",
    "Bahrain": "BH",
    "Bangladesh": "BD",
    "Barbados": "BB",
    "Belarus": "BY",
    "Belgium": "BE",
    "Belize": "BZ",
    "Benin": "BJ",
    "Bhutan": "BT",
    "Bolivia": "BO",
    "Bosnia and Herzegovina": "BA",
    "Botswana": "BW",
    "Brazil": "BR",
    "Brunei Darussalam": "BN",
    "Bulgaria": "BG",
    "Burkina Faso": "BF",
    "Burundi": "BI",
    "Cabo Verde": "CV",
    "Cambodia": "KH",
    "Cameroon": "CM",
    "Canada": "CA",
    "Central African Republic": "CF",
    "Chad": "TD",
    "Chile": "CL",
    "China, People's Republic of": "CN",
    "Colombia": "CO",
    "Comoros": "KM",
    "Congo, Dem. Rep. of the": "CD",
    "Congo, Republic of": "CG",
    "Costa Rica": "CR",
    "Croatia": "HR",
    "Cyprus": "CY",
    "Czech Republic": "CZ",
    "Côte d'Ivoire": "CI",
    "Denmark": "DK",
    "Djibouti": "DJ",
    "Dominican Republic": "DO",
    "Ecuador": "EC",
    "Egypt": "EG",
    "El Salvador": "SV",
    "Estonia": "EE",
    "Eswatini": "SZ",
    "Ethiopia": "ET",
    "Fiji": "FJ",
    "Finland": "FI",
    "France": "FR",
    "Gabon": "GA",
    "Gambia, The": "GM",
    "Georgia": "GE",
    "Germany": "DE",
    "Ghana": "GH",
    "Greece": "GR",
    "Guatemala": "GT",
    "Guinea": "GN",
    "Guinea-Bissau": "GW",
    "Guyana": "GY",
    "Haiti": "HT",
    "Honduras": "HN",
    "Hong Kong SAR": "HK",
    "Hungary": "HU",
    "Iceland": "IS",
    "India": "IN",
    "Indonesia": "ID",
    "Iran": "IR",
    "Iraq": "IQ",
    "Ireland": "IE",
    "Israel": "IL",
    "Italy": "IT",
    "Jamaica": "JM",
    "Japan": "JP",
    "Jordan": "JO",
    "Kazakhstan": "KZ",
    "Kenya": "KE",
    "Korea, Republic of": "KR",
    "Kuwait": "KW",
    "Kyrgyz Republic": "KG",
    "Lao P.D.R.": "LA",
    "Latvia": "LV",
    "Lebanon": "LB",
    "Lesotho": "LS",
    "Liberia": "LR",
    "Libya": "LY",
    "Lithuania": "LT",
    "Luxembourg": "LU",
    "Madagascar": "MG",
    "Malawi": "MW",
    "Malaysia": "MY",
    "Mali": "ML",
    "Malta": "MT",
    "Mauritania": "MR",
    "Mauritius": "MU",
    "Mexico": "MX",
    "Moldova": "MD",
    "Mongolia": "MN",
    "Montenegro": "ME",
    "Morocco": "MA",
    "Mozambique": "MZ",
    "Myanmar": "MM",
    "Namibia": "NA",
    "Nepal": "NP",
    "Netherlands": "NL",
    "New Zealand": "NZ",
    "Nicaragua": "NI",
    "Niger": "NE",
    "Nigeria": "NG",
    "North Macedonia": "MK",
    "Norway": "NO",
    "Oman": "OM",
    "Pakistan": "PK",
    "Panama": "PA",
    "Papua New Guinea": "PG",
    "Paraguay": "PY",
    "Peru": "PE",
    "Philippines": "PH",
    "Poland": "PL",
    "Portugal": "PT",
    "Qatar": "QA",
    "Romania": "RO",
    "Russian Federation": "RU",
    "Rwanda": "RW",
    "Saint Lucia": "LC",
    "Saint Vincent and the Grenadines": "VC",
    "Saudi Arabia": "SA",
    "Senegal": "SN",
    "Serbia": "RS",
    "Seychelles": "SC",
    "Sierra Leone": "SL",
    "Singapore": "SG",
    "Slovak Republic": "SK",
    "Slovenia": "SI",
    "South Africa": "ZA",
    "Spain": "ES",
    "Sri Lanka": "LK",
    "Sudan": "SD",
    "Suriname": "SR",
    "Sweden": "SE",
    "Switzerland": "CH",
    "Syria": "SY",
    "Tajikistan": "TJ",
    "Tanzania": "TZ",
    "Thailand": "TH",
    "Timor-Leste": "TL",
    "Togo": "TG",
    "Trinidad and Tobago": "TT",
    "Tunisia": "TN",
    "Türkiye, Republic of": "TR",
    "Uganda": "UG",
    "Ukraine": "UA",
    "United Arab Emirates": "AE",
    "United Kingdom": "GB",
    "United States": "US",
    "Uruguay": "UY",
    "Venezuela": "VE",
    "Vietnam": "VN",
    "Yemen": "YE",
    "Zambia": "ZM",
    "Zimbabwe": "ZW"
}

# Setup

KEYWORDS: List[str] = ["artificial intelligence"]
TIMEFRAME = "2004-01-01 2025-12-31"
HL = "en-US"
TZ = 360

def fetch_country_trends(pytrends: TrendReq, kw_list: List[str], iso2: str) -> pd.DataFrame:
    pytrends.build_payload(kw_list=kw_list, timeframe=TIMEFRAME, geo=iso2)
    df = pytrends.interest_over_time()
    if df.empty:
        return df
    if "isPartial" in df.columns:
        df = df.drop(columns=["isPartial"])
    return df

def weekly_to_yearly(weekly_df: pd.DataFrame) -> pd.DataFrame:
    out = weekly_df.copy()
    out = out.reset_index()
    out["year"] = out["date"].dt.year
    yearly = out.groupby("year", as_index=False).mean(numeric_only=True)
    return yearly

def main(country_dict: Dict[str, str]) -> None:
    pytrends = TrendReq(hl=HL, tz=TZ)

    all_rows = []
    failures = []

    for i, (country_name, iso2) in enumerate(country_dict.items(), start=1):
        try:
            time.sleep(random.uniform(2.0, 5.0))
            weekly = fetch_country_trends(pytrends, KEYWORDS, iso2)
            if weekly.empty:
                failures.append((country_name, iso2, "No data returned"))
                print(f"[{i}/{len(country_dict)}] {country_name} ({iso2}): no data")
                continue
            yearly = weekly_to_yearly(weekly)
            yearly.insert(0, "country", country_name)
            yearly.insert(1, "iso2", iso2)
            all_rows.append(yearly)
            print(f"[{i}/{len(country_dict)}] {country_name} ({iso2}): OK")

        except Exception as e:
            failures.append((country_name, iso2, str(e)))
            print(f"[{i}/{len(country_dict)}] {country_name} ({iso2}): ERROR -> {e}")
            time.sleep(random.uniform(10.0, 25.0))

    if not all_rows:
        raise RuntimeError("No country data collected.")

    df_trends = pd.concat(all_rows, ignore_index=True)
    rename_map = {kw: kw.lower().replace(" ", "_").replace("-", "_") for kw in KEYWORDS}
    df_trends = df_trends.rename(columns=rename_map)
    df_trends.to_csv("google_trends_ai_country_year.csv", index=False)

    if failures:
        df_fail = pd.DataFrame(failures, columns=["country", "iso2", "reason"])
        df_fail.to_csv("google_trends_failures.csv", index=False)

    print("\nDone.")
    print("Saved: google_trends_ai_country_year.csv")
    if failures:
        print("Saved: google_trends_failures.csv (some countries failed or returned no data)")

if __name__ == "__main__":
    main(country_dict)
