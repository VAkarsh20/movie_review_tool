from datetime import datetime

# Get today's date for the review date
def get_review_date():
    today = datetime.now()
    return "{}/{}/{}".format(today.strftime('%m'), today.strftime('%d'), today.strftime('%Y')) 

def change_date_format(date):
    month, day, year = date.split("/")
    return "{}-{}-{}".format(year, month, day)