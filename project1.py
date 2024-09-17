import re
from bs4 import BeautifulSoup
import requests
LINK='https://www.momondo.com/'
TIMEPATTERN=r"(\d{1,2}:\d{2} (am|pm))"


def getPrice(soup):
    soup=soup[soup.find("price-text"):]
    dollar_index=soup.find("$")
    if dollar_index==-1:
        return
    price=""
    dollar_index+=1
    while True:
        price+=soup[dollar_index]
        dollar_index+=1
        if  dollar_index==len(soup) or not soup[dollar_index].isnumeric():
            break
    return price

def getNumConnections(soup):
    soup=soup[soup.find("stops-text")+1:]
    stop_index=soup.find("stop")
    if stop_index==-1:
        return
    num_of_stops=0
    if soup[stop_index-2].isnumeric():
        num_of_stops=int(soup[stop_index-2])
    return num_of_stops

def getTimes(soup):
    departure_time=re.search(TIMEPATTERN,soup)
    index=soup.find(departure_time[0])+1
    arrival_time=re.search(TIMEPATTERN,soup[index:])
    return departure_time[0],arrival_time[0]

def getAirlines(soup):
    start_index=soup.find('<div class="c_cgF c_cgF-mod-variant-default" dir="auto">')+len('<div class="c_cgF c_cgF-mod-variant-default" dir="auto">')+3
    end_index=soup[start_index:].find('</div>')+start_index-3
    while soup[start_index]==" ":
        start_index+=1
    while soup[end_index]==" ":
        end_index-=1
    return soup[start_index:end_index]

def results(origin,destination,departure_date,return_date):
    request_link=LINK+"flight-search/"+origin+"-"+destination+"/"+departure_date+"/"+return_date+"?sort=price_a"
    session = requests.Session()
    flights_list=[]
    with open("output.txt", "w", encoding="utf-8") as f:
        session.get(LINK,headers={'User-Agent':'Mozilla/5.0'})
        soup=BeautifulSoup(session.get(request_link,headers={'User-Agent':'Mozilla/5.0'}).text,'html.parser').prettify()
        f.write(soup)
        start_index=soup.find("data-resultid")
        soup=soup[start_index:]
        while start_index!=-1:
            price=getPrice(soup)
            connections=getNumConnections(soup)
            times=getTimes(soup)
            airlines=getAirlines(soup)
            start_index=soup.find("data-resultid",1)
            soup=soup[start_index:]
            flights_list.append({
                "origin":origin,
                "destination":destination,
                "departs at":times[0],
                "arrives at":times[1],
                "price":price+"$",
                "connections":connections,
                'airlines':airlines
                })
    return flights_list

print(*results('TLV','BUD','2024-09-18','2024-10-16'),sep="\n")





