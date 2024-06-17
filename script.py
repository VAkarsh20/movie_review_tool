# Not Good Code! Including for people who want some ideas.

import wikipedia
import pandas as pd
import numpy as np
import review_tool
import os
from protos import movie_pb2
from google.protobuf import text_format
import sys
from collections import defaultdict
import tools.sheets as sheets
import subprocess
import yaml
import tools.rotten_tomatoes as rotten_tomatoes
import tools.letterboxd as letterboxd
import tools.imdb as imdb
import threading
import re
from tqdm import tqdm
import multiprocessing as mp
from utils.proto_utils import *
from utils.print_utils import *
from google.protobuf.json_format import MessageToJson

def create_df():

    # Creating dataframe
    df = pd.read_csv("movies.csv").fillna("")

    for i in range(len(df)):
        if df.loc[i, 'imdbID'] == "":
            df.loc[i, 'imdbID'] = get_imdb_id(df.loc[i, 'Title'])

    df['Stars'] = df['Rating'].map(lambda x: rating_to_stars(x))

    return df

# Fix issue with protos not having rating and reviews
def add_rating_and_review_date(df):

    start = 167
    end = len(df)

    for i in range(start, end):

        record = df.iloc[i]
        title = record['Title']

        wiki_title = title.replace(" ", "_")
        infobox = review_tool.parse_wiki("https://en.wikipedia.org/wiki/" + wiki_title)

        if title.endswith("film)"):
            title = title[:title.rfind(' (')]

        release_year = review_tool.find_release_year(infobox)    
        filename = ("movies_textproto/" + title + " ({})".format(release_year) + ".textproto").replace(":","")

        with open(filename, "r") as fd:
            text_proto = fd.read()

        proto = text_format.Parse(text_proto, movie_pb2.Movie())

        proto.rating = record['Rating']
        proto.review_date = record['Date']

        review_tool.write_proto(proto)


def create_protos_free_from_csv(df):

    free_df = df[:166]
    for i in range(len(free_df)):

        try: 

            record = free_df.iloc[i]
            title = record['Title']

            wiki_title = title.replace(" ", "_")
            infobox = review_tool.parse_wiki("https://en.wikipedia.org/wiki/" + wiki_title)

            if title.endswith("film)"):
                title = title[:title.rfind(' (')]

            proto = movie_pb2.MovieFree(
                title = title, 
                rating = record['Rating'], 
                review = record['Review'], 
                release_year = review_tool.find_release_year(infobox),
                review_date = record['Date'], 
                redux = False
            )


            filename = ("movies_textproto/" + proto.title + " ({})".format(proto.release_year) + ".textproto").replace(":","")

            if not os.path.exists(filename): 
                review_tool.write_proto(proto)
        except:
            print("Issue with {}".format(i))
            continue

def fill_in_acting(comments):

    def fill_in_acting_comments(actors_dict, comment):
        if "from the rest of the cast" in comment:
            cast = movie_pb2.Movie.Review.GenericCategory(rating = "TODO", comments=comment)
            proto.review.acting.cast = cast
            return True
        else:
            name = comment.partition("from ")[-1]
            actor_comment_idx = comments.find("(")

            if actor_comment_idx != -1:
                name = name.partition(" (")[0]

            i = actors_dict[name]
            if i != -1:
                proto.review.acting.actor[i].comments = comment
                return True
            else:
                return False

    start = comments.find("(")
    if start == -1:
        proto.review.acting.comments = comments.strip()
        return
    else:
        proto.review.acting.comments = comments[:start].strip()

    if comments[-1] != ")":
        raise Exception("Acting should end with a closing parenthesis")

    start += 1
    current = start

    actors_dict = defaultdict(lambda: -1)

    for i in range(len(proto.review.acting.actor)):
        actor = proto.review.acting.actor[i]
        actors_dict[actor.name] = i

    stack = []
    while current < len(comments) - 1:

        if comments[current] == "(":
            stack.append("(")
        elif comments[current] == ")":
            stack.pop()
        if comments[current] == "," and len(stack) == 0:
            comment = comments[start:current].strip()
            # Fix this
            if not fill_in_acting_comments(actors_dict, comment):
                res.append(comment + "\n")
            start = current + 1
        current += 1

    last_comment = comments[start:-1].strip()
    if not fill_in_acting_comments(actors_dict, last_comment):
        res.append(last_comment + "\n")


