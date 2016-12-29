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
		return "Product Details:--\n---------------------\nUPC :- %s\nTitle :- %s\nPrice :- %s"%(self.upc,self.title,self.price)
		# print "Product Details:--\n"
		# print "---------------------"
		# print "UPC :- ", self.upc
		# print "Title :- ", self.title
		# print "Price :- ", self.price
# input_file_path = "upc_sample.xlsx"
# inputWorkbook = load_workbook(input_file_path)
def getJetPrices(upc):
	# container :: div - list-products-container
	jet_url = "https://jet.com/search?term="+upc
	page = opener.open(jet_url).read()
	soup = BeautifulSoup(page,'html.parser')
	container = soup.findAll("div",{'class':'list-grid list-products show-action'})
	print soup.prettify()
	# print len(container)
def getWalmartPrices(upc):
	walmart_url = "https://www.walmart.com/search/?query="+upc
	page = opener.open(walmart_url).read()
	soup = BeautifulSoup(page,'html.parser')
	tileContainers = soup.findAll("div",{'id':'tile-container'})
	priceDict={}
	for tileContainer in tileContainers:
		title = tileContainer.findAll("a",{'class':'js-product-title'})[0].text
		price = tileContainer.findAll("span",{'class':'price price-display'})[0].text
		if title.lower() not in priceDict:
			priceDict[title.lower()] = [[price],0]
		else:
			priceDict[title.lower()][0].append(price)
	return priceDict

import operator
import urllib2
from fuzzywuzzy import fuzz
from bs4 import BeautifulSoup
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
	priceDict = {}
	for innerGrid in innerGrids:
		title =  innerGrid.findAll("h2")[0]['data-attribute']
		# title = innerGrid.findAll("h2",{'class':'a-size-medium a-color-null s-inline  s-access-title  a-text-normal'})
		# for some products price is not available in resuls page, we need to open that product then only we can see it's price. so assigning it's price as None
		price = None
		try:
			price = float(innerGrid.findAll("span",{'class':'a-size-base a-color-price s-price a-text-bold'})[0].text.strip('$'))
		except:
			pass
		if price:
			if title.lower() not in priceDict:
				priceDict[title.lower()] = [[price],0]
			else:
				priceDict[title.lower()][0].append(price)
	# print len(priceDict)
	# To remove products whose prices are None
	return priceDict

def matchingFunction(otcTitle,outputDict):
	wordMatches = {}
	wordMatches["ea"] = ["ea","each","pack","count","tablets","items","tablet"]
	wordMatches["pack"] = ["pack","packet","packs","packets"]
	wordMatches["oz"] = ["oz","ounce","ounze","pounds"]
	for otherStoreTitle in outputDict.keys():
		otherStoreWords = otherStoreTitle.split()
		for ourTitleWord in [word.lower() for word in otcTitle.split()]:
			if ourTitleWord in otherStoreWords:
				# print ourTitleWord
				outputDict[otherStoreTitle][1] += 1

#difflib -> sequencematcher
def secondMatcher(otcTitle,outputDict):
	print "Sequence Matcher::"
	print "----------------------"
	for otherStoreTitle in outputDict.keys():
		print otherStoreTitle,SM(None,otcTitle,otherStoreTitle).ratio(),outputDict[otherStoreTitle]

#FilterOne - assigns a fuzzy ratio for every item in dictionary. high values means most relevent
def fuzzyFilter(otcTitle,outputDict):
	for otherStoreTitle in outputDict.keys():
		outputDict[otherStoreTitle][1] = fuzz.ratio(otcTitle,otherStoreTitle)
		# print otherStoreTitle,fuzz.ratio(otcTitle,otherStoreTitle),outputDict[otherStoreTitle]
def getJetPrices(upc):
	jet_url = "https://jet.com/search?term="+upc
	print jet_url
	page = opener.open(jet_url).read()
	soup = BeautifulSoup(page,'html.parser')
	priceDict = {}
	moduleProduct = soup.findAll("div",{"class":"list-products-container"})
	print moduleProduct
#if there are more prices corresponding to one title then choose one which is closer to our price
def takeOnePriceFilter(otcProduct,outputDict):
	for title in outputDict.keys():
		if len(outputDict[title][0]) > 1:		#if corresponding title has more than one price
			finalPrice = outputDict[title][0][0]	#take first one as our result temporarily
			priceDiff = abs(otcProduct.price - outputDict[title][0][0])	#calculate first title price difference
			for i in range(1,len(outputDict[title][0])):	#loop through other prices
				if abs(otcProduct.price - outputDict[title][0][i]) < priceDiff:	#compare with current price difference, it lesser then assign to difference
					priceDiff = abs(otcProduct.price - outputDict[title][0][i])
			# print title,out[title]
			outputDict[title][0] = finalPrice	# overwrite list with single price value
		else:
			outputDict[title][0] = outputDict[title][0][0]	#overwrite list with price
def finalFilter(otcProduct,outputDict):
	highScoreItems = [(title,val) for title,val in outputDict.iteritems() if val[1] == max(outputDict.values(),key=lambda x:x[1])[1]]	# get all titles with maximum fuzzy ratio score
	if(len(highScoreItems) == 1):	# if only one item then return it
		return highScoreItems[0]
	else:	# if more than one item then get one which is closer to our price
		# return highScoreItems
		print highScoreItems
		finalResult = Product(otcProduct.upc,highScoreItems[0][0][0],highScoreItems[0][1][0])
		priceDiff = abs(finalResult.price - otcProduct.price)
		for highScoreItem in highScoreItems[1:]:
			if abs(highScoreItem[1][0] - otcProduct.price) < priceDiff:
				finalResult.title = highScoreItem[0]
				finalResult.price = highScoreItem[1][0]
		return finalResult

# otcTitle = "Natures Answer Cranberry single herb supplement vegetarian capsules - 90 ea".lower()
otcProduct = Product("083000161582","Natures Answer Cranberry single herb supplement vegetarian capsules - 90 ea",8.78)
# otcProduct = Product("076970442317","Heritage Lavender flower water - 8 oz",7.70)
# otcTitle = "Heritage Lavender flower water - 8 oz"
# otcTitle = "Health From The Sun Borage Oil 300 soft gels 1300mg - 60 ea" #$24.64
# otcTitle = "Hearos water protection ear plugs, Plus free case - 1 Pair" # $4.67
print "otc Title :: ",otcProduct.title,otcProduct.price
out = getAmazonPrices(otcProduct.upc)
# print out
print "---------------------"
print "Amazon Result:-"
print "---------------------"
for title in out.keys():
	print title,out[title]
#fuzzyFilter(otcProduct.title.lower(),out)
print "---------------------"
print "After fuzzyFilter:--"
print "---------------------"
for title in out.keys():
	print title,out[title]
#takeOnePriceFilter(otcProduct,out)
print "---------------------"
print "After takeOnePriceFilter:--"
print "---------------------"
for title in out.keys():
	print title,out[title]
print "---------------------"
print "After FinalFilter :--"
print "---------------------"
#print finalFilter(otcProduct,out)
#print max(out.values(),key=lambda x:x[1])[1]