import pandas as pd
from bs4 import BeautifulSoup as bs
from requests import get
import subprocess
from pymongo import MongoClient

'''
df = pd.DataFrame()
for p in range(1, 5):
    url = f'https://sn.coinafrique.com/?page={p}'
    res = get(url)
    soup = bs(res.text, 'html.parser')
    info1 = soup.find_all('div', class_ = 'col s6 m4 l3')
    links = [a.find('a')['href'] for a in info1]
    links_con = ['https://sn.coinafrique.com' + link for link in links]
    data = []
    for x in links_con:
      res = get(x)
      soup = bs(res.text, 'html.parser')
      try:
        try:
          info3 = soup.find_all('div', class_ = 'ad__info')
          price_inf = soup.find('p', class_ = 'price').text
        except:
          price_inf = ''
        try:
          info4 = soup.find('h1', class_ = 'title title-ad hide-on-large-and-down')
          desc_inf =info4.text.strip()
        except:
          desc_inf = ''
        try:
          info5 = soup.find_all('span', class_ = 'valign-wrapper')
          time_p = info5[0].text
          location = info5[1].text
          product_t = info5[2].text
        except:
          time_p = ''
          location = ''
          product_t = ''
        try:
          info6 = soup.find_all('div', class_ ='isNew-option')
          inf_etat = info6[0].text
        except:
          inf_etat = ''
        try:
          info7 = soup.find_all('div', class_ ='delivery-option')
          livraison = info7[0].text.replace('Livraison ','')
        except:
          livraison = ''
        
        obj = {
            'Name': desc_inf,
            'Price': price_inf,
            'Time': time_p,
            'Location': location,
            'Product': product_t,
            'Etat': inf_etat,
            'Livraison': livraison
        }
        data.append(obj)
      except Exception as e:
        print(f"Error parsing page: {x}, {e}")
        continue
    print(f"Sample entry:", {p})
    DF = pd.DataFrame(data)
    df = pd.concat([df, DF])

df.to_csv('mydata.csv', index=False)
'''

df = pd.read_csv('/home/sabou/Documents/project1/coinmarket.csv', index_col=False)

#upload to hdfs
# Step 1: Copy file into container
subprocess.run(['docker', 'cp', '/home/sabou/Documents/project1/coinmarket.csv', 'hadoop-hdfs-namenode:/coinmarket.csv'])

# Step 2: Run HDFS put from inside the container
subprocess.run([
    'docker', 'exec', 'hadoop-hdfs-namenode', 
    'hdfs', 'dfs', '-mkdir', '-p', '/home/coinmarketdata'
])
subprocess.run([
    'docker', 'exec', 'hadoop-hdfs-namenode',
    'hdfs', 'dfs', '-put', '-f', '/coinmarket.csv', '/home/coinmarketdata/'
])

# Connect to MongoDB with authentication
try:
    # Replace these with your actual MongoDB credentials
    username = "user1"
    password = "user1"
    auth_db = "admin"
    
    # Connect to MongoDB with authentication
    client = MongoClient(f"mongodb://{username}:{password}@localhost:27017/?authSource={auth_db}")
    
    # Test the connection
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
    
    # Create/use database
    db = client['coinmarketdata']
    
    # Create collection
    collection = db['coinmarketdata']
    
    # Convert DataFrame to list of dictionaries and insert
    records = df.to_dict(orient='records')
    if records:
        collection.insert_many(records)
        print(f"Successfully inserted {len(records)} documents into MongoDB")
        
        # Print first 3 documents
        print("\nFirst 3 documents in the collection:")
        for doc in collection.find().limit(3):
            print(doc)
    else:
        print("No records to insert into MongoDB")
        
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
finally:
    if 'client' in locals():
        client.close()
