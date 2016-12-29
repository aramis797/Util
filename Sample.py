from bs4 import BeautifulSoup
import urllib2
opener = urllib2.build_opener()
opener.addheaders = [('User-agent','Mozilla/5.0 (X11; Ubuntu; Linux i686 on x86_64; rv:45.0) Gecko/20100101 Firefox/45.0')]


class Product:
	def __init__(self,upc,title,price,fuzzyScore = 0):
		self.upc = upc
		self.title = title
		self.price = price
		self.fuzzyScore = fuzzyScore
	def __str__(self):
		# return "Product Details:--\n---------------------\nUPC :- %s\nTitle :- %s\nPrice :- %s\nFuzzy Score :- %s"%(self.upc,self.title,self.price,self.fuzzyScore)
		return "(%s,%s,%s,%s)"%(self.upc,self.title,self.price,self.fuzzyScore)
def getAmazonPrices(upc):
	# amazon_url = "https://www.amazon.com/gp/aw/s/ref=is_box_?k=083000161582"
	#upc="892201002330"
	#a-fixed-left-grid-inner
	amazon_url = "https://www.amazon.com/s/ref=nb_sb_noss/161-5363731-5917166?url=search-alias%3Daps&field-keywords="+upc
	page = opener.open(amazon_url).read()
	soup = BeautifulSoup(page,'html.parser')
	#prices = soup.findAll("span",{'class':'a-size-base a-color-price s-price a-text-bold'})
	# for i in prices:
	# 	print i.text
	#1- innergrids:- 
	innerGrids = soup.findAll("div",{"class":"a-fixed-left-grid-inner"})
	# print len(innerGrids)
	productDict = {}
	for innerGrid in innerGrids:
		title =  innerGrid.findAll("h2")[0]['data-attribute']
		# title = innerGrid.findAll("h2",{'class':'a-size-medium a-color-null s-inline  s-access-title  a-text-normal'})
		# for some products price is not available in resuls page, we need to open that product then only we can see it's price. so assigning it's price as None
		price = None
		try:
			price = float(innerGrid.findAll("span",{'class':'sx-price-whole'})[0].text.strip('$'))
			print price
		except:
			pass
		if price:
			if title.lower() not in productDict:
				productDict[title.lower()] = Product(upc,title.lower(),[price])
			else:
				productDict[title.lower()].price.append(price)
	# print len(priceDict)
	# To remove products whose prices are None
	return productDict

otcProduct = Product("083000161582","Natures Answer Cranberry single herb supplement vegetarian capsules - 90 ea",8.78)

out = getAmazonPrices(otcProduct.upc)
print out