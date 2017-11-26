# -*- coding: UTF-8 -*-
import glob
import codecs
from collections import defaultdict
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from operator import itemgetter

client = language.LanguageServiceClient()

# Review to analyze
def getSentiment(text, hotelAttributes, attributeCount, hotelName, eachHotelAttribute):
    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT)

    # Detects the sentiment of the text
    sentiment_response = client.analyze_sentiment(document=document)
    entity = client.analyze_entity_sentiment(document=document)


    for i in entity.entities:
        if i.name not in eachHotelAttribute:
            eachHotelAttribute[i.name]=i.sentiment.score
        else:
            score = eachHotelAttribute.get(i.name)
            score+=i.sentiment.score
            score= score/2
            eachHotelAttribute[i.name] = score
        if i.name not in attributeCount:
            attributeCount[i.name]=1
        else:
            count = attributeCount.get(i.name)
            count+=1
            attributeCount[i.name]=count
    hotelAttributes[hotelName]=eachHotelAttribute
    return hotelAttributes , attributeCount , eachHotelAttribute


def generateAttribute(hotelAttributes,attributeCount):
    selectedAttributes = sorted(attributeCount.values(), reverse=True)
    selectedAttributes=selectedAttributes[:10]
    attrList=[]
    for attributeCnt in selectedAttributes:
        for k, v in attributeCount.iteritems():
            if v == attributeCnt:
                attrList.append(k)
                del attributeCount[k]
                break
    return attrList

def generateCSV(hotelAttributes , attrList, hotelName, hotelDetails):
    values=hotelName[:-4]
    print values
    for attr in attrList:
        if attr in hotelDetails:
            values=values + ',' + str(hotelDetails.get(attr))
        else:
            values=values + ',' + '0.0001'
    return values


if __name__ == '__main__':
    files = glob.glob('/Users/puneetkoul/Desktop/DBI/Project/Data/new-york/*.txt')
    hotelAttributes = {}
    attributeCount={}
    #print hotelAttributes
    hotelCount=1
    fileCount=1
    for eachFile in files:
        print "File "+ str(fileCount)
        fileCount+=1
        eachHotelAttribute={}
        hotelNames = eachFile.split('/')
        hotelName = hotelNames[len(hotelNames)-1]
        print hotelName
        f = open(eachFile,'r')
        review = f.readline()
        review=review[11:]
        review=review.strip()
        while review:
            review=review.decode("utf-8","ignore")
            hotelAttributes , attributeCount, eachHotelAttribute = getSentiment(review,hotelAttributes,attributeCount,hotelName, eachHotelAttribute)
            review=f.readline()
        if hotelCount == 1:
            attrList=generateAttribute(hotelAttributes,attributeCount)
            hotelCount+=1
        f.close()

    ## Writing to output File
    f = open('outputCSV.csv', 'w')
    firstLine = "Hotel Name"
    for attr in  attrList:
        firstLine = firstLine + ',' + attr
    print firstLine
    f.write(firstLine)
    f.write('\n')
    for k in hotelAttributes:
        values=generateCSV(hotelAttributes,attrList,k,hotelAttributes[k])
        print values
        f.write(values)
        f.write('\n')
    f.close()