def change_date_format(date):
    month, day, year = date.split("/")
    return "{}-{}-{}".format(year, month, day)

def update_csv():

    title = ""
    df = pd.DataFrame(columns=["imdbID", "Title", "Year", "Rating","WatchedDate","Tags","Review","Id"])
    files = os.listdir("movies_textproto/")

    for i in range(len(files)):

        try: 
            filename = files[i].replace(".textproto","")

            if filename == "reduxed":
                continue

            proto = review_tool.read_proto(filename)
            record = [proto.imdb_id, proto.title, proto.release_year, rating_to_stars(proto.rating), change_date_format(proto.review_date), rating_to_tag(proto.rating), review_tool.print_short_review(proto, filename), proto.id]
            df.loc[len(df)] = record
            # sheets.post_to_sheets(proto.title, proto.rating, review_tool.print_review(proto, filename), proto.release_year, proto.review_date, proto.id, proto.imdb_id)

        except:
            raise Exception("Issue with {} {}".format(title, i))
            continue

    df = df.sort_values(by=['Id'])
    df = df.drop(columns=['Id'])

    df.to_csv("letterboxd_upload.csv", index=False)

# TODO: Create FILM TO REDUX
# https://www.imdb.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.imdb.com%2Fregistration%2Fap-signin-handler%2Fimdb_us&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=imdb_us&openid.mode=checkid_setup&siteState=eyJvcGVuaWQuYXNzb2NfaGFuZGxlIjoiaW1kYl91cyIsInJlZGlyZWN0VG8iOiJodHRwczovL3d3dy5pbWRiLmNvbS8_cmVmXz1sb2dpbiJ9&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&tag=imdbtag_reg-20
def parse(filename):

    # proto = review_tool.read_proto(filename)

    path = "movies_textproto/"
    count = 0
    while os.path.exists(path + ("reduxed/" * count) + filename):
        count += 1

    if not os.path.exists(path + ("reduxed/" * count)):
        os.mkdir(path + ("reduxed/" * count))

    while count > 0:
        os.rename(path + ("reduxed/" * (count - 1)) + filename, path + ("reduxed/" * (count)) + filename)
        count -= 1

def export_imdb(files):

    bot = imdb.IMDbBot()
    bot.login()
    print()

    for filename in files:

        try:
            proto = review_tool.read_proto(filename)
            review = review_tool.print_imdb_review(proto, filename)
            bot.import_review(proto.imdb_id, proto.rating, review)

            if proto.rating >= 9.5:        
                bot.add_to_cinema_personified_list(proto.imdb_id, proto.title, proto.release_year)
        except:
            raise Exception("Issue with {}".format(filename))
            continue



def bulk_export_imdb():
    # df = pd.read_csv("movies.csv")[329:]
    # files = ["{} ({})".format(df["Title"].iloc[i].replace(":","").replace("/", " "), df["Release Year"].iloc[i]) for i in range(len(df))]
    files = filter_values()

    # creating thread
    t1 = threading.Thread(target=export_imdb, args=(files[0:6],))
    t2 = threading.Thread(target=export_imdb, args=(files[6:12],))
    t3 = threading.Thread(target=export_imdb, args=(files[12:18],))
    t4 = threading.Thread(target=export_imdb, args=(files[18:],))

    # starting thread 1
    t1.start()
    # starting thread 2
    t2.start()
    # starting thread 3
    t3.start()
    # starting thread 4
    t4.start()

    # wait until thread 1 is completely executed
    t1.join()
    # wait until thread 2 is completely executed
    t2.join()
    # wait until thread 3 is completely executed
    t3.join()
    # wait until thread 4 is completely executed
    t4.join()


def filter_values():
    df = pd.read_csv("movies.csv")[0:167]

    files = []
    for i in range(len(df)):
        record = df.iloc[i]
        if isinstance(record["Review"], str) and len(record["Review"]) >= 600:
            files.append("{} ({})".format(record["Title"].replace(":","").replace("/", " "), record["Release Year"]))
    return files

def list_of_reviews_changed():
    df = pd.read_csv("movies.csv")
    df = df.loc[(df["Rating"] > 1.2) & (df["Rating"] < 9.0)][['Title', 'Rating', 'Release Year', 'Id']].sort_values(by=['Rating'])
    df.to_csv('movies_temp.csv', index=False) 


