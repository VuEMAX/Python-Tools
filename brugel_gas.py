import requests
import json
import pandas as pd
import sqlalchemy as db

engine = db.create_engine('mysql://root:root_emax@localhost:3306/kyla_pub', echo=False)

def flatten_json(condition_arrays):
    conditions = ""
    for condition in condition_arrays:
        conditions += " " + condition["descrEn"]
    return conditions

def get_postcodes():
    conn = engine.connect()
    metadata = db.MetaData()
    city_be = db.Table('city_be', metadata, autoload=True, autoload_with=engine)
    province_be = db.Table('province_be', metadata, autoload=True, autoload_with=engine)
    query = db.select([city_be.c.postal_code.distinct()]).where(db.and_(db.and_(province_be.c.postal_code_min <= city_be.c.postal_code, province_be.c.postal_code_max >= city_be.c.postal_code)), province_be.c.region == 'Brussels').order_by('postal_code')
    postcodes = conn.execute(query).fetchall()
    postcodes = [r[0] for r in postcodes]

    return postcodes

def insert_data():
    postcodes = get_postcodes()
    for postcode in postcodes:
        try:
            # Brugel api-endpoint
            url = "https://www.brusim.be/rest/comparison/doSimulation"

            data = '''{
                "zipCode":%s,
                "consumerType":"residential",
                "gasRequest":{
                    "profile": "D3b",
                    "dgoName": "Sibelga"
                },
                "requestDate":"Nov 30, 2021 12:34:10 PM"
                }''' % postcode
            headers = {'Content-Type': 'application/json; charset=utf-8'}
            response = requests.post(url, data=data, headers=headers)
            result = response.json()

            df = pd.json_normalize(result['onlyGas'])[['supplierName', 'productUrlEn', 'price', 'variability', 'contractDuration', 'productNameEn', 'conditions']]
            df['postcode'] = postcode
            df['conditions'] = df['conditions'].apply(flatten_json)
            df['price'] = df['price'].div(34890).round(4)
            df.sort_values(by=['price'], inplace=True, ascending=True)

            df.rename(columns={'supplierName': 'supplier', 'productUrlEn': 'supplier_url', 'variability': 'type', 'contractDuration': 'duration', 'productNameEn': 'product', 'postcode':'postal_code'}, inplace=True)
            df.loc[df['type'] == 'fixed'].head(10).to_sql('gas_offer', con=engine, if_exists='append', index=False)

        except Exception as e:
            print(e+ " " + postcode)
            continue