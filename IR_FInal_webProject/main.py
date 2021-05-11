
from flask import Flask,render_template,request
app = Flask(__name__)
import re, os, sys, nltk
import xml.etree.cElementTree as et
import pickle, base64, time
from heapq import *
import math, operator, json, copy
from autocorrect import Speller
spell = Speller()
basePath = '/Users/union/androidandpy/PycharmProjects/IR_FInal_webProject/reso/'

stemmer = nltk.stem.SnowballStemmer('english')
stop_words = {}
stop_file = open(basePath + "stop_words.txt", "r")
words = stop_file.read()
words = words.split(",")
for word in words:
    word = word.strip()
    if word:
        stop_words[word[1:-1]] = 1
#print(stop_words)
fields = {}
fields["t"] = open(basePath + "title_output.txt","r")
fields["c"] = open(basePath + "category_output.txt","r")
fields["i"] = open(basePath + "infobox_output.txt","r")
fields["b"] = open(basePath + "body_text_output.txt","r")

words_position = {}
with open(basePath + "word_position.json",'r') as f:
    words_position = json.load(f)

title_position = pickle.load(open(basePath + "title_position.pickle", "rb"))
titles = open(basePath + "titles.txt",'r')
results = 10

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/result", methods = ['POST'])
def result():

    res = request.form.get('search')
    query = res
    query_result = []
    start = time.time()
    result_doc = {}
    if ":" in query:
        query_fields = query.split(" ")
        for queries in query_fields:
            field, query = queries.split(":")
            query = spell(query)
            print("Field Query after auto correction: ", query)
            if field == "ref" or field == "ext" or field == "body":
                field = "b"
            elif field == "title":
                field = "t"
            elif field == "category":
                field = "c"
            elif field == "infobox":
                field = "i"
            words = query.split(" ")
            for word in words:
                word = stemmer.stem(word)
                if word and word not in stop_words:
                    if word in words_position and field in words_position[word]:
                        docs = []
                        pointer = words_position[word][field]
                        fields[field].seek(pointer)
                        posting_list = fields[field].readline()[:-1]
                        posting_list = posting_list.split(",")
                        for doc in posting_list:
                            print(doc)
                            doc_no, score = doc.split(":")
                            if doc_no not in result_doc:
                                result_doc[doc_no] = 0
                            result_doc[doc_no] += float(score)
    else:
        query = spell(query)
        print("Normal Query after auto-correction: ", query)
        query_words = query.split(" ")
        for word in query_words:
            word = word.strip()
            word = stemmer.stem(word)
            if word not in stop_words:
                if word in words_position:
                    docs = []
                    for field in words_position[word].keys():
                        pointer = words_position[word][field]
                        print(field)
                        fields[field].seek(pointer)
                        posting_list = fields[field].readline()[: -1]
                        posting_list = posting_list.split(",")
                        for doc in posting_list:
                            doc_no, score = doc.split(":")
                            if doc_no not in result_doc:
                                result_doc[doc_no] = 0
                            result_doc[doc_no] += float(score)

    count = 1
    result_doc = sorted(result_doc.items(), key=operator.itemgetter(1), reverse=True)
    for document in result_doc:

        position = title_position[int(document[0]) - 1]
        titles.seek(position)
        query_result.append(titles.readline()[: -1])
        if count >= results:
            break
        count += 1

    end = time.time()
    print("Time Taken :- ", (end - start))
    time_taken = end - start
    len_query = len(query_result)
    if len(query_result) == 0:
        print("No result found")
    else:
        print("Number of Results :- ", len(query_result))
        for result in query_result:
            print(result)


    return render_template('index.html', res = res,query_result = query_result,time_taken = time_taken,len_query = len_query,query = query)
app.run(debug = True)