import pandas as pd
import matplotlib.pyplot as plt


prepayment_df = pd.read_csv('../input_data/prepayments.csv', index_col=0).T
balances_df = pd.read_csv('../input_data/balances.csv', index_col=0).T
account_info_df = pd.read_csv('../input_data/account_info.csv', index_col=0)
account_info_df.origination = pd.to_datetime(account_info_df.origination).dt.date
prepayment_df.index = pd.to_datetime(prepayment_df.index).date
balances_df.index = pd.to_datetime(balances_df.index).date


def create_seasoned_df(input_df, cumulative=False):
    """ iterates through all loans and drops dates before their origination --> merged them back into one table """

    aggregated_data = []
    for loan_id in input_df:
        one_loan = input_df[loan_id]
        if cumulative is True:
            one_loan = one_loan.cumsum()
        origination_date = account_info_df.loc[loan_id, 'origination']
        tmp = one_loan[one_loan.index > origination_date]
        tmp.index = range(1, len(tmp)+1)
        tmp.name = loan_id
        aggregated_data.append(tmp)

    seasoned_df = pd.concat(aggregated_data, axis=1)
    return seasoned_df.T


seasoned_prepay = create_seasoned_df(input_df=prepayment_df, cumulative=True)
seasoned_balance = create_seasoned_df(input_df=balances_df, cumulative=False)


def create_vintage_aggregation(seasoned_df, account_df):
    """ group by origination date either monthly (MS) or quarterly (QS) period"""

    seasoned_df = seasoned_df.merge(account_df[['origination']], right_index=True, left_index=True, how='left')
    seasoned_df.set_index('origination', inplace=True)
    seasoned_df.index = pd.to_datetime(seasoned_df.index)
    vintage_df = seasoned_df.groupby(pd.Grouper(freq='MS')).agg('sum')
    return vintage_df


vintage_prepay = create_vintage_aggregation(seasoned_df=seasoned_prepay, account_df=account_info_df)
vintage_balance = create_vintage_aggregation(seasoned_df=seasoned_balance, account_df=account_info_df)
vintage_prepay_curves = vintage_prepay.div(vintage_balance)

# plot curves
fig, ax = plt.subplots()
for vintage_date, vintage_curve in vintage_prepay_curves.iterrows():
    ax.plot(vintage_curve[:40], label=vintage_date)

ax.legend(loc='upper left')
plt.show()
