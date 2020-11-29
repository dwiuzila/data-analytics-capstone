from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
plt.style.use('seaborn-whitegrid')
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.exchange-rates.org/history/IDR/USD/T')
soup = BeautifulSoup(url_get.content,"html.parser")

tbody = soup.find(
    'table', 
    attrs={'class':'table table-striped table-hover table-hover-solid-row table-simple history-data'}
)
tr = tbody.find_all('tr')
temp = [] #initiating a tuple

for i in range(len(tr)):
    row = tbody.find_all('tr')[i]
    
    #get date
    period = row.find_all('td')[0].text
    period = period.strip() #for removing the excess whitespace
    
    #get exchange rate
    ex_rate = row.find_all('td')[2].text
    ex_rate = ex_rate.strip() #for removing the excess whitespace
    
    temp.append((period,ex_rate))

temp = temp[::-1]

#change into dataframe
df = pd.DataFrame(temp, columns=['date', 'exchange_rate'])

#insert data wrangling here
df['date'] = df['date'].astype('datetime64')
df['exchange_rate'] = df['exchange_rate'].apply(lambda x : x.split(' ')[0])
df['exchange_rate'] = df['exchange_rate'].str.replace(',', '')
df['exchange_rate'] = df['exchange_rate'].astype(float)

#end of data wranggling 

@app.route("/")
def index(): 
	
	min_rate = f"IDR {df['exchange_rate'].min().round(2)}"
	avg_rate = f"IDR {df['exchange_rate'].mean().round(2)}"
	max_rate = f"IDR {df['exchange_rate'].max().round(2)}"

	# generate plot
	ax = df.set_index('date').plot(figsize = (15,6))
	ax.legend().remove()
	plt.ylabel('Exchange Rate ( IDR / USD )')
	plt.xlabel('Date')
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]


	# render to html
	return render_template('index.html',
		min_rate = min_rate, 
		avg_rate = avg_rate,
		max_rate = max_rate,
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)
