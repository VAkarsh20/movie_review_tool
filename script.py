# Not Good Code! Including for people who want some ideas.

import wikipedia
import pandas as pd
import numpy as np
import review_tool
import os
import movie_pb2
from google.protobuf import text_format
import sys

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

def fill_in_proto(proto, field):
    
    if "Direction" in field and proto.review.direction.comments == "Direction ()":
        proto.review.direction.comments = field
        return True
    elif "Story" in field and proto.review.story.comments == "Story ()":
        proto.review.story.comments = field
        return True
    elif "Screenplay" in field and proto.review.screenplay.comments == "Screenplay ()":
        proto.review.screenplay.comments = field
        return True
    elif "Score" in field and proto.review.score.comments == "Score ()":
        proto.review.score.comments = field
        return True
    elif "Cinematography" in field and proto.review.cinematography.comments == "Cinematography ()":
        proto.review.cinematography.comments = field
        return True
    elif "Sound" in field and proto.review.sound == "Sound ()":
        proto.review.sound = field
        return True
    elif "Editing" in field and proto.review.editing.comments == "Editing ()":
        proto.review.editing.comments = field
        return True
    elif "Visual Effects" in field and proto.review.visual_effects == "Visual Effects ()":
        proto.review.visual_effects = field
        return True
    elif "Production Design" in field and proto.review.production_design == "Production Design ()":
        proto.review.production_design = field
        return True
    elif "Makeup" in field and proto.review.makeup == "Makeup ()":
        proto.review.makeup = field
        return True
    elif "Costumes" in field and proto.review.costumes == "Costumes ()":
        proto.review.costumes = field
        return True
    else:
        return False

def parse_review(df, filename):

    
    global proto
    proto = review_tool.read_proto(filename)

    record = ""
    if not df[df['Title'] == proto.title].empty:
        record = df[df['Title'] == proto.title]
    elif not df[df['Title'] == "{} (film)".format(proto.title)].empty: 
        record = df[df['Title'] == "{} (film)".format(proto.title)]
    else:
        record = df[df['Title'] == "{} ({} film)".format(proto.title, proto.release_year)]
    review = record["Review"].item()
    
    start = 0
    current = 0

    period = review.split(". Overall, ")
    comments = period[0]
    overall = "Overall, " + period[1].rstrip(". ")

    res = []
    stack = []
    while current < len(comments):
        if comments[current] == "(":
            stack.append("(")
        elif comments[current] == ")":
            stack.pop()
        if comments[current] == "," and len(stack) == 0:
            field = comments[start:current].strip()
            if not fill_in_proto(proto, field):
                res.append(field + "\n")
            start = current + 1
        current += 1
    res.append(comments[start:].strip())
    proto.review.overall = overall

    if len(stack) > 0:
        raise Exception("Review is invalid")

    with open("parsed.txt", "w") as fd:
        fd.writelines(res)
    
    with open("movies_textproto/" + filename + ".textproto", "w") as fd:
        text_proto = text_format.MessageToString(proto)
        fd.write(text_proto)


if __name__=="__main__":

    argc = len(sys.argv)

    df = create_df()

    if argc > 1:
        filename = sys.argv[1]
        parse_review(df, filename)

    # df.to_csv("movies.csv", index=False)
    # create_protos_from_csv(df)
    # create_protos_free_from_csv(df)

