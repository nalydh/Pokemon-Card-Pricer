# Libraries used: 
# Requests
# BeautifulSoup4
# Plotly
# Pandas

from datetime import datetime
import requests
import pandas as pd
import plotly.express as px
from bs4 import BeautifulSoup

# Grab URL
url = 'https://www.ebay.com.au/sch/i.html?_from=R40&_trksid=p2334524.m570.l1313&_nkw=pokemon+sylveon+psa+10+212%2F203&_sacat=0&_odkw=pokemon+sylveon+psa+10212%2F203+&_osacat=0&LH_PrefLoc=1&LH_Complete=1&LH_Sold=1'

# requests accesses webpage
r = requests.get(url)

# Create bs4 object to parse the webpage in a tree structure
soup = BeautifulSoup(r.text, 'html.parser')

# find all html tags with the class that contains products
product_containers = soup.find_all(class_="s-item__wrapper clearfix")

# data structure (dictionary) to store product information
product_info = {
    'name': [],
    'link': [],
    'price': [],
    'date_sold': []
}

# loops through each product and extracts relevant data if listing name has all the keywords present
for product in product_containers:
    # extract name html tag if found
    name_tag = product.find(class_ = "s-item__title")
    if name_tag:
        name = name_tag.text
    else:
        name = "N/A"
    
    # extract link html tag if found
    link_tag = product.find(class_= "s-item__link", )
    if link_tag:
        link = link_tag.get('href')
    else:
        link = "N/A"

    # extract price html tag if found
    price_tag = product.find(class_= "s-item__price")
    if price_tag:
        price = price_tag.text.lstrip("AU $")
    else:
        price = "N/A"

    # extract date sold html tag if found
    date_sold_tag = product.find(class_= "s-item__caption--signal POSITIVE")
    if date_sold_tag:
        # strip irrelevant information -> e.g. 27 Oct 2024
        date_sold = date_sold_tag.text.lstrip("Sold ")
        # convert text string into datetime object
        # Output: 2024-10-27
        date_sold = datetime.strptime(date_sold, "%d %b %Y") 
    else:
        date_sold = "N/A"
    
    # keyword check + ensure only AU sales are included
    if "psa 10" in name.lower() and "sylveon" in name.lower() and "212/203" in name.lower() and not product.find(class_="s-item__location"):
        product_info['name'].append(name)
        product_info['link'].append(link)
        product_info['price'].append(price)
        product_info['date_sold'].append(date_sold)

# create a dataFrame to store the information. used to plot the data
df = pd.DataFrame((product_info))

# sort values by date_sold 
df = df.sort_values(by='date_sold')

# applies a lambda function that produces a clickable link that opens on a new tab
df['hyperlink'] = df.apply(
    lambda row: f'<a href="{row["link"]}" target="_blank" style="color: black";>{row["name"]}</a>',
    axis= 1
)

# removes the comma for every row to convert to a float
df['price'] = df['price'].str.replace(',', '').astype(float)


fig = px.line(df, x="date_sold", y="price", title="Price trend for Sylveon 212/198", markers=True, hover_name="hyperlink", labels={"date_sold": "Date Sold", "price":"Price"})

# Set the y-axis range: Start at 0, end slightly above max price
max_price = df['price'].max()
fig.update_layout(
    yaxis=dict(range=[0, max_price * 1.1],
               dtick=20.00,
               tickprefix="$",
               tickformat=".2f")  # Add 10% buffer above the max price
)

print(df)
fig.show()

# // TO DO:
# Sort dataframe for date sold
# Filter outliers
# calculate monthly change +/-
# change code for it to be more modular and extensible