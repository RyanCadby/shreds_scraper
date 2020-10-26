#imports
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException as ex
# import time
from bs4 import BeautifulSoup
# source venv/bin/activate
# import pandas as pd
# import re
# import os
#website urls
base_url = 'http://www.worldsnowboarding.org/'
athletes_url = 'http://www.worldsnowboarding.org/points-lists/?type=SS&gender=M#table'
# athletes_url = 'http://www.worldsnowboarding.org/points-lists/27/?type=SS&gender=M'
# athletes_url = 'http://www.worldsnowboarding.org/points-lists/?type=SS&gender=W#table'
# athletes_url = 'http://www.worldsnowboarding.org/points-lists/9/?type=SS&gender=M'

# Chrome session
driver = webdriver.Chrome(executable_path='/Users/rcadby/Sites/shreds_scraper/chromedriver')
driver.get(athletes_url)
driver.implicitly_wait(100)

# name the output file to write to local disk
out_filename = "./csv/snowboard-profiles.csv"
# header of csv file to be written
headers = "riderName, position, points, sponsors, age, nationality, stance, height, residence, resort, website, facebook, twitter, nationality_full  \n"

# opens file, and writes headers
f = open(out_filename, "w")
f.write(headers)

# get initial page soup
page_soup = BeautifulSoup(driver.page_source, 'html.parser')

# count number of pages
page_count = page_soup.find('div', attrs={'class': 'pagination-links'}).find_all('a')
pages = []
for link in page_count:
    pages.append(link)
page_total = pages[-2].text.strip()
page_total = int(page_total)
print("page total: " + str(page_total))

