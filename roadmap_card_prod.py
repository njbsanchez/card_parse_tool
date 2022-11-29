from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
import time
from datetime import date

from bs4 import BeautifulSoup
import json

options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


def parse_main_page(url):
    """
    takes in url of page, returns page source
    """
    
    driver.get(url)
    item_link = driver.find_elements(By.CLASS_NAME, value="item-link")
    cards_dictionary = {}
    

    for link in item_link:
        # 
        if link.is_displayed():
            driver.execute_script("arguments[0].click();", link)
            # time.sleep(1)
            current_url = driver.current_url
            print(current_url)
            
        try:
            param = current_url.split("?&p=",1)[1]
            print(param)
        except:
            param = str("none")
            
        cards_dictionary[param]={'url':current_url}
        
        print("card dictionary url is ", cards_dictionary[param])
        
    return cards_dictionary 

def add_to_dictionary(cards_dictionary):
    
    for param in cards_dictionary:
        
        url = cards_dictionary[param]['url']
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        content = soup.find_all(class_="modal-inner")  

        for i,card in enumerate(content,start=1):
        
            title = str(card.h4.string)
            desc = 'N/A' if card.find(class_="description").p is None else str(((card.find(class_="description")).p.contents)[0])
            try:
                status = str(card.find(class_="custom-category").contents[0])
            except:
                category = str("missing")
            try:
                category = str(card.find(class_="custom-category2").contents[0])
            except:
                category = str("none")
            try:
                date = str(card.find(class_="custom-field-1").contents[0])
            except:
                date = str("none")
            products = []
            try:
                for product in card.find(class_="custom-product").contents:
                    products.append(str(product.string))
            except:
                for product in card.find(class_="custom-productVersion").contents:
                        products.append(str(product.string))
            links=[]
            try:
                for a in card.find_all('a', href=True):
                    print("LINK HERE:", a["href"])
                    links.append(str(a['href']))
            except:
                links="none"
        
            cards_dictionary[param].update({
                'param':param,
                'title':title,
                'description':desc,
                'status':status,
                'category':category,
                'date':date,
                'products':products,
                'links':links
                })
            
            print("CARD DICTIONARY ITEM:")
            print(cards_dictionary[param])
            print("*********************------**********************")
    
    return cards_dictionary
        
    
def get_data(url):
    
    cards_dictionary = parse_main_page(url)
    add_to_dictionary(cards_dictionary)
    
    return cards_dictionary


def create_report(cards_dictionary, type):
    
    today = date.today()

    if type == "cloud":
        file_name = f'cloud_cards_{today}'
    elif type == "dc":
        file_name = f'dc_cards_{today}'
    else:
        file_name = f'undefined_{today}'
        
    with open(f'json_outputs/{file_name}.json', 'w') as outfile:
        json.dump(cards_dictionary, outfile)
    
    y=json.dumps(cards_dictionary)
    
    df = (pd.DataFrame.from_dict(cards_dictionary)).T
    file = f'csv_outputs/{file_name}.csv'
    df.to_csv (file, index = False, header=True)
  
def parse_roadmap(url, roadmap_type):
        
    cards_dictionary = get_data(url)
    create_report(cards_dictionary, roadmap_type)


if __name__ == "__main__":
    
    # cloud_url = 'https://proof.marketing.internal.atlassian.com/wac/roadmap/archived-cloud'
    # dc_url = 'https://proof.marketing.internal.atlassian.com/wac/roadmap/archived-data-center'

    cloud_url = 'https://atlassian.com/wac/roadmap/cloud'
    dc_url = 'https://atlassian.com/roadmap/data-center'

#    parse_roadmap(dc_url, "dc")
    parse_roadmap(cloud_url, "cloud")
    

