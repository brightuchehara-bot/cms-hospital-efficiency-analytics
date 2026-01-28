# Entity Relationship Diagram (ERD)

## Join Key
**Facility ID** is the primary key across datasets.

## Tables (Logical Model)

### dim_hospital (from Hospital_General_Information.csv)
- Facility ID (PK)
- Facility Name
- Address, City/Town, State, ZIP Code, County/Parish
- Hospital Type, Ownership, Emergency Services
- Hospital overall rating
- (plus other descriptive fields)

### fact_mspb (from Medicare_Hospital_Spending_Per_Patient-Hospital.csv)
- Facility ID (FK)
- Measure ID, Measure Name
- Score
- Start Date, End Date

### fact_readmissions (from FY_2025_Hospital_Readmissions_Reduction_Program_Hospital.csv)
- Facility ID (FK)
- Measure Name
- Excess Readmission Ratio
- Predicted/Expected Readmission Rate
- Number of Discharges, Number of Readmissions
- Start Date, End Date

### fact_complications_deaths (from Complications_and_Deaths-Hospital.csv)
- Facility ID (FK)
- Measure ID, Measure Name
- Compared to National
- Denominator, Score, Lower/Higher Estimate
- Start Date, End Date
