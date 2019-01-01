from argparse import ArgumentParser
from feedparser import parse
from urllib.request import urlopen
from json import dumps

# --------------------------------

def process_duration(str):
    secconds = 0
    slices = str.split(":")
    factor = 1
    while len(slices) > 0:
        secconds += factor * int(slices.pop(-1))
        factor *= 60
    return secconds

def remove_extra_description_data(description):
    return description.split("***")[0]

def generate_feed_item(feedItem, socialMetadata):
    result = {}
    result["title"] = feedItem["title"]
    result["description"] = feedItem["summary"] if socialMetadata == None else remove_extra_description_data(feedItem["summary"])
    result["link"] = feedItem["link"]
    result["guid"] = feedItem["id"]
    links = feedItem["links"]
    result["mediaurl"] = [x for x in links if x["rel"] == "enclosure"][0]["href"]
    result["publicationdate"] = feedItem["published"]
    result["duration"] = process_duration(feedItem["itunes_duration"])
    return result

def generate_feed(feedUrl, feedPath, destinationPath, socialMetadata):
    print("Obteniendo información del Feed RSS")
    content = urlopen(feedUrl).read()
    feed = parse(content)

    print("Procesando Feed")
    result = {"version": "1.0"}
    result["title"] = feed["feed"]["title"]
    result["description"] = feed["feed"]["subtitle"]
    result["linksharing"] = feed["feed"]["link"]
    result["imageurl"] = feed["feed"]["image"]["href"]
    result["items"] = [generate_feed_item(x, socialMetadata) for x in feed["entries"]]

    if socialMetadata != None:
        with open(socialMetadata) as f:
            socialMetadata = f.read()
        result["metadata"] = {"social": socialMetadata}

    print("Generando Feed Nuevo")
    if feedPath != None:
        with open(feedPath, "wb") as f:
            f.write(content)
    
    with open(destinationPath, "w") as f:
        f.write(dumps(result))

    print("Tarea Completada")

# --------------------------------

def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument("--url", "-u", required=True, help="URL del feed RSS")
    parser.add_argument("--feedfile", "-f", help="Ruta donde se guardará el feed RSS en local")
    parser.add_argument("--destination", "-d", required=True, help="Ruta donde se guardará el feed JSON")
    parser.add_argument("--social_metadata", "-sm",  help="Ruta a un archivo con la descripción de las redes sociales")

    return parser.parse_args()

# --------------------------------

def main():
    args = parse_arguments()
    generate_feed(args.url, args.feedfile, args.destination, args.social_metadata)

if __name__ == "__main__":
    main()
