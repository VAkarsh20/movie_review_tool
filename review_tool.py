import sys
from tools.sheets import initialize_to_sheets, post_to_sheets, reviews_sorted
from tools.letterboxd import post_to_letterboxd
from tools.imdb import post_to_imdb
from tools.video_description import get_post_description
from tools.proofread import proofread
import os

import pandas as pd
import multiprocessing as mp
import subprocess

import copy
from utils.proto_utils import *
from utils.print_utils import *
from utils.text_utils import *

# TODO: Redux is not created for Home Alone 2
# TODO: Redux not created for Star Wars Episode I because of '-' char
# TODO: Redux is not created for The Big Short
def move_redux_reviews(filename):
    path = os.path.join(os.path.dirname(__file__), 'movies_textproto/')
    count = 0
    while os.path.exists(path + ("reduxed/" * count) + filename + ".textproto"):
        print(path + ("reduxed/" * count) + filename + ".textproto")
        count += 1

    if not os.path.exists(path + ("reduxed/" * count)):
        os.mkdir(path + ("reduxed/" * count))

    while count > 0:
        os.rename(path + ("reduxed/" * (count - 1)) + filename + ".textproto", path + ("reduxed/" * (count)) + filename + ".textproto")
        count -= 1

if __name__=="__main__":    
    argc = len(sys.argv)

    # Reset clock
    subprocess.run(["sudo", "hwclock", "-s"])

    if argc == 1 or sys.argv[1] == "create_proto":
        # TODO: Deletes original version of the file
        if argc > 2 and sys.argv[2] == "redux":
            movie = create_proto(True)
            move_redux_reviews(get_filename(movie.title, movie.release_year))
        else:
            movie = create_proto()
            initialize_to_sheets(movie)
        write_proto(movie)
    elif sys.argv[1] == "create_proto_free":
        # TODO: Deletes original version of the file
        if argc > 2 and sys.argv[2] == "redux":
            movie = create_proto(True)
            move_redux_reviews(get_filename(movie.title, movie.release_year))
            initialize_to_sheets(movie)
        else:
            movie = create_proto_free()
            initialize_to_sheets(movie)
        write_proto(movie)
    elif sys.argv[1] == "reviews_sorted":
        print(reviews_sorted())   
    elif sys.argv[1] == "post_to_sheets":
        filename = input("What is the name of the movie?\n")

        # Get details for post
        proto = read_proto(filename)
        sanity_check(proto)
        if proto.rating == 0.1:
            print("Cannot post a review with a 0.1/10.0. Please fix rating.")
            sys.exit(0)
        review = print_review(proto, filename)
        
        post_to_sheets(proto, review)
    elif sys.argv[1] == "post_to_letterboxd":   
        filename = input("What is the name of the movie?\n")

        # Get details for post
        proto = read_proto(filename)
        sanity_check(proto)
        if proto.rating == 0.1:
            print("Cannot post a review with a 0.1/10.0. Please fix rating.")
            sys.exit(0)
        short_review = print_short_review(proto, filename)

        post_to_letterboxd(proto, short_review)
    elif sys.argv[1] == "post_to_imdb":
        filename = input("What is the name of the movie?\n")

        # Get details for post
        proto = read_proto(filename)
        sanity_check(proto)
        if proto.rating == 0.1:
            print("Cannot post a review with a 0.1/10.0. Please fix rating.")
            sys.exit(0)
        imdb_review = print_imdb_review(proto, filename)

        post_to_imdb(proto, imdb_review)
        
    elif sys.argv[1] == "post_to_all":
        filename = input("What is the name of the movie?\n")

        # Get details for post
        proto = read_proto(filename)
        sanity_check(proto)
        if proto.rating == 0.1:
            print("Cannot post a review with a 0.1/10.0. Please fix rating.")
            sys.exit(0)
        review = print_review(proto, filename)
        short_review = print_short_review(proto, filename)
        imdb_review = print_imdb_review(proto, filename)

        # Post to Sheets and Letterboxd
        p_sheets = mp.Process(target=post_to_sheets, args=(proto, review))
        p_letterboxd = mp.Process(target=post_to_letterboxd, args=(copy.deepcopy(proto), short_review))
        p_imdb = mp.Process(target=post_to_imdb, args=(copy.deepcopy(proto), imdb_review))

        p_sheets.start()
        p_letterboxd.start()
        p_sheets.join()
        p_letterboxd.join()
        p_imdb.start()
        p_imdb.join()
    elif sys.argv[1] == "get_post_description":
        filename = input("What is the name of the movie?\n")

        # Get details for post
        proto = read_proto(filename)

        print(get_post_description(proto))
    elif sys.argv[1] == "proofread":
        filename = input("What is the name of the movie?\n")

        # Get details for post
        proto = read_proto(filename)

        print(proofread(proto))
    else:
        print("Invalid input. Please try again.")