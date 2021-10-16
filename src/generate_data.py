from datetime import datetime

import numpy as np
import pandas as pd
import numpy_financial as npf


# Input Assumptions
n_loans = 10000
avg_balance = 350000
st_deviation = 50000
origination_range = (datetime(2016, 1, 1), datetime(2017, 6, 1))
coupons = np.random.uniform(low=0.005, high=0.1, size=(n_loans,))
terms = np.random.randint(low=12, high=60, size=(n_loans,))
loan_type = np.random.choice(a=['buy to let', 'owner occupied'], size=n_loans, p=[0.3, 0.7])


balances = np.random.normal(loc=avg_balance, scale=st_deviation, size=n_loans)
day_range = (origination_range[1] - origination_range[0]).days + 1
origination_dates = pd.to_timedelta(np.random.rand(n_loans) * day_range, unit='D') + origination_range[0]


def calculate_amortisation(coupon, term, orig_bal, orig_date):
    """ generate cash flow for one loan based on no default but random prepayment assumptions

    Args:
        coupon (float): only works for fix coupon loans
        term (int): number of months
        orig_bal (float): loan's nominal value
        orig_date (datetime.datetime): origination date

    Returns:
        cf_df (pd.DataFrame): loan cash flow table
    """

    cpr_vector = np.random.uniform(low=0.005, high=0.1, size=(term,))
    smm_vector = [1-(1-cpr)**(1/12) for cpr in cpr_vector]
    adj_term = term + 1 if orig_date.day == 1 else term
    dates = pd.date_range(pd.to_datetime(orig_date).date(), periods=adj_term, freq='MS', closed='right')

    period = 1
    end_bal = orig_bal
    result = []

    while round(end_bal, 0) > 0:
        beg_bal = end_bal
        pmt_i = npf.pmt(rate=coupon/12, nper=term - period + 1, pv=-beg_bal)
        interest = beg_bal * coupon / 12
        scheduled_prin = pmt_i - interest
        prepayment = max(0, (min(beg_bal - scheduled_prin, smm_vector[period - 1] * (beg_bal - scheduled_prin))))
        end_bal = beg_bal - scheduled_prin - prepayment

        result.append({
            'period': period,
            'beg_bal': beg_bal,
            'sched_prin': scheduled_prin,
            'int': interest,
            'prepay': prepayment,
            'end_bal': end_bal
        })
        period += 1

    cf_df = pd.DataFrame(result, index=dates)
    return cf_df


prepays_df_list = []
balances_df_list = []
for i in range(n_loans):
    df = calculate_amortisation(coupon=coupons[i], term=terms[i], orig_bal=balances[i], orig_date=origination_dates[i])

    tmp_prepay = df['prepay']
    tmp_bal = df['beg_bal'] - df['sched_prin']

    # loan id is simple integers
    tmp_prepay.name = i
    tmp_bal.name = i

    prepays_df_list.append(tmp_prepay)
    balances_df_list.append(tmp_bal)


prepay_df = pd.concat(prepays_df_list, axis=1).T
balances_df_list = pd.concat(balances_df_list, axis=1).T
account_info = pd.DataFrame({
    'coupon': coupons,
    'term': terms,
    'origination': origination_dates,
    'balance': balances,
    'loan_type': loan_type
}, index=range(n_loans))

account_info.origination = pd.to_datetime(account_info.origination)

prepay_df.to_csv('../input_data/prepayments.csv')
balances_df_list.to_csv('../input_data/balances.csv')
account_info.to_csv('../input_data/account_info.csv')
