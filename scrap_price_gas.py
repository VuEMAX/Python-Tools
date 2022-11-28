import brugel_gas
import cwape_gas
import vreg_gas
import sqlalchemy as db

engine = db.create_engine('mysql://root:root_emax@localhost:3306/kyla_pub', echo=False)
conn = engine.connect()
metadata = db.MetaData()

# delete offer in test db
def clean_old_offer():
    offer = db.Table('gas_offer', metadata, autoload=True, autoload_with=engine)
    delete_query = offer.delete()
    conn.execute(delete_query)
    alter_seq_query = "ALTER TABLE gas_offer AUTO_INCREMENT = 1"
    conn.execute(alter_seq_query)

# export offer in test db
def export_offer():
    offer = db.Table('gas_offer', metadata, autoload=True, autoload_with=engine)

# import offer in prod db

def main():
    clean_old_offer()

    # call brugel
    brugel_gas.insert_data()

    # call cwape
    cwape_gas.insert_data()

    # call vreg
    vreg_gas.insert_data()

if __name__ == "__main__":
    main()