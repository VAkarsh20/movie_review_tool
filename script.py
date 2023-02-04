# Not Good Code! Including for people who want some ideas.

import wikipedia
import pandas as pd
import numpy as np
import review_tool
import os
import movie_pb2
from google.protobuf import text_format

def get_imdb_id(film):

    links = wikipedia.WikipediaPage(title=film).references
    imdb_id = [x.replace("https://www.imdb.com/title/","").partition("/")[0] for x in links if("https://www.imdb.com/title/" in x)]

    if len(imdb_id) > 1 and len(set(imdb_id)) > 1:
        raise Exception("More than one IMDB link for " + film)

    imdb_id = imdb_id[0]
    return imdb_id

def rating_to_stars(rating):

    rating = int (rating * 10)

    # Mapping rating to its respective star
    if rating in range(97, 100):
        return 5
    elif rating in range(95, 97):
        return 5
    elif rating in range(90, 95):
        return 4.5
    elif rating in range(85, 90):
        return 4
    elif rating in range(80, 85):
        return 3.5
    elif rating in range(75, 80):
        return 3
    elif rating in range(70, 75):
        return 3
    elif rating in range(60, 70):
        return 2.5
    elif rating in range(50, 60):
        return 2
    elif rating in range(40, 50):
        return 1.5
    elif rating in range(30, 40):
        return 1.0
    elif rating in range(20, 30):
        return 0.5
    else:
        return 0

def create_df():
    
    # Creating dataframe
    df = pd.read_csv("movies.csv").fillna("")

    for i in range(len(df)):
        if df.loc[i, 'imdbID'] == "":
            df.loc[i, 'imdbID'] = get_imdb_id(df.loc[i, 'Title'])

    df['Stars'] = df['Rating'].map(lambda x: rating_to_stars(x))
    
    return df

# def create_protos_from_csv(df):
#     titles = df['Title'].to_list()

#     for title in titles:
#         proto = review_tool.create_proto(title)
#         filename = ("movies_textproto/" + proto.title + " ({})".format(proto.release_year) + ".textproto").replace(":","")

#         if not os.path.exists(filename): 
#             review_tool.write_proto(proto)

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

if __name__=="__main__":
    df = create_df()
    # df.to_csv("movies.csv", index=False)
    create_protos_from_csv(df)
    # create_protos_free_from_csv(df)

