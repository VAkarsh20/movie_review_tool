def get_post_description(proto, show_year=False):

    res = proto.title
    
    if show_year:
        res += " {}".format(proto.release_year)

    res += "\n\n"

    res += "#" + proto.title.lower().replace(" ", "") + " "

    for performance in proto.review.acting.performance:
        res += "#" + performance.actor.name.lower().replace(" ", "").replace(".", "") + " "

    res += "#foryoupage #fyp #moviereview #film #filmtok #movie #movietok"

    print("There are {} tags".format(res.count('#')))

    return res