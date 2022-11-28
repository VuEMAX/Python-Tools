from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup, Comment
from decimal import Decimal
import pandas as pd
import time
from tabulate import tabulate

driver = webdriver.Chrome(executable_path='/opt/homebrew/bin/chromedriver')
#driver = webdriver.Firefox()
driver.implicitly_wait(30)

try:
    URL = "https://www.brugel.brussels/nl_BE/outils/brusim-2"
    driver.get(URL)

    frame = driver.find_element_by_id('tool-iframe-brusim-2')
    driver.switch_to.frame(frame)
    
    postcode_input = "1000"

    radioEnergyElec = driver.find_element_by_css_selector("input#radioEnergyElec")
    driver.execute_script("arguments[0].click();", radioEnergyElec)

    prosumerNo = driver.find_element_by_xpath("//input[@id='prosumerNo']")
    driver.execute_script("arguments[0].click();", prosumerNo)

    radioResidential = driver.find_element_by_id("radioResidential")
    driver.execute_script("arguments[0].click();", radioResidential)

    select_element = Select(driver.find_element_by_xpath('//*[@id="tab-1"]/form/fieldset[4]/div/div[2]/select'))
    select_element.select_by_value(postcode_input)

    button = driver.find_element_by_xpath('//*[@id="tab-1"]/div/div/div[2]/button')
    driver.execute_script("arguments[0].click();", button)
    
    elecDay = driver.find_element_by_id("elecDay")
    elecDay.send_keys('3500')
    
    button = driver.find_element_by_xpath('//*[@id="tab-2"]/div/div/div[2]/button[2]')
    driver.execute_script("arguments[0].click();", button)
    
    page_source = driver.page_source
    print(page_source)
    soup = BeautifulSoup(page_source, 'html.parser')
    print(soup.prettify())
    data = []
    table = soup.find_all('table')
    rows = table.find('tbody')
    for row in rows:
        print(row)
    #rows = soup.find_all('tbody')[1].find_all('tr')

    #data_list = list()
    #for row in rows:
        #print(row)
        #tds = row.select('td')s
        #if tds:
            #data = {}
            #print("------------")
            #supplier = ''
            #if tds[1].text:
                #supplier = tds[1].text
                #print("Supplier: " + supplier)
            
            #if tds[2].text:
                #product = tds[2].text
                #print("Product: " + tds[2].text)
            
            #if tds[3].text:
                #contract_type = tds[3].text
                #print("Contract type: " + tds[3].text)
            
            #if tds[4].text:
                #contract_duration = tds[4].text
                #print("Contract duration: " + tds[4].text)
            
            #if tds[7].text:
                #annual_price = tds[7].select('span')[1].text.replace("€ ", "").replace(",", ".")
                #price = float(annual_price) / 3500
                #print("Annual price: " + tds[7].text)
                #print("Price: " + str(round(price, 4)))

            #data['Postcode'] = postcode_input
            #data['Supplier'] = supplier
            #data['Product'] = product
            #data['Contract type'] = contract_type
            #data['Contract duration'] = contract_duration
            #data['Price'] = str(round(price, 4))
            #data_list.append(data)
    
    #Create Pandas Dataframe and print it
    #df_bs = pd.DataFrame(data_list,columns=['Postcode','Supplier', 'Product', 'Contract type', "Contract duration", "Price"])
    #print(df_bs.head())

    #Exporting the data into csv
    #df_bs.to_csv('brugel.csv')
except Exception as e:
    print(e)
finally:
    driver.quit()

