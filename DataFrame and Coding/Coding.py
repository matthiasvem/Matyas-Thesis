#--------------------------------------------------------------------------------------------------------------------
# Modules and Paths
import re
import unicodedata
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt

trends_path     = "Inputs/google_trends_ai_country_year.csv"  
aip_path        = "Inputs/aip.xlsx"                       
gdp_path        = "Inputs/GDP_growth.xlsx"                     
hdi_path        = "Inputs/HDI.xlsx"                              
invest_path     = "Inputs/investment.xlsx"
fdi_path        = "Inputs/fdi.xlsx"
trade_path      = "Inputs/trade.xlsx"
inflation_path  = "Inputs/inflation.xlsx"

output_path     = "Outputs/df.xlsx"

#--------------------------------------------------------------------------------------------------------------------
# Getting to DataFrame (df) 
# From datasets, at the end there is a file that contains all variables used plus Prepearness index.

#--------------------------------------------------------------------------------------------------------------------
# - Supporter Functions -

def clean_country(s: str) -> str:
    if pd.isna(s):
        return s
    s = str(s).strip().replace("\u00a0", " ")
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"\s+", " ", s)
    return s

# - Loading dataa -

df_trends = pd.read_csv(trends_path)

aip_raw = pd.read_excel(aip_path)

gdp_wide = pd.read_excel(gdp_path)

hdi_raw = pd.read_excel(hdi_path)

inv_wide = pd.read_excel(invest_path)

fdi_wide = pd.read_excel(fdi_path)

trade_wide = pd.read_excel(trade_path)

inflation_wide = pd.read_excel(inflation_path)

# - Google Trends -

df_trends["year"] = df_trends["year"].astype(int)
df_trends["artificial_intelligence"] = pd.to_numeric(df_trends["artificial_intelligence"], errors="coerce")

# - AI readiness (at the end not used ): ) -

df_ai = aip_raw.rename(columns={"AI Preparedness Index (Index)": "country",2023: "ai_readiness_2023"})[["country", "ai_readiness_2023"]]

# - GDP per capita -

year_cols = [c for c in gdp_wide.columns if re.fullmatch(r"\d{4}", str(c))]
gdp_long = gdp_wide.melt(id_vars=["Country Name", "Country Code"],value_vars=year_cols,var_name="year",value_name="gdp_pc_growth",).rename(columns={"Country Name": "country","Country Code": "iso3"})
gdp_long["year"] = gdp_long["year"].astype(int)
gdp_long["gdp_pc_growth"] = pd.to_numeric(gdp_long["gdp_pc_growth"], errors="coerce")

# - HDI -

df_hdi = hdi_raw[hdi_raw["indicatorCode"].astype(str).str.lower().eq("hdi")].rename(columns={"value": "hdi"})[["country", "year", "hdi"]]
df_hdi["year"] = df_hdi["year"].astype(int)
df_hdi["hdi"] = pd.to_numeric(df_hdi["hdi"], errors="coerce")

# - Control1 Investment -

id_vars_inv = ["Country Name"]
if "Country Code" in inv_wide.columns:
    id_vars_inv.append("Country Code")
year_cols_inv = [c for c in inv_wide.columns if re.fullmatch(r"\d{4}", str(c))]
inv_long = inv_wide.melt(id_vars=id_vars_inv,value_vars=year_cols_inv,var_name="year",value_name="investment",).rename(columns={"Country Name": "country"})
inv_long["year"] = inv_long["year"].astype(int)
inv_long["investment"] = pd.to_numeric(inv_long["investment"], errors="coerce")

# - Control2 FDI -

id_vars_fdi = ["Country Name"]
if "Country Code" in fdi_wide.columns:
    id_vars_fdi.append("Country Code")
year_cols_fdi = [c for c in fdi_wide.columns if re.search(r"\d{4}", str(c))]
fdi_long = fdi_wide.melt(id_vars=id_vars_fdi,value_vars=year_cols_fdi,var_name="year",value_name="fdi",).rename(columns={"Country Name": "country"})
fdi_long["year"] = fdi_long["year"].astype(str).str.extract(r"(\d{4})").astype(int)
fdi_long["fdi"] = pd.to_numeric(fdi_long["fdi"].replace("..", np.nan),errors="coerce")

# - Control3 Trade openness (percetage of overall GDP) -

