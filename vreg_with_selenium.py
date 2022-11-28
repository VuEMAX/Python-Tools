from selenium import webdriver
from bs4 import BeautifulSoup
from decimal import Decimal
import pandas as pd
import time

data_file = open("vreg_data.csv", "w")
data_file.write("postal_code,supplier,supplier_url,product,type,duration,green_percentage,conditions,price")
data_file.close()

file = open('flanders.csv', 'r')
postcodes = file.read().splitlines()

for postcode_input in postcodes:
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        driver = webdriver.Chrome(executable_path='/opt/homebrew/bin/chromedriver',options=options)   
        driver.implicitly_wait(10)
        URL = "https://vtest.vreg.be/"
        driver.get(URL)

        postcode = driver.find_element_by_id("postcode")
        postcode.send_keys(postcode_input)

        vglType_e = driver.find_element_by_css_selector("input#vglType_e")
        driver.execute_script("arguments[0].click();", vglType_e)

        type_hh = driver.find_element_by_xpath("//input[@id='type_hh']")
        driver.execute_script("arguments[0].click();", type_hh)

        gedomicilieerd_ja = driver.find_element_by_id("gedomicilieerd_ja")
        driver.execute_script("arguments[0].click();", gedomicilieerd_ja)

        digitalemeter_nee = driver.find_element_by_id("digitalemeter_nee")
        driver.execute_script("arguments[0].click();", digitalemeter_nee)

        zonnepanelen_nee = driver.find_element_by_id("zonnepanelen_nee")
        driver.execute_script("arguments[0].click();", zonnepanelen_nee)
        time.sleep(1)
        kentE_no = driver.find_element_by_id("kentE_no")
        driver.execute_script("arguments[0].click();", kentE_no)
        time.sleep(1)
        eMeter_EV = driver.find_element_by_css_selector("input#eMeter_EV")
        driver.execute_script("arguments[0].click();", eMeter_EV)
        time.sleep(1)
        elek_contractvoorkeur_optie_vast = driver.find_element_by_id("elek_contractvoorkeur_optie_vast")
        driver.execute_script("arguments[0].click();", elek_contractvoorkeur_optie_vast)
        time.sleep(1)
        aantalPersonen = driver.find_element_by_id("aantalPersonen")
        aantalPersonen.send_keys("1")

        driver.find_element_by_id("container").submit()
        page_source = driver.page_source

        soup = BeautifulSoup(page_source, 'html.parser')
        rows = soup.select('table tbody tr')

        data_list = list()
        for row in rows:
            tds = row.select('td')
            if tds:
                data = {}
                product = tds[1].text
                supplier = ""
                if tds[2].select('img') and tds[2].select('img')[0]:
                    supplier = tds[2].select('img')[0]['alt'].replace("Leverancier: ", "")

                about = tds[2].find('a')['href']

                conditions = tds[3].find_all('a')
                condition_content = ""
                for condition in  conditions:
                    condition_content += " " + condition['data-content']

                contract_type = tds[4].text
                
                contract_duration = tds[5].text.replace(",", " ").replace("jaar", "")

                green_percentage = tds[6].select('span')[0].text.replace("%", "")
                
                annual_price = tds[7].select('span')[0].text.replace("€ ", "").replace(",", ".")
                price = float(annual_price) / 1200

                data['Postcode'] = postcode_input
                data['Supplier'] = supplier
                data['About'] = about
                data['Product'] = product
                data['Contract type'] = contract_type
                data['Contract duration'] = contract_duration
                data['Green percentage'] = green_percentage
                data['Conditions'] = condition_content
                data['Price'] = str(round(price, 4))
                data_list.append(data)
        
        # Create Pandas Dataframe and print it
        df_bs = pd.DataFrame(data_list,columns=['Postcode','Supplier', 'About', 'Product', 'Contract type', 'Contract duration', 'Green percentage', 'Conditions','Price'])
        df_bs.sort_values(by=['Price'], inplace=True, ascending=True)

        # Exporting the data into csv
        df_bs.loc[df_bs['Contract duration'] == '1 jaar'].head(10).to_csv('vreg_data.csv', mode='a', index=False, header=False)
    except Exception as e:
        print(e)
    finally:
        driver.quit()
