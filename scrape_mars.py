from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import requests 

from webdriver_manager.chrome import ChromeDriverManager

def browser_init():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    browser = browser_init()
    
    news_title, news_p = news(browser)
    featured_image_url = image(browser)
    mars_facts = facts()
    hems_list = hemispheres(browser)
    
    data = {}

    data["mars_news"] = news_title
    data["mars_text"] = news_p

    data["featured_image"] = featured_image_url

    data["mars_facts"] = mars_facts

    data["mars_hems"] = hems_list

    return data

def news(browser):
    # URL of NASA page to be scraped
    nasa_url = 'https://mars.nasa.gov/news/'
    browser.visit(nasa_url)

    # Scrape page into Soup
    html = browser.html
    nasa_soup = BeautifulSoup(html, 'html.parser')
    
    # Retrieve the latest element that contains news title and news_paragraph
    results = nasa_soup.find_all('li', class_="slide")[0]

    # scrape the article title 
    news_title = results.find('div', class_='content_title').text

    # scrape the article paragraph
    news_p = results.find('div', class_='article_teaser_body').text

    return news_title, news_p

def image(browser):
    # URL of JPL page to be scraped
    featured_image_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(featured_image_url)

    # Navigate to id for button "Full Image" & click
    browser.find_by_id('full_image').click()

    # Click button "More Info"
    browser.links.find_by_partial_text('more info').click()

    # Retrieve Featured image from page
    jpl_soup = BeautifulSoup(browser.html, "html.parser")
    featured_image_url = f"https://www.jpl.nasa.gov{jpl_soup.find('img', class_='main_image')['src']}"

    return featured_image_url

def facts():
    mars_facts = pd.read_html('https://space-facts.com/mars/')[0]
    mars_facts.columns=["Description", "Data"]
    mars_facts.set_index("Description", inplace=False)

    return mars_facts.to_html()

def hemispheres(browser):
    # URL of USGS AstroGeology page to be scraped
    USGS_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(USGS_url)

    hemispheres = browser.find_by_css('h3')
    hems_list =[]


    for hemisphere in range(len(hemispheres)):
        mars_hem_dict = {}
        title = browser.find_by_css('a.product-item h3')[hemisphere].text
        
        # remove enhanced
        title = title.split(" ")
        for word in title:
            if word == "Enhanced":
                title.remove(word)
        title = " ".join(title)
               
        # create empty dict to store title & URL , then append dicts to larger list
        mars_hem_dict["title"] = title
        browser.find_by_css('a.product-item h3')[hemisphere].click()
        
        # Navigate to image download 
        mars_image = browser.find_by_text('Sample').first['href']
        # store img in dict
        mars_hem_dict["image"] = mars_image
        # store dictionary items into hems_list
        hems_list.append(mars_hem_dict)
        
        browser.back()

    return hems_list