id_vars_trade = ["Country Name"]
if "Country Code" in trade_wide.columns:
    id_vars_trade.append("Country Code")
year_cols_trade = [c for c in trade_wide.columns if re.fullmatch(r"\d{4}", str(c))]
trade_long = trade_wide.melt(id_vars=id_vars_trade,value_vars=year_cols_trade,var_name="year",value_name="trade_openness",).rename(columns={"Country Name": "country"})
trade_long["year"] = trade_long["year"].astype(int)
trade_long["trade_openness"] = pd.to_numeric(trade_long["trade_openness"],errors="coerce")

# - Control4 Inflation -

id_vars_inf = ["Country Name"]
if "Country Code" in inflation_wide.columns:
    id_vars_inf.append("Country Code")
year_cols_inf = [c for c in inflation_wide.columns if re.search(r"\d{4}", str(c))]
inflation_long = inflation_wide.melt(id_vars=id_vars_inf,value_vars=year_cols_inf,var_name="year",value_name="inflation",).rename(columns={"Country Name": "country"})
inflation_long["year"] = inflation_long["year"].astype(str).str.extract(r"(\d{4})").astype(int)
inflation_long["inflation"] = pd.to_numeric(inflation_long["inflation"].replace("..", np.nan),errors="coerce")

# - Names fixing (country names are diff) -

for d in (df_trends, df_ai, gdp_long, df_hdi, inv_long,fdi_long,trade_long,inflation_long):
    d["country"] = d["country"].apply(clean_country)
name_fix = {"Türkiye, Republic of": "Turkey","Côte d'Ivoire": "Cote d'Ivoire","Korea, Republic of": "Korea, Rep.","Russian Federation": "Russia","Slovak Republic": "Slovakia","Lao P.D.R.": "Lao PDR","Congo, Republic of": "Congo, Rep.","Congo, Republic of ": "Congo, Rep.",
    "Congo, Dem. Rep. of the": "Congo, Dem. Rep.","Gambia, The": "Gambia","Bahamas, The": "Bahamas","Hong Kong SAR": "Hong Kong SAR, China","China, People's Republic of": "China","North Macedonia ": "North Macedonia",
    "Egypt, Arab Rep.": "Egypt","Czechia": "Czech Republic","Iran, Islamic Rep.": "Iran","St. Lucia": "Saint Lucia","St. Vincent and the Grenadines": "Saint Vincent and the Grenadines","Turkiye": "Turkey","Venezuela, RB": "Venezuela","Viet Nam": "Vietnam","Yemen, Rep.": "Yemen",}
for d in (df_trends, df_ai, gdp_long, df_hdi, inv_long,fdi_long,trade_long,inflation_long):
    d["country"] = d["country"].replace(name_fix)

# - Missing vals fill for ONLY HDI at tehh end -

# 2024-2025 HDI = 2023 HDI

hdi_2023 = (df_hdi[df_hdi["year"] == 2023][["country", "hdi"]].rename(columns={"hdi": "hdi_2023"}))
df_hdi = df_hdi.merge(hdi_2023, on="country", how="left")
mask_hdi_fill = df_hdi["year"].isin([2024, 2025]) & df_hdi["hdi"].isna()
df_hdi.loc[mask_hdi_fill, "hdi"] = df_hdi.loc[mask_hdi_fill, "hdi_2023"]
df_hdi = df_hdi.drop(columns=["hdi_2023"])

# - Merging dfs -

df_full = df_trends.merge(df_ai, on="country", how="left")
df_full = df_full.merge(gdp_long[["country", "year", "gdp_pc_growth"]],on=["country", "year"],how="left")
df_full = df_full.merge(df_hdi[["country", "year", "hdi"]],on=["country", "year"],how="left")
df_full = df_full.merge(inv_long[["country", "year", "investment"]],on=["country", "year"],how="left")
df_full = df_full.merge(fdi_long[["country", "year", "fdi"]],on=["country", "year"],how="left")
df_full = df_full.merge(trade_long[["country", "year", "trade_openness"]],on=["country", "year"],how="left")
df_full = df_full.merge(inflation_long[["country", "year", "inflation"]],on=["country", "year"],how="left")

# Smpl Formatting

