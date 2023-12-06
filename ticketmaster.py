import requests
import json

# root URL : https://app.ticketmaster.com/{package}/{version}/{resource}.json?apikey=**{API key}
# apikey = A3phA47g5rC6uF9zpmgWGxlD7SCtsimG

# to find the id of an artist or venue: 
    # /attractions or /venues in url -> set "keyword" param -> retrieve d["_embedded"]["venues/attractions"][0]["id"]

# create table if not exists
# read locations from file
# keep count of number retrieved from APi and stop at 200

def get_data(api_key, page):

    resp = requests.get("https://app.ticketmaster.com/discovery/v2/events.json", params={"apikey": api_key, "attractionId": "K8vZ9175Tr0", "page": page})
    dct = json.loads(resp.content)
    events = dct["_embedded"]["events"]

    for event in events:
        city = event["_embedded"]["venues"][0]["city"]["name"]

        if "priceRanges" in event:
            max_price = str(event["priceRanges"][0]["max"])
            print(city + ": max " + max_price)
        else:
            print(city + ": none")

    return dct["_embedded"]["events"]

    

def write_json(filename, dict):

    f = open(filename, "w")
    f.write(json.dumps(dict))
    f.close()


    # https://app.ticketmaster.com/discovery/v2/events.json?apikey=A3phA47g5rC6uF9zpmgWGxlD7SCtsimG&keyword=Taylor%20Swift

    # artist = input("What's your favorite music artist (or 'quit')? ")
    # urls = []

    # while artist != 'quit':

    #     resp = requests.get("https://app.ticketmaster.com/discovery/v2/attractions.json", params={"apikey": api_key, "keyword": artist})
    #     dct = json.loads(resp.content)
    #     url = dct["_embedded"]["attractions"][0]["url"]
    #     if url not in urls:
    #         urls.append(url)
    #     print(url)
    #     artist = input("What's your favorite music artist (or 'quit')? ")

    # return urls 
    


def main():

    data = get_data("A3phA47g5rC6uF9zpmgWGxlD7SCtsimG", 2)
    write_json("test.json", data)


main()

