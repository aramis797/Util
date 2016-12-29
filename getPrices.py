from difflib import SequenceMatcher as SM
import operator
import urllib2
from fuzzywuzzy import fuzz
from bs4 import BeautifulSoup
#from openpyxl import Workbook,load_workbook

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
# input_file_path = "upc_sample.xlsx"
# inputWorkbook = load_workbook(input_file_path)

def getAmazonPrices(upc):
	amazon_url = "https://www.amazon.com/s/ref=nb_sb_noss/161-5363731-5917166?url=search-alias%3Daps&field-keywords="+upc
	page = opener.open(amazon_url).read()
	soup = BeautifulSoup(page,'html.parser')
	innerGrids = soup.findAll("div",{"class":"a-fixed-left-grid-inner"})
	# print len(innerGrids)
	productDict = {}
	for innerGrid in innerGrids:
		title =  innerGrid.findAll("h2")[0]['data-attribute']
		# title = innerGrid.findAll("h2",{'class':'a-size-medium a-color-null s-inline  s-access-title  a-text-normal'})
		# for some products price is not available in resuls page, we need to open that product then only we can see it's price. so assigning it's price as None
		price = None
		try:
			# price = float(innerGrid.findAll("span",{'class':'a-size-base a-color-price s-price a-text-bold'})[0].text.strip('$'))
			price = float(innerGrid.findAll("span",{'class':'sx-price-whole'})[0].text.strip('$'))
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

#FilterOne - assigns a fuzzy ratio for every item in dictionary. high values means more identical
def fuzzyFilter(otcTitle,productDict):
	for otherStoreTitle in productDict.keys():
		productDict[otherStoreTitle].fuzzyScore = fuzz.token_set_ratio(otcTitle,otherStoreTitle)

#FilterTwo - if there are more prices corresponding to one title then choose one which is closer to our price
def takeOnePriceFilter(otcProduct,productDict):
	for title in productDict.keys():
		if len(productDict[title].price) > 1:		#if corresponding title has more than one price
			finalPrice = productDict[title].price[0]	#take first one as our result temporarily
			priceDiff = abs(otcProduct.price - productDict[title].price[0])	#calculate first title price difference
			for i in range(1,len(productDict[title].price)):	#loop through other prices
				if abs(otcProduct.price - productDict[title].price[i]) < priceDiff:	#compare with current price difference, it lesser then assign to difference
					priceDiff = abs(otcProduct.price - productDict[title].price[i])
			# print title,out[title]
			productDict[title].price = finalPrice	# overwrite list with single price value
		else:
			productDict[title].price = productDict[title].price[0]	#overwrite list with price

#FilterThree - if more than one titles have highest fuzzy score then take one which is closer to our price
def finalFilter(otcProduct,productDict):
	highScoreItems = [product for title,product in productDict.iteritems() if product.fuzzyScore == max(productDict.values(),key=lambda x:x.fuzzyScore).fuzzyScore]	# get all titles with maximum fuzzy ratio score
	if(len(highScoreItems) == 1):	# if only one item then return it
		return highScoreItems[0]
	else:	# if more than one item then get one which is closer to our price
		# return highScoreItems
		finalResult = Product(otcProduct.upc,highScoreItems[0].title,highScoreItems[0].price,highScoreItems[0].fuzzyScore)
		priceDiff = abs(finalResult.price - otcProduct.price)
		for highScoreItem in highScoreItems[1:]:
			if abs(highScoreItem.price - otcProduct.price) < priceDiff:
				finalResult.title = highScoreItem.title
				finalResult.price = highScoreItem.price
		return finalResult

# otcTitle = "Natures Answer Cranberry single herb supplement vegetarian capsules - 90 ea".lower()
otcProduct = Product("083000161582","Natures Answer Cranberry single herb supplement vegetarian capsules - 90 ea",8.78)
# otcProduct = Product("076970442317","Heritage Lavender flower water - 8 oz",7.70)
# otcProduct = Product("0822383531328","Drive Medical First Class School Chair Anti Tippers, Large - 1 Pair",27.68)
# otcProduct = Product("019200800884","Lysol deep reach toilet bowl cleaner - 24 oz/pack, 12 pack",28.04)
# otcProduct = Product("072140813598","Nivea for Men Deep Cleaning Face Scrub - 4.4 Oz",4.74)
# otcTitle = "Heritage Lavender flower water - 8 oz"
# otcTitle = "Health From The Sun Borage Oil 300 soft gels 1300mg - 60 ea" #$24.64
# otcTitle = "Hearos water protection ear plugs, Plus free case - 1 Pair" # $4.67
print "otc Title :: ",otcProduct.title,otcProduct.price
out = getAmazonPrices(otcProduct.upc)
for i in out.keys():
	print out[i]
# print "---------------------"
# print "Amazon Result:-"
# print "---------------------"
# for title in out.keys():
# 	print out[title]
# fuzzyFilter(otcProduct.title.lower(),out)
# print "---------------------"
# print "After fuzzyFilter:--"
# print "---------------------"
# for title in out.keys():
# 	print out[title]
# takeOnePriceFilter(otcProduct,out)
# print "---------------------"
# print "After takeOnePriceFilter:--"
# print "---------------------"
# for title in out.keys():
# 	print out[title]
# print "---------------------"
# print "After FinalFilter :--"
# print "---------------------"
# print finalFilter(otcProduct,out)
# print max(out.values(),key=lambda x:x[1])[1]
# for i in out.values():
# 	print i.fuzzyScore
# print max(out.values(),key=lambda x:x.fuzzyScore)