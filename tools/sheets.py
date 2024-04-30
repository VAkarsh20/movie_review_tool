import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from csv import writer
import subprocess

# sudo hwclock -s
def initialize_to_sheets(proto):

    # Accessing API
    client = access_api()

    # Accessing Sheet
    sheet = client.open("Movies").sheet1
    
    # Finding number of rows
    data = sheet.get_all_records()
    rows = len(data)

    # Check to see if review already exists, if it does not create a new entry, else replace it
    cell = sheet.find(proto.imdb_id)
    if cell is None:
        record = [proto.title, "", "", proto.release_year, "", proto.id, proto.imdb_id]
        sheet.insert_row(record, rows + 2)
    else:
        print("Review is already initialized in row {}".format(cell.row))

def post_to_sheets(proto, review):

    # Accessing API
    client = access_api()

    # Accessing Sheet
    sheet = client.open("Movies").sheet1

    # Post review to local csv file
    post_to_csv(proto, review)

    # Check to see if review already exists, if it does not create a new entry, else replace it
    cell = sheet.find(proto.imdb_id)
    if cell is not None:
        sheet.update_cell(cell.row, 2, proto.rating)
        sheet.update_cell(cell.row, 3, review)
        sheet.update_cell(cell.row, 5, proto.review_date)
    else:
        print("Cannot post review")

def reviews_sorted():

    # Getting all the Titles and Ratings
    df = pd.read_csv("movies.csv")[["Title", "Rating"]]

    # Sorts in descending order and returning as a string
    df = df.sort_values(by=['Rating'], ascending=False)
    return df.to_string(index=False)

# Helper Functions
def access_api():
    
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    return gspread.authorize(creds)

def post_to_csv(proto, review):

    df = pd.read_csv("movies.csv")
    # TODO: See if the match should be ID or IMDB ID
    # Sees if review already exists, else append
    if not df[df['Id'] == proto.id].empty:
        df.at[int(proto.id) - 1, 'Rating'] = proto.rating
        df.at[int(proto.id) - 1, 'Review'] = review
        df.at[int(proto.id) - 1, 'Review Date'] = proto.review_date
    else:
        record = [proto.title, proto.rating, review, proto.release_year, proto.review_date, proto.id, proto.imdb_id]
        df.loc[len(df)] = record
    
    df.to_csv('movies.csv', index=False)