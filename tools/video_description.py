def get_post_description(proto, show_year=False):

    res = proto.title

    if show_year:
        res += " {}".format(proto.release_year)

    res += "\n\n"

    res += "#" + proto.title.lower().replace(" ", "") + " "

    for performance in proto.review.acting.performance:
        res += (
            "#" + performance.actor.name.lower().replace(" ", "").replace(".", "") + " "
        )

    director = proto.review.direction.director.name
    if director != None:
        res += "#" + director.lower().replace(" ", "").replace(".", "") + " "

    res += "#foryoupage #fyp #moviereview #film #filmtok #movie #movietok"

    print("There are {} tags".format(res.count("#")))

    return res


def get_youtube_tags(proto):
    res = ["Cinema Personified", "cinemapersonified", proto.title]
    for performance in proto.review.acting.performance:
        res.append(performance.actor.name)
    res += ["movie", "film", "movietok", "filmtok", "For You Page", "fyp"]

    return ",".join(res)