df_full["investment"] = pd.to_numeric(df_full["investment"], errors="coerce")
df_full["year"] = df_full["year"].astype(int)
df_full["gdp_pc_growth"] = pd.to_numeric(df_full["gdp_pc_growth"], errors="coerce")
df_full["hdi"] = pd.to_numeric(df_full["hdi"], errors="coerce")
df_full["fdi"] = pd.to_numeric(df_full["fdi"], errors="coerce")
df_full["trade_openness"] = pd.to_numeric(df_full["trade_openness"],errors="coerce")
df_full["inflation"] = pd.to_numeric(df_full["inflation"],errors="coerce")

# Dealing w missing errs

def force_gdp_2025_equals_2024(g):
    v2024 = g.loc[g["year"] == 2024, "gdp_pc_growth"]
    if not v2024.dropna().empty:
        g.loc[g["year"] == 2025, "gdp_pc_growth"] = v2024.dropna().iloc[0]
    return g

def fill_hdi_2024_2025_with_2023_if_missing(g):
    v2023 = g.loc[g["year"] == 2023, "hdi"]
    if not v2023.dropna().empty:
        base = v2023.dropna().iloc[0]
        mask = g["year"].isin([2024, 2025]) & g["hdi"].isna()
        g.loc[mask, "hdi"] = base
    return g

df_full = (df_full.groupby("country", group_keys=False).apply(force_gdp_2025_equals_2024).groupby("country", group_keys=False).apply(fill_hdi_2024_2025_with_2023_if_missing))

# - Making of regression ready variables -

# Ai trends standardization (z-score)
df_full["ai_trends_std"] = df_full.groupby("country")["artificial_intelligence"].transform(lambda x: (x - x.mean()) / x.std(ddof=0) if x.std(ddof=0) not in (0, np.nan) else np.nan)

# Interaction term AI trends * HDI
df_full["ai_x_hdi"] = df_full["ai_trends_std"] * df_full["hdi"]

# - Exporttting -

df_full = df_full.sort_values(["country", "year"]).reset_index(drop=True)
df_full.to_excel(output_path, index=False)

#--------------------------------------------------------------------------------------------------------------------

# Df DONEEE 
# Innentől kivettem a AI readiness indexet a regressionbol de a df ben benne van.

#--------------------------------------------------------------------------------------------------------------------

# Descriptive Stats

variables = [
    "gdp_pc_growth",
    "ai_trends_std",
    "hdi",
    "investment",
    "fdi",
    "trade_openness",
    "inflation"
]
df_desc = df_full[variables].dropna()
desc_stats = df_desc.describe().T
desc_stats["observations"] = len(df_desc)
desc_stats = desc_stats[["observations", "mean", "std", "min", "25%", "50%", "75%", "max"]]
correlation_matrix = df_desc.corr()
with pd.ExcelWriter("Outputs/descriptive_statistics.xlsx") as writer:
    desc_stats.to_excel(writer, sheet_name="Descriptive_Statistics")
    correlation_matrix.to_excel(writer, sheet_name="Correlation_Matrix")

#--------------------------------------------------------------------------------------------------------------------

# Correlation matrix heatmap niceerrr

variables = ["gdp_pc_growth","ai_trends_std","hdi","investment","fdi","trade_openness","inflation"]
corr = df_full[variables].dropna().corr()
fig, ax = plt.subplots(figsize=(9, 7))
im = ax.imshow(corr, vmin=-1, vmax=1, cmap="coolwarm")
ax.set_xticks(np.arange(len(variables)))
ax.set_yticks(np.arange(len(variables)))
ax.set_xticklabels(variables, rotation=45, ha="right")
ax.set_yticklabels(variables)
for i in range(len(variables)):
    for j in range(len(variables)):
        ax.text(j,i,f"{corr.iloc[i, j]:.2f}",ha="center",va="center",color="black")
plt.colorbar(im, ax=ax, label="Correlation coefficient")
plt.title("Correlation Matrix")
plt.tight_layout()
plt.savefig("Outputs/correlation_matrix_heatmap.png", dpi=300)
#plt.show()

# --------------------------------------------------------------------------------------------------------------------

df_base_model = df_full[["gdp_pc_growth", "ai_trends_std", "hdi","investment", "fdi", "trade_openness", "inflation","country", "year"]].dropna()
df_full_model = df_full[["gdp_pc_growth", "ai_trends_std", "hdi", "ai_x_hdi","investment", "fdi", "trade_openness", "inflation","country", "year"]].dropna()

# 1 Baseline regression

