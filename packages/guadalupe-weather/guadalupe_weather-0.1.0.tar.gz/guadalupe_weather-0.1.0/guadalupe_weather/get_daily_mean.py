def get_daily_mean(data, variable):
    return data.groupby(["Date"])[variable].mean()
