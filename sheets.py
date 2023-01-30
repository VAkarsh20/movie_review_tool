import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

def access_api():
    
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    return gspread.authorize(creds)


def post_to_sheets(title, rating, review):

    # Accessing API
    client = access_api()

    # Accesing Sheet
    sheet = client.open("Movies").sheet1

    # Finding number of rows
    data = sheet.get_all_records()
    rows = len(data)

    # Check to see if review already exists, if it does not create a new entry, else replace it
    cell = sheet.find(title)
    if cell is None:
        record = [title, rating, review, rows + 1]
        sheet.insert_row(record, rows + 2)
    else:
        sheet.update_cell(cell.row, 2, rating)
        sheet.update_cell(cell.row, 3, review)

def reviews_sorted():
    
    # Accessing API
    client = access_api()

    # Accesing Sheet
    sheet = client.open("Movies").sheet1

    # Getting all the Titles and Ratings
    df = pd.DataFrame(sheet.get_all_records())[["Title", "Rating"]]

    # Sortings in descending order and returning as a string
    df = df.sort_values(by=['Rating'], ascending=False)
    return df.to_string(index=False)