model_base = smf.ols(
    formula="""
    gdp_pc_growth ~ ai_trends_std + hdi
    + investment + fdi + trade_openness + inflation
    + C(country) + C(year)
    """,
    data=df_base_model).fit(cov_type="cluster",cov_kwds={"groups": df_full_model["country"]})

# 2. Full regression

model_full = smf.ols(
    formula="""
    gdp_pc_growth ~ ai_trends_std + hdi + ai_x_hdi
    + investment + fdi + trade_openness + inflation
    + C(country) + C(year)
    """,
    data=df_full_model).fit(cov_type="cluster",cov_kwds={"groups": df_full_model["country"]})

# --------------------------------------------------------------------------------------------------------------------

# Regression table

# RegressionTableHelpers

def stars(p):
    if pd.isna(p):
        return ""
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return ""

def fmt(x, digits=3):
    return "" if pd.isna(x) else f"{x:.{digits}f}"

def coef_with_stars(model, var):
    if var not in model.params.index:
        return ""
    coef = model.params[var]
    pval = model.pvalues[var]
    return f"{fmt(coef)}{stars(pval)}"

def se_in_parentheses(model, var):
    if var not in model.bse.index:
        return ""
    return f"({fmt(model.bse[var])})"

# Making the Table

variables_order = [("ai_trends_std", "AI trends"),("hdi", "HDI"),("ai_x_hdi", "AI trends × HDI"),("investment", "Investment"),("fdi", "FDI"),("trade_openness", "Trade openness"),("inflation", "Inflation")]
models = {"(1) Baseline Model": model_base,"(2) Extended Model": model_full}
rows = []
for var, label in variables_order:
    coef_row = {"Variable": label}
    se_row = {"Variable": ""}
    for model_name, model in models.items():
        coef_row[model_name] = coef_with_stars(model, var)
        se_row[model_name] = se_in_parentheses(model, var)   
    rows.append(coef_row)
    rows.append(se_row)

rows.append({"Variable": "Country FE", **{name: "Yes" for name in models.keys()}})
rows.append({"Variable": "Year FE", **{name: "Yes" for name in models.keys()}})
rows.append({"Variable": "Observations", **{name: int(model.nobs) for name, model in models.items()}})
rows.append({"Variable": "R-squared", **{name: fmt(model.rsquared) for name, model in models.items()}})
reg_table_thesis = pd.DataFrame(rows)

note = pd.DataFrame([{"Variable": "Notes: Standard errors in parentheses. Country and year fixed effects included. Standard errors clustered at the country level. * p<0.10, ** p<0.05, *** p<0.01."}])
reg_table = pd.concat([reg_table_thesis, note], ignore_index=True)
reg_table.to_excel("Outputs/regression_table.xlsx", index=False)

# --------------------------------------------------------------------------------------------------------------------

# Robustness Checks
# This tests the full model.

# --------------------------------------------------------------------------------------------------------------------

# Robustness1: Lagged AI trends

df_full = df_full.sort_values(["country", "year"])
df_full["ai_trends_lag1"] = df_full.groupby("country")["ai_trends_std"].shift(1)
df_full["ai_lag1_x_hdi"] = df_full["ai_trends_lag1"] * df_full["hdi"]
robust_lag = smf.ols(
    formula="""
    gdp_pc_growth ~ ai_trends_lag1 + hdi + ai_lag1_x_hdi
    + investment + fdi + trade_openness + inflation
    + C(country) + C(year)
    """,
    data=df_full
).fit(cov_type="HC1")
#print(robust_lag.summary())

# --------------------------------------------------------------------------------------------------------------------

# Robustness2: Excluding 2025

df_no2025 = df_full[df_full["year"] < 2025]

robust_no2025 = smf.ols(
    formula="""
    gdp_pc_growth ~ ai_trends_std + hdi + ai_x_hdi
    + investment + fdi + trade_openness + inflation
    + C(country) + C(year)
    """,
    data=df_no2025
).fit(cov_type="HC1")
#print(robust_no2025.summary())

# --------------------------------------------------------------------------------------------------------------------

# Robustness3: Excluding GDP growth outliers

lower = df_full["gdp_pc_growth"].quantile(0.01)
upper = df_full["gdp_pc_growth"].quantile(0.99)

