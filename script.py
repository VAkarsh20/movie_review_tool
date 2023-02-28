# Not Good Code! Including for people who want some ideas.

import wikipedia
import pandas as pd
import numpy as np
import review_tool
import os
import movie_pb2
from google.protobuf import text_format
import sys
from collections import defaultdict
import sheets

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
        return 4
    elif rating in range(75, 80):
        return 3.5
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

def rating_to_tag(rating):

    rating = int (rating * 10)

    # Mapping rating to its respective tag
    if rating in range(97, 100):
        return "Brilliant"
    elif rating in range(95, 97):
        return "Incredible"
    elif rating in range(90, 95):
        return "Great"
    elif rating in range(85, 90):
        return "Very Good"
    elif rating in range(80, 85):
        return "Good"
    elif rating in range(75, 80):
        return "Pretty Good"
    elif rating in range(70, 75):
        return "Decent"
    elif rating in range(60, 70):
        return "Pretty Bad"
    elif rating in range(40, 60):
        return "Bad"
    elif rating in range(30, 40):
        return "Very Bad"
    else:
        return "Terrible"

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

def fill_in_acting(comments):
    
    def fill_in_acting_comments(actors_dict, comment):
        if "from the rest of the cast" in comment:
            proto.review.acting.cast = comment
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

def fill_in_proto(field):
    
    if "Direction" in field and proto.review.direction.comments == "Direction ()":
        proto.review.direction.comments = field
        return True
    elif "Acting" in field and proto.review.acting.comments.strip() == "Acting":
        fill_in_acting(field)
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
    elif "Plot Structure" in field and proto.review.plot_structure == "Plot Structure ":
        proto.review.plot_structure = field
        return True
    elif "Pacing" in field and proto.review.pacing == "Pacing ":
        proto.review.pacing = field
        return True
    # elif field.startswith("the build to climax") and proto.review.climax == "climax ":
    #     proto.review.climax = field.replace("the build", "Build")
    #     return True
    # elif field.startswith("climax"):
    #     proto.review.climax += "; {}".format(field)
    #     return True
    elif field.startswith("climax"):
        proto.review.climax = field.capitalize()
        return True
    elif field.startswith("tone "):
        proto.review.tone = field.capitalize()
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

    global res
    res = []
    stack = []
    while current < len(comments):
        if comments[current] == "(":
            stack.append("(")
        elif comments[current] == ")":
            stack.pop()
        if comments[current] == "," and len(stack) == 0:
            field = comments[start:current].strip()
            if not fill_in_proto(field):
                res.append(field + "\n")
            start = current + 1
        current += 1
    res.append(comments[start:].strip())
    proto.review.overall = overall

    if len(stack) > 0:
        raise Exception("Review is invalid, there is an extra (")

    with open("parsed.txt", "w") as fd:
        fd.writelines(res)
    
    with open("movies_textproto/" + filename + ".textproto", "w") as fd:
        text_proto = text_format.MessageToString(proto)
        fd.write(text_proto)

def add_id(df, start_idx):

    # read_proto(filename)
    # with open("movies_textproto/" + filename + ".textproto", "r") as fd:
    #     text_proto = fd.read()

    # return text_format.Parse(text_proto, movie_pb2.Movie())

    title = ""
    new_df = df.copy()
    count = 0
    for i in range(start_idx, len(df)):
        
        try: 
            
            record = df.iloc[i]
            title = record['Title']

            if title in ["Best F(r)iends: Volume 1", "We Are Columbine"]:
                continue

            wiki_title = title.replace(" ", "_")
            infobox = review_tool.parse_wiki("https://en.wikipedia.org/wiki/" + wiki_title)

            if title.endswith("film)"):
                title = title[:title.rfind(' (')]
            
            filename = (title + " ({})".format(review_tool.find_release_year(infobox))).replace(":","").replace("?","")
            
            proto = review_tool.read_proto(filename)

            proto.id = record['Id']

            review = review_tool.print_review(proto)
            with open("movies_textproto/" + filename + ".textproto", "w") as fd:
                text_proto = text_format.MessageToString(proto)
                fd.write(text_proto)
            
        except:
            raise Exception("Issue with {} {}".format(title, i))
            continue
    print(count)


def add_imdb_id(start_idx, df):
    title = ""
    files = os.listdir("movies_textproto/")
    
    id_to_imdb = dict(map(lambda x,y : (x,y) , df['Id'], df['imdbID']))

    for i in range(start_idx, len(files)):
        
        try: 
            filename = files[i].replace(".textproto","")
            proto = review_tool.read_proto(filename)

            proto_id = proto.id
            if proto_id > 315:
                print(proto.title)
                continue

            proto.imdb_id = id_to_imdb[proto.id]

            with open("movies_textproto/" + filename + ".textproto", "w") as fd:
                text_proto = text_format.MessageToString(proto)
                fd.write(text_proto)
            
        except:
            raise Exception("Issue with {} {}".format(title, i))
            continue


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

if __name__=="__main__":

    argc = len(sys.argv)

    # df = create_df()

    # add_imdb_id(109, df)
    # if argc > 1:
        # filename = sys.argv[1]
        # parse_review(df, filename)

    # update_csv()

    # df.to_csv("movies.csv", index=False)
    # create_protos_from_csv(df)
    # create_protos_free_from_csv(df)
    proto = review_tool.read_proto("Pathaan (2023)")
    sheets.initialize_to_sheets(proto)