def change_rating(filename):
    try:
        proto = review_tool.read_proto(filename)
        proto.rating = reduced_rating(proto.rating)
        review_tool.write_proto(proto)
    except:
        print("Issue with {}".format(filename))


def change_review_ratings():
    # df = pd.read_csv("movies_temp.csv")
    # for i in range(len(df)):
    #     record = df.iloc[i]

    #     filename = "{} ({})".format(record["Title"], int(record['Release Year']))
    #     change_rating(filename)

    f = open("issues.txt", "r")
    filenames = f.read().splitlines()
    for filename in filenames:
        change_rating(filename)


def reduced_rating(val):
    if val >= 1.5 and val <= 2.0:
        return round(val - 0.2,1)
    elif val >= 2.5 and val <= 3.9:
        return round(val - 0.6,1)
    elif val >= 4.0 and val <= 4.9:
        return round(val - 0.5,1)
    elif val >= 5.0 and val <= 6.4:
        return round(val - 0.4,1)
    elif val >= 6.5 and val <= 7.6:
        return round(val - 0.3,1)
    elif val >= 7.7 and val <= 8.4:
        return round(val - 0.2,1)
    elif val >= 8.5 and val <= 8.9:
        return round(val - 0.1,1)
    else:
        return val


def create_letterboxd_csv():

    temp_df = pd.read_csv("movies_temp.csv")
    df = pd.DataFrame(columns=["imdbID", "Title", "Year", "Rating","WatchedDate","Tags","Review"])
    for i in range(len(temp_df)):
        temp_record = temp_df.iloc[i]

        filename = "{} ({})".format(temp_record["Title"], int(temp_record['Release Year']))
        try:
            proto = review_tool.read_proto(filename)
            short_review = review_tool.print_short_review(proto, filename)
        
            record = [proto.imdb_id, proto.title, proto.release_year, letterboxd.rating_to_stars(proto.rating), letterboxd.change_date_format(proto.review_date), letterboxd.rating_to_tag(proto.rating), short_review]
            df.loc[i+1] = record
        except:
            print("Issue with {}".format(filename))
            continue
    

    df.to_csv("letterboxd_upload.csv", index=False)

def export_sheets(files):

    bot = imdb.IMDbBot()
    bot.login()
    print()

    for filename in files:

        try:
            proto = review_tool.read_proto(filename)
            review = review_tool.print_imdb_review(proto, filename)
            bot.import_review(proto.imdb_id, proto.rating, review)

            if proto.rating >= 9.5:        
                bot.add_to_cinema_personified_list(proto.imdb_id, proto.title, proto.release_year)
        except:
            raise Exception("Issue with {}".format(filename))
            continue

def bulk_export_sheets():

    # Accessing API
    client = sheets.access_api()

    # Accessing Sheet
    sheet = client.open("Movies").sheet1

    # Post review to local csv file
    df = pd.read_csv("movies.csv")
    temp_df = pd.read_csv("movies_temp.csv")
    for i in tqdm(range(len(temp_df)-30, len(temp_df))):
        record = temp_df.iloc[i]

        filename = "{} ({})".format(record["Title"], int(record['Release Year'])).replace(":","").replace("/", " ")
        
        try:
            proto = review_tool.read_proto(filename)
        except:
            print("Issue with {}".format(filename))
            continue

        # Sees if review already exists, else append
        if not df[df['Id'] == proto.id].empty:
            df.at[int(proto.id) - 1, 'Rating'] = proto.rating
        else:
            print("Issue with {}".format(proto.title))

        # Check to see if review already exists, if it does not create a new entry, else replace it
        cell = sheet.find(proto.imdb_id)
        if cell is not None:
            sheet.update_cell(cell.row, 2, proto.rating)
        else:
            print("Cannot post review")
    
    df.to_csv('movies.csv', index=False) 


def set_id(imdb_id, redux):
    movie_id = 0
    if redux:
        df = pd.read_csv("movies.csv")
        movie_id = int(df[df["imdbID"] == imdb_id]["Id"])
    else:
        movie_id = len(os.listdir('movies_textproto/'))
    return movie_id



if __name__=="__main__":

    argc = len(sys.argv)

    filename = "Inside Out (2015)"
    proto = read_proto(filename=filename)

    print(print_imdb_review(proto, filename))