df_no_outliers = df_full[(df_full["gdp_pc_growth"] >= lower)& (df_full["gdp_pc_growth"] <= upper)]
robust_no_outliers = smf.ols(
    formula="""
    gdp_pc_growth ~ ai_trends_std + hdi + ai_x_hdi
    + investment + fdi + trade_openness + inflation
    + C(country) + C(year)
    """,
    data=df_no_outliers
).fit(cov_type="HC1")
#print(robust_no_outliers.summary())

# --------------------------------------------------------------------------------------------------------------------

# Robustness4: Cluster -> HCI

# Robustness: Same main modellll with HC1 robust SEs

model_full_hc1 = smf.ols("""gdp_pc_growth ~ ai_trends_std + hdi + ai_x_hdi+ investment + fdi + trade_openness + inflation+ C(country) + C(year)""",data=df_full_model).fit(cov_type="HC1")

# --------------------------------------------------------------------------------------------------------------------

# Robustness5: using AI readiness instead of HDI

df_full["ai_x_readiness"] = (df_full["ai_trends_std"]* df_full["ai_readiness_2023"])
df_readiness_model = df_full[["gdp_pc_growth","ai_trends_std","ai_readiness_2023","ai_x_readiness","investment","fdi","trade_openness","inflation","country","year"]].dropna()

model_readiness = smf.ols(
    formula="""
    gdp_pc_growth
    ~ ai_trends_std
    + ai_readiness_2023
    + ai_x_readiness
    + investment
    + fdi
    + trade_openness
    + inflation
    + C(country)
    + C(year)
    """,
    data=df_readiness_model).fit(cov_type="cluster",cov_kwds={"groups": df_readiness_model["country"]})

# --------------------------------------------------------------------------------------------------------------------

# To excel

with pd.ExcelWriter("Outputs/robustness_checks.xlsx") as writer:
    pd.DataFrame({"Coefficient": robust_lag.params,"Std.Error": robust_lag.bse,"P-value": robust_lag.pvalues}).to_excel(writer, sheet_name="Lagged_AI")
    pd.DataFrame({"Coefficient": robust_no2025.params,"Std.Error": robust_no2025.bse,"P-value": robust_no2025.pvalues}).to_excel(writer, sheet_name="No_2025")
    pd.DataFrame({"Coefficient": robust_no_outliers.params,"Std.Error": robust_no_outliers.bse,"P-value": robust_no_outliers.pvalues}).to_excel(writer, sheet_name="No_Outliers")
    pd.DataFrame({"Coefficient": model_full_hc1.params,"Std.Error": model_full_hc1.bse,"P-value": model_full_hc1.pvalues}).to_excel(writer, sheet_name="HC1_SE")
    pd.DataFrame({"Coefficient": model_readiness.params,"Std.Error": model_readiness.bse,"P-value": model_readiness.pvalues}).to_excel(writer, sheet_name="AIReadiness")

# --------------------------------------------------------------------------------------------------------------------

# Illustrations
# Plus dolgok amiket hozzaadok a paperhez

# --------------------------------------------------------------------------------------------------------------------

# Marginal effects of AI adoption across HDI levels w ci ff

beta_ai = model_full.params["ai_trends_std"]
beta_inter = model_full.params["ai_x_hdi"]
cov = model_full.cov_params()
var_ai = cov.loc["ai_trends_std", "ai_trends_std"]
var_inter = cov.loc["ai_x_hdi", "ai_x_hdi"]
cov_ai_inter = cov.loc["ai_trends_std", "ai_x_hdi"]
hdi_vals = np.linspace(df_full_model["hdi"].min(), df_full_model["hdi"].max(), 100)
marginal_effect = beta_ai + beta_inter * hdi_vals
se_marginal = np.sqrt(var_ai+ (hdi_vals ** 2) * var_inter+ 2 * hdi_vals * cov_ai_inter)
ci_upper = marginal_effect + 1.96 * se_marginal
ci_lower = marginal_effect - 1.96 * se_marginal
plt.figure(figsize=(8, 5))
plt.plot(hdi_vals, marginal_effect, label="Marginal effect")
plt.fill_between(hdi_vals, ci_lower, ci_upper, alpha=0.2, label="95% CI")
plt.axhline(0, linestyle="--")
plt.xlabel("Human Development Index (HDI)")
plt.ylabel("Marginal effect of AI trends on GDP per capita growth")
plt.title("Marginal Effect of AI Trends Across HDI Levels")
plt.legend()
plt.tight_layout()
plt.savefig("Outputs/f_marginal_effects_ci.png", dpi=300)
#plt.show()

