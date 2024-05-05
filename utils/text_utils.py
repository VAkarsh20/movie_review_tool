
def get_filename(title, release_year):
    return (title + " ({})".format(release_year) + ".textproto").replace(":","").replace("/", " ").replace("?", "")