for i in range(page_total): # for each page

    # count profiles per page
    profile_count = len(driver.find_elements_by_class_name('ranking'))
    print('number of riders ' + str(profile_count))

    
    # create list of rider links per page
    rank_page_soup = BeautifulSoup(driver.page_source, 'html.parser')
    # profile a tags
    profile_links = rank_page_soup.find_all(class_="ranking-table-link")
    # get urls from a tags
    rider_link_array = []
    for profile_link in profile_links:
        rider_link_input = 'http://www.worldsnowboarding.org/' + profile_link.get('href')
        # rider_link_input = profile_link.get('href')
        rider_link_array.append(rider_link_input)


    # get whole rank row
    profile_data = rank_page_soup.find_all("tr", {"class":"ranking"})
    print(profile_data)
    country_array = []
    score_array = []
    position_array = []
    # get array of full country names
    for row in profile_data:
        try:
            country_array.append(row.find("span", {"class": "icon-flag-medium"})['oldtitle'])
            score_array.append(float(row.find("td", {"class": "last"}).text))
            position_str = row.findChildren()[0].span.text
            position = int(position_str[:-1])
            position_array.append(position)
        except:
            score_array.append('')
            country_array.append('')
            position_array.append(0)


    print('profile links:')
    print(profile_links)     # print all a tags to profiles
    print('rider links:')
    print(rider_link_array)  # print all urls to profiles
    print('full countries:')
    print(country_array)
    print('scores:')
    print(score_array)
    print('positions:')
    print(position_array)
    
    loop_counter = 0
    for rider_link in rider_link_array:
        # initiate list for rider stats
        profile = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
        # assign full country name to profile
        profile[13] = country_array[loop_counter]
        profile[1] = position_array[loop_counter]
        profile[2] = score_array[loop_counter]
        # click on rider profile
        driver.get(rider_link)
        # get html on rider page and parse
        profile_soup = BeautifulSoup(driver.page_source, 'html.parser')
        # get rider name
        try:
            rider_name = profile_soup.select('h1.rider-label')[0].text.strip()
            profile[0] = rider_name

            # #get rider points
            # rider_point_soup = profile_soup.find('div', attrs={'id': 'result-table-points-list-ss'})
            # if rider_point_soup is not None:
            #     rider_point_cont = rider_point_soup.ul.find_all('li')
            #     point_counter = 1
            #     for litag in rider_point_cont:
            #         rider_point_data = litag.getText()
            #         rider_point_info = rider_point_data.split(':', 1)
            #         profile[point_counter] = rider_point_info[1]
            #         point_counter += 1
            # else:
            #     profile[1] = ''
            #     print('FAIL: no slopestyle score')
                
            # get rider sponsors
            rider_sponsor_soup = profile_soup.find('div', attrs={'class': 'sponsor-list'})
            if rider_sponsor_soup is None:
                profile[3] = ''
            else:
                rider_sponsor_soup_conf = rider_sponsor_soup.ul.find_all('li')
                sponsors = ''
                for litag in rider_sponsor_soup_conf:
                    sponsor_item = litag.text.strip()
                    sponsors += sponsor_item + ' | '

                profile[3] = sponsors

            profile_code_soup = profile_soup.find_all('ul', attrs={'class': 'plain-list'})
            for ultag in profile_code_soup:
                profile_li = ultag.find_all('li')

                for litag in profile_li:
                    # get data
                    profile_info = litag.getText()
                    # clean data
                    profile_info = profile_info.replace("'", 'ft.')
                    profile_info = profile_info.replace('"', 'in.')
                    profile_info = profile_info.replace(',', '|')

                    profile_type, profile_stat = profile_info.split(":", 1)
                    profile_type = profile_type.lower()
                    profile_stat = profile_stat.strip()

                    # check nationality
                    if profile_type == 'age':
                        profile[4]=profile_stat
                    elif profile_type == 'nationality':
                        profile[5]=profile_stat
                    elif profile_type == 'stance':
                        profile[6]=profile_stat
                    elif profile_type == 'height':
                        profile[7]=profile_stat
                    elif profile_type == 'residence':
                        profile[8]=profile_stat
                    elif profile_type == 'home resort':
                        profile[9]=profile_stat
                    elif profile_type == 'website':
                        profile[10]=profile_stat
                    elif profile_type == 'facebook':
                        profile[11]=profile_stat
                    elif profile_type == 'twitter':
                        profile[12]=profile_stat
                    elif profile_type == 'instagram':
                        profile[13]=profile_stat
                    else:
                        pass

            profile_str = ', '.join(str(x) for x in profile)
            print('PROFILE STRING: ' + profile_str)
            f.write(profile_str)

            # go back to initial page
            driver.execute_script("window.history.go(-1)")

            #start new line for new rider profile
            f.write("\n")
        except:
            print('FAIL: 404 go back')
            # go back to initial page
            driver.execute_script("window.history.go(-1)")

            table_soup = BeautifulSoup(driver.page_source, 'html.parser')
            # find url in table
            url = rider_link.strip('http://www.worldsnowboarding.org/')
            find_link = table_soup.select_one("a[href*='" + url + "']")
            # find parent of url - this is the row that has all the rider info
            parent = find_link.find_parent('tr', attrs={'class': 'ranking'})
            stat_array = parent.find_all('td')

            profile[1] = int(stat_array[0].span.text.strip('.'))       #position
            name = stat_array[3].a.text.split(',')
            first_name = name[1]
            last_name = name[0]
            profile[0] = str(first_name + last_name)   #name
            profile[5] = stat_array[4].span.text       #nationality
            if stat_array[5] is not None or len(stat_array[5]) > 0:
                profile[4] = stat_array[5].text     #age
            profile[2] = float(stat_array[8].text)  #points

            profile_str = ', '.join(str(x) for x in profile)
            print('PROFILE STRING (FROM TABLE): ' + profile_str)
            f.write(profile_str)

            #start new line for new rider profile
            f.write("\n")

        loop_counter += 1
     # navigate to link
    page_next = driver.find_element_by_class_name('next')
    page_next.click()


f.close()  # Close the file
driver.quit()

# WHEN IT IS DONE!!
# Traceback (most recent call last):
#   File "sel_scraper_3.py", line 185, in <module>
#     page_next = driver.find_element_by_class_name('next')
#   File "/usr/local/lib/python3.8/site-packages/selenium/webdriver/remote/webdriver.py", line 564, in find_element_by_class_name
#     return self.find_element(by=By.CLASS_NAME, value=name)
#   File "/usr/local/lib/python3.8/site-packages/selenium/webdriver/remote/webdriver.py", line 976, in find_element
#     return self.execute(Command.FIND_ELEMENT, {
#   File "/usr/local/lib/python3.8/site-packages/selenium/webdriver/remote/webdriver.py", line 321, in execute
#     self.error_handler.check_response(response)
#   File "/usr/local/lib/python3.8/site-packages/selenium/webdriver/remote/errorhandler.py", line 242, in check_response
#     raise exception_class(message, screen, stacktrace)
# selenium.common.exceptions.NoSuchElementException: Message: no such element: Unable to locate element: {"method":"css selector","selector":".next"}
#   (Session info: chrome=86.0.4240.80)