# --------------------------------------------------------------------------------------------------------------------

# Table: Marginal effects at low, mean, and high HDI tt

hdi_levels = {"Low HDI (25th percentile)": df_full["hdi"].quantile(0.25),"Mean HDI": df_full["hdi"].mean(),"High HDI (75th percentile)": df_full["hdi"].quantile(0.75)}
marginal_effects = []
for label, hdi_value in hdi_levels.items():
    effect = beta_ai + beta_inter * hdi_value
    marginal_effects.append({"HDI level": label,"HDI value": round(hdi_value, 3),"Marginal effect of AI trends": round(effect, 3)})

marginal_effects_table = pd.DataFrame(marginal_effects)
marginal_effects_table.to_excel("Outputs/t_marginal_effects.xlsx", index=False)

# --------------------------------------------------------------------------------------------------------------------

# Predicted GDP growth across AI trends by HDI level ff

ai_vals = np.linspace(df_full["ai_trends_std"].quantile(0.05),df_full["ai_trends_std"].quantile(0.95),100)
hdi_low = df_full["hdi"].quantile(0.25)
hdi_mean = df_full["hdi"].mean()
hdi_high = df_full["hdi"].quantile(0.75)
investment_mean = df_full["investment"].mean()
fdi_mean = df_full["fdi"].mean()
trade_mean = df_full["trade_openness"].mean()
inflation_mean = df_full["inflation"].mean()
beta_0 = model_full.params["Intercept"]
beta_ai = model_full.params["ai_trends_std"]
beta_hdi = model_full.params["hdi"]
beta_inter = model_full.params["ai_x_hdi"]
beta_inv = model_full.params["investment"]
beta_fdi = model_full.params["fdi"]
beta_trade = model_full.params["trade_openness"]
beta_inflation = model_full.params["inflation"]

def predicted_growth(ai, hdi):
    return (beta_0+ beta_ai * ai+ beta_hdi * hdi+ beta_inter * ai * hdi+ beta_inv * investment_mean+ beta_fdi * fdi_mean+ beta_trade * trade_mean+ beta_inflation * inflation_mean)

plt.figure(figsize=(8, 5))
plt.plot(ai_vals, predicted_growth(ai_vals, hdi_low), label="Low HDI")
plt.plot(ai_vals, predicted_growth(ai_vals, hdi_mean), label="Mean HDI")
plt.plot(ai_vals, predicted_growth(ai_vals, hdi_high), label="High HDI")
plt.axhline(0, linestyle="--")
plt.xlabel("AI trends standardised")
plt.ylabel("Predicted GDP per capita growth")
plt.title("Predicted GDP Growth Across AI Trends by HDI Level")
plt.legend()
plt.tight_layout()
plt.savefig("Outputs/f_predicted_growth.png", dpi=300)
#plt.show()

# --------------------------------------------------------------------------------------------------------------------

# Robustness of AI * HDI interaction coefficient across specs

robust_models = {"Main model": model_full,"HC1 SE": model_full_hc1,"No 2025": robust_no2025,"No outliers": robust_no_outliers,"Lagged AI": robust_lag, "AIPI Interaction-term":model_readiness}
coef_names = {"Main model": "ai_x_hdi","HC1 SE": "ai_x_hdi","No 2025": "ai_x_hdi","No outliers": "ai_x_hdi","Lagged AI": "ai_lag1_x_hdi","AIPI Interaction-term":"ai_x_readiness"}
coef_values = []
se_values = []
labels = []
for label, model in robust_models.items():
    coef_name = coef_names[label]
    if coef_name in model.params.index:
        labels.append(label)
        coef_values.append(model.params[coef_name])
        se_values.append(model.bse[coef_name])
ci_95 = [1.96 * se for se in se_values]
plt.figure(figsize=(8, 5))
plt.errorbar(labels,coef_values,yerr=ci_95,fmt="o",capsize=6)
plt.axhline(0, linestyle="--")
plt.ylabel("Interaction Coefficient")
plt.title("Robustness of AI Interaction Across Specifications")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig("Outputs/f_robustness_interaction_coefficients.png", dpi=300)
# plt.show()

# --------------------------------------------------------------------------------------------------------------------

print("Thanks for running my code...KÖSZIKE")

# --------------------------------------------------------------------------------------------------------------------