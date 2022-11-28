import requests
from bs4 import BeautifulSoup
from decimal import Decimal
import pandas as pd
import time
import json
import sqlalchemy as db

engine = db.create_engine('mysql://root:root_emax@localhost:3306/kyla_pub', echo=False)

def get_postcodes():
    conn = engine.connect()
    metadata = db.MetaData()
    city_be = db.Table('city_be', metadata, autoload=True, autoload_with=engine)
    province_be = db.Table('province_be', metadata, autoload=True, autoload_with=engine)
    query = db.select([city_be.c.postal_code.distinct()]).where(db.and_(db.and_(province_be.c.postal_code_min <= city_be.c.postal_code, province_be.c.postal_code_max >= city_be.c.postal_code)), province_be.c.region == 'Flanders').order_by('postal_code')
    postcodes = conn.execute(query).fetchall()
    postcodes = [r[0] for r in postcodes]

    return postcodes

def insert_data():
    postcodes = get_postcodes()

    for postcode_input in postcodes:
        try:
            ZIPCODE_URL = "https://vtest.vreg.be/Compare/ZipCode?zipcode="+ postcode_input + "&type=HH"
            response = requests.get(ZIPCODE_URL)
            postcode_id = json.loads(response.content)[0]["Id"]
            URL = "https://www.vtest.be/Compare/Result?Environment=Hh&postcode=" + postcode_input + "&postcodeId=" + str(postcode_id) +"&vergelijkingstype=elektriciteitEnAardgas&type=hh&IsGedomicilieerdInWoning=true&ElektriciteitHeeftDigitaleMeter=false&ElektriciteitHeeftZonnepanelen=false&ElektriciteitVermogenZonnepanelen=&kentElektriciteitsverbruik=false&elektricteitMetertype=EV&elektriciteitVerbruikBegin=&elektriciteitVerbruikEinde=&aantalPersonen=1&kentAardgasverbruik=false&gasType=L&aardgasVerbruikBegin=&aardgasVerbruikEinde=&aardgasVerwarming=false&gasWarmWater=true&elektriciteitContractvoorkeur=vast&gasContractvoorkeur=vast"

            page = requests.post(URL)

            soup = BeautifulSoup(page.text, 'html.parser')
            rows = soup.select('table tbody tr')

            data_list = list()
            for row in rows:
                tds = row.select('td')
                json_object = json.loads(tds[1].text)
                if (json_object["EnergyType"] == "E"):
                    data = {}
                    data['postal_code'] = postcode_input
                    data['supplier'] = json_object["SupplierBrandName"]
                    if tds[3].find('a'):
                        data['supplier_url'] = tds[3].find('a')['href']
                    else:
                        data['supplier_url'] = ""
                    data['product'] = json_object["Product"]
                    data['type'] = json_object["PriceType"]
                    data['duration'] = json_object["ContractDuration"].replace(" jaar", "")
                    if json_object["EnergyGreen"]:
                        data['green_percentage'] = json_object["EnergyGreen"]
                    else:
                        data['green_percentage'] = '0'
                    conditions = tds[4].find_all('a')
                    condition_content = ""
                    for condition in  conditions:
                        condition_content += " " + condition['data-content']
                    data['conditions'] = condition_content
                    price = float(json_object["Price"]) / 1200
                    data['price'] = round(price, 4)
                    data_list.append(data)
                
            # Create Pandas Dataframe
            df_bs = pd.DataFrame(data_list,columns=['postal_code','supplier', 'supplier_url', 'product', 'type', 'duration', 'green_percentage', 'conditions','price'])
            df_bs.sort_values(by=['price'], inplace=True, ascending=True)

            df_bs.loc[(df_bs['type'] == 'Vast') & (df_bs['duration'] == '1')].head(10).to_sql('electricity_offer', con=engine, if_exists='append', index=False)

            time.sleep(2)
        except Exception as e:
            print(e+ " " + postcode_input)
            continue