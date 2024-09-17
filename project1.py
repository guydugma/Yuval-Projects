from dataclasses import dataclass
import re
from bs4 import BeautifulSoup
import requests
import logging
BASE_URL='https://www.momondo.com/'
TIME_PATTERN=r"(\d{1,2}:\d{2} (am|pm))"
logging.basicConfig(level=logging.DEBUG)

@dataclass
class SearchResult:
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    connections: int
    airlines: str
    
    def __str__(self):
        return f"Flight from {self.origin} to {self.destination} from {self.departure_time} to {self.arrival_time} with {self.connections} connections by {self.airlines}"


def get_price(segment:BeautifulSoup):
    price_segment=segment.find("div",{'class':re.compile(r".*price-text")})
    return price_segment.get_text()

def get_num_connections(segment:BeautifulSoup):
    outgoing_connections=0
    return_connections=0
    span=segment.find_all("span",{"class":re.compile(r".*stops-text")})
    if span[0].get_text()!="nonstop":
        outgoing_connections=span[0].get_text()[0]
    if span[1].get_text()!="nonstop":
        return_connections=span[1].get_text()[0]
    return outgoing_connections,return_connections

def get_times(segment:BeautifulSoup):
    divs=segment.find_all("div",{"class":"vmXl vmXl-mod-variant-large"})
    outgoing_times=divs[0].find_all("span")
    returning_times=divs[1].find_all("span")
    return ((outgoing_times[0].get_text(),outgoing_times[2].get_text()),(returning_times[0].get_text(),returning_times[2].get_text()))

def get_airlines(segment:BeautifulSoup):
    divs=segment.find_all("div",{"class":"VY2U"})
    outgoing_airlines=divs[0].find("div",{'class':"c_cgF c_cgF-mod-variant-default"})
    returning_airlines=divs[1].find("div",{'class':"c_cgF c_cgF-mod-variant-default"})
    return outgoing_airlines.get_text(),returning_airlines.get_text()

def results(origin:str,destination:str,departure_date:str,return_date:str):
    request_link=f"{BASE_URL}flight-search/{origin}-{destination}/{departure_date}/{return_date}?sort=price_a"
    session = requests.Session()
    flights_list=[]
    session.get(BASE_URL,headers={'User-Agent':'Mozilla/5.0'})
    soup=BeautifulSoup(session.get(request_link,headers={'User-Agent':'Mozilla/5.0'}).text,'html.parser')
    soup_segments=soup.findAll("div",{"data-resultid" : re.compile(r".*")})
    for segment in soup_segments:
        price=get_price(segment)
        connections=get_num_connections(segment)
        outgoing_times,returning_times=get_times(segment)
        outgoing_airlines,returning_airlines=get_airlines(segment)
        flights_list.append({'outbound':SearchResult(origin,destination,departure_time=outgoing_times[0],arrival_time=outgoing_times[1],connections=connections[0],airlines=outgoing_airlines),
                            'return':SearchResult(origin=destination,destination=origin,departure_time=returning_times[0],arrival_time=returning_times[1],connections=connections[1],airlines=returning_airlines),
                            'price':price})
    output=""
    for result in flights_list:
        output+=(f"outbound: {str(result['outbound'])}\n return: {str(result['return'])}\n price: {result['price']}\n\n")
    return output

print(results('TLV','BUD','2024-09-18','2024-10-16'))





