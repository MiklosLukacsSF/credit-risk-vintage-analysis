# Credit Risk Vintage Analysis

A script to create prepayment curves (CPR) for separate cohorts based on their origination dates. Each cohort represent 
all loans originated in the same months or in the same quarter.

## Input data
- prepayments.csv: each row represents one loan's prepayment amount for every period. The columns represent payment
  dates (months). First column is the loan id.
- balances.csv: similarly to prepayments, each row represents one loan's period start balance minus the scheduled 
  principal. First column is the loan id.
- account_info.csv contains high level info about the loans (balance, origination date, buy-to-let or owner occupied 
  type, etc.). First column is the loan id.  
  
### Data Generation 

Since I can't share real people's payment information, I created a script (generate_data.py) that generates RANDOM 
loan tape, balance and prepayment information. Therefore, you can easily test the calculation on random data. 

The script requires a few input assumptions (e.g. avg loan size, terms range, number of loans, etc.).

## Calculate Vintage CPR Curves

- read input data
- create seasoned table based on origination date. In the new table the columns are not actual dates but how many months
  happened since the origination. Therefore, each loan's prepayment, balance info will start from the same column (1st 
  months).
- divide prepayment by balance for each period and each cohort
