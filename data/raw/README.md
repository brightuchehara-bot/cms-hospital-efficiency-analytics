# Raw Data Sources (CMS Provider Data)

These CSVs are downloaded from CMS Provider Data (data.cms.gov) and placed 
locally in `data/raw/`.
Raw CSVs are excluded from GitHub via `.gitignore` to keep the repo 
lightweight and reproducible.

## Files
- `Hospital_General_Information.csv`
- `Medicare_Hospital_Spending_Per_Patient-Hospital.csv`
- `FY_2025_Hospital_Readmissions_Reduction_Program_Hospital.csv`
- `Complications_and_Deaths-Hospital.csv`

## Citations / References
- CMS Provider Data: Hospitals topic (dataset catalog).  
- Medicare Spending Per Beneficiary (MSPB) methodology (measure definition 
+ episode window).  
- HRRP program documentation for how readmissions performance is 
evaluated.

> Notes:
> - MSPB episode includes payments for services 3 days prior through 30 
days after an inpatient stay (risk-adjusted / standardized).  
> - HRRP uses excess readmission ratios / penalties for certain 
conditions.

