semester_currency_variation = {
    "2016-07": 0.3058,
    "2017-01": 0.3144,
    "2017-07": 0.3121,
    "2018-01": 0.2918,
    "2018-07": 0.2577,
}


def month_to_semester(month):
    year = month[:4]
    if int(month[5:7]) <= 6:
        return f"{year}-01"
    return f"{year}-07"
