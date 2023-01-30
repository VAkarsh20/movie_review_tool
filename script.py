import wikipedia
import pandas as pd
import numpy as np


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

if __name__=="__main__":
    print(create_df())