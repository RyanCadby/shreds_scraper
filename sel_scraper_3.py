#imports
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException as ex
# import time
from bs4 import BeautifulSoup

# import pandas as pd
# import re
# import os
#website urls
base_url = 'http://www.worldsnowboarding.org/'
athletes_url = 'http://www.worldsnowboarding.org/points-lists/?type=SS&gender=M#table'

# Chrome session
driver = webdriver.Chrome(executable_path='/Users/rcadby/Sites/shreds_scraper/chromedriver')
driver.get(athletes_url)
driver.implicitly_wait(100)

# name the output file to write to local disk
out_filename = "snowboard-profiles.csv"
# header of csv file to be written
headers = "riderName, position, points, sponsors, age, nationality, stance, height, residence, resort, website, facebook, twitter  \n"

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

for i in range(page_total): # for each page of 50 riders

    # count profiles per page
    profile_count = len(driver.find_elements_by_class_name('ranking'))
    print(profile_count)
    athlete_profiles = []

    # get initial page soup
    each_page_soup = BeautifulSoup(driver.page_source, 'html.parser')
    profile_links = each_page_soup.find_all(class_="ranking-table-link")
    print(profile_links)

    for i in range(profile_count):
        # initiate list for rider stats
        profile = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']


        # driver.implicitly_wait(5) # seconds

        try:
            element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'table')))
            print('SUCESS: table loaded')
        except ex:
            print('FAIL: could not find the table holding rider stats.... Refreshing Now')
            driver.execute_script("location.reload()")

        # navigate to link
        # WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "ttr-logo")))
        try: 
            profile_link = driver.find_elements_by_class_name('ranking-table-link')[i]
            profile_link.click()
            print('SUCCESS: clicked on rider link')
            rider_wait = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "rider-label")))
            if profile_link is None and rider_wait.tag_name != 'h1' :
                print('FAIL: could not find rider link or rider title')
                driver.execute_script("location.reload()")
                print('FAIL: reloaded page')
                profile_link.click()
            else:
                print('SUCCESS: on rider page')
        except ex:
            print('FAIL: could not find rider link')
            # check for page not found
            profile_soup_test = BeautifulSoup(driver.page_source, 'html.parser')
            fourhundo = profile_soup_test.find('div', attrs={'id': 'result-table-points-list-ss'}).h1.get_text()
            print(fourhundo)
            if fourhundo == 'Page Not Found':
                # go back to initial page
                driver.execute_script("window.history.go(-1)")
                print('FAIL: 404 page not found')
                #start new line for new rider profile
                f.write("\n")
                print('EXIT: write new line in csv')
                profile_link = driver.find_elements_by_class_name('ranking-table-link')[i+1]
                print('EXIT: find new rider')
                profile_link.click()
            else:
                driver.execute_script("location.reload()")
                profile_link = driver.find_elements_by_class_name('ranking-table-link')[i]
                profile_link.click()
        except IndexError:
            rider_wait = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "rider-label")))
            print('SUCCESS: found rider name on rider profile page')   
        # except:
        #     profile_link = driver.find_elements_by_class_name('ranking-table-link')[i]
        #     rider_wait = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "rider-label")))
        #     if profile_link is None and rider_wait.tag_name != 'h1' :
        #         driver.execute_script("location.reload()")
        #         profile_link.click()
        #     else:
        #         print('on rider page')

        # try:
        #     rider_wait = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "rider-label")))
        #     print('SUCCESS: found rider name on rider profile page')            
        # except ex:
        #     # get html and parse
        #     profile_soup = BeautifulSoup(driver.page_source, 'html.parser')
        #     not_found = profile_soup.find('ul', attrs={'class': 'plain-list'})
        #     if not_found is not None:
        #         print('on rider page found')
                
        #         profile[0] = profile_soup.find_all('.ranking-table-link')[i].text.strip()
        #         profile[5] = profile_soup.find_all('icon-flag-medium')[i].attrs.get('oldtitle')
        #         profile[5] = profile_soup.find_all('ranking')[i].td.text.strip()

        #         profile_str = ', '.join(str(x) for x in profile)
        #         print('PROFILE STRING: ' + profile_str)
        #         f.write(profile_str)
        #         f.write("\n")
        #         driver.execute_script("window.history.go(-1)")
        #         i += 1
        #         # navigate to link
        #         profile_link = driver.find_elements_by_class_name('ranking-table-link')[i]
        #         profile_link.click()
        #     else:
        #         print('Not on rider profile page... clicking now')
        #         profile_link.click()

        rider_wait = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "rider-label")))
        print('SUCCESS: found rider name on rider profile page')  
        # get html and parse
        profile_soup = BeautifulSoup(driver.page_source, 'html.parser')
        # get rider name
        rider_name = profile_soup.select('h1.rider-label')[0].text.strip()
        profile[0] = rider_name

        #get rider points
        rider_point_soup = profile_soup.find('div', attrs={'id': 'result-table-points-list-ss'})
        if rider_point_soup is not None:
            rider_point_cont = rider_point_soup.ul.find_all('li')
            point_counter = 1
            for litag in rider_point_cont:
                rider_point_data = litag.getText()
                rider_point_info = rider_point_data.split(':', 1)
                profile[point_counter] = rider_point_info[1]
                point_counter += 1
        else:
            profile[1] = ''
            print('FAIL: no slopestyle score')
            


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

     # navigate to link
    page_next = driver.find_element_by_class_name('next')
    page_next.click()


f.close()  # Close the file
driver.quit()