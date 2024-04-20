import os
from google.protobuf import text_format
import movie_pb2

def write_proto(proto):

    filename = (proto.title + " ({})".format(proto.release_year) + ".textproto").replace(":","").replace("/", " ").replace("?", "")
    path = ("movies_textproto/" + filename)
    if not os.path.exists(filename):
        with open(path, "w") as fd:
            text_proto = text_format.MessageToString(proto)
            fd.write(text_proto)
    else:
        print("File already exists! Either choose different file or move current to redux.")

def read_proto(filename):
    with open("movies_textproto/" + filename + ".textproto", "r") as fd:
        text_proto = fd.read()
        
        fd.seek(0)
        if len(fd.readlines()) <= 8:
            return text_format.Parse(text_proto, movie_pb2.MovieFree())
        else: 
            # TODO: Try Catch for old Proto Format
            return text_format.Parse(text_proto, movie_pb2.Movie())