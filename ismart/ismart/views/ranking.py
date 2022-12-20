from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import requests
import json
import threading
import re
import spacy
from datetime import date
from operator import itemgetter

todays_date = date.today()
sp = spacy.load('en_core_web_sm')

@api_view(['GET'])
def ranking(request):
    keywords = request.GET.get('keywords')
    recent = request.GET.get('recent')
    c_weight = request.GET.get('citation_weight')
    if keywords is None:
        return HttpResponse("Enter valid keywords")
    researchPapers = papers(keywords)
    articles = []
    for paper in researchPapers:
        dict = {}
        
        authors = paper['authors']
        numberOfAuthors = len(authors)
        author_score = 0

        score1 = None
        score2 = None

        if recent and ((todays_date.year - paper['year']) < 5):
            score2 = 3.25
        else:
            score2 = 0
        
        if c_weight and ((paper['citationCount'] / (todays_date.year - paper['year']))>150):
            score1 = 3.25*((paper['citationCount'] / (todays_date.year - paper['year']))/150)
        else:
            score1 = 0

        if(numberOfAuthors == 0):
            author_score = 0
        else:
            if 'authorId' in authors[0]:
                author_score = (authorScore(keywords,authors[0]['authorId']))
        # elif(numberOfAuthors == 1):
        
        # else:
        #     if 'authorId' in authors[0] and 'authorId' in authors[1]:
        #         author_score = ((authorScore(keywords,authors[0]['authorId'])) + (authorScore(keywords,authors[1]['authorId']))) / 2
        
        authorsList = authorList(paper)
        try:
            dict['title'] = paper['title']
        except:
            dict['title'] = " "
        try:
             dict['pdf_url'] = paper['url']
        except:
             dict['pdf_url'] = " "
        try:
            dict['abstract'] = (paper['abstract']).replace("Abstract","")
        except:
            dict['abstract'] = " "
        try:
            dict['publication_year'] = paper['year']
        except:
            dict['publication_year'] = " "
        try:
            dict['citing_paper_count'] = paper['citationCount']
        except:
            dict['citing_paper_count'] = " "
        try:
            dict['influenceScore'] = paper['influentialCitationCount']
        except:
            dict['influenceScore'] = " "
        try:
            dict['auhtorScore'] = str(author_score)
        except:
            dict['auhtorScore'] = " "
        try:
            dict['paperScore'] = (author_score + citation_per_year(paper) + score1 + score2)
        except:
            dict['paperScore'] = 0
        try:
            dict['publication_date'] = paper['publicationDate']
        except:
            dict['publication_date'] = " "

        dict['publisher'] = " "
        
        try:
            dict['journal'] = paper['journal']['name']
        except:
            dict['journal'] = " "
        try:
            dict['authors'] = {"authors" : authorsList}
        except:
            dict['authors'] = {"authors" : []}
        
        articles.append(dict)
        
    articles = sorted(articles, key=itemgetter('paperScore'), reverse=True)
    return JsonResponse({"articles" : articles})

def citations_per_paper_score(citations, number_of_papers):
    
    citations = int(citations)
    number_of_papers = int(number_of_papers)
    
    citations_per_paper = citations / number_of_papers
    if citations_per_paper < 5 :
        return 0.03 * citations_per_paper
    else :
        return 0.15
    
def publications_per_year_score(publication, exp):
    
    publication = int(publication)
    exp = int(exp)
    
    publications_per_year = publication / (exp)
    if publications_per_year < 3:
        return 0.15 * publications_per_year / 2
    elif publications_per_year < 6:
        return 0.15 * (6 - publications_per_year) / 2
    else:
        return 0
    
def experience(data):
    
    end_year = 0
    start_year = 3000
    try : 
        
        for paper in data['papers']:
            if(paper['year'] > end_year):
                end_year = paper['year']
            if(paper['year'] < start_year):
                start_year = paper['year']

        exp = end_year - start_year + 1
        return exp
    except:
        return 1
    
def experience_score(start_year, end_year):
    time_duration = end_year - start_year + 1
    if time_duration < 16:
        return 0.15 * time_duration / 15
    else:
        return 0.15
    
def check_topic_relevance(keywords, data):
    score = 0
    for papers in data['papers']:
        for publication_topics in papers['title']:
            text_tokens = list(keywords)
            publication_topics = list(publication_topics)
            all_stopwords = sp.Defaults.stop_words
            tokens_without_stopwords = [word for word in text_tokens if not word in all_stopwords]
            relevant_topics = [word for word in tokens_without_stopwords for topic in publication_topics if topic == word]
            if len(relevant_topics) == len(tokens_without_stopwords):
                score += 0.02
            else:
                score += 0.02 * len(relevant_topics) / len(tokens_without_stopwords)
    
    return score/50

def hIndex(data):
    return data['hIndex']/30
    
def authorJson(authorId):
    URL = "https://api.semanticscholar.org/graph/v1/author/" + (authorId) + "?fields=url,name,affiliations,paperCount,citationCount,hIndex,papers.title,papers.year"
    data = (requests.get(url = URL )).json()
    return data
    
def authorScore(keywords,authorId):
    
    data = authorJson(authorId)
    exp = experience(data)
    ppy_score = publications_per_year_score(str(data['paperCount']),str(exp))
    cpp_score = citations_per_paper_score(str(data['citationCount']),str(data['paperCount']))
    ctr_score = check_topic_relevance(keywords,data)
    hi_score = hIndex(data)
    
    authorScore = ppy_score + cpp_score + ctr_score + hi_score

    return authorScore

def influential_citation_count(paper):
    score = paper['influentialCitationCount']
    if(score < 50):
        return score/250
    else:
        return 0.5
    
def authorList(paper):
    authors = paper['authors']
    authorList = []
    max = 0
    i = 1;
    for author in authors:
        if(max < 2):
            dict = {}
            data = authorJson(author['authorId'])
            try:
                dict['affiliation'] = data['affiliations'][0]
            except:
                dict['affiliation'] = " "
            dict['authorUrl'] = data['url']
            dict['id'] = data['authorId']
            dict['full_name'] = data['name']
            dict['author_order'] = i
            dict['citations'] = data['citationCount']
            dict['paperCount'] = data['paperCount']
            dict['hIndex'] = data['hIndex']
            i = i + 1
            authorList.append(dict)
            max += 1
    
    return authorList
    
    
def citation_per_year(paper):
    score = (paper['citationCount'] / (todays_date.year - paper['year']))
    if(score < 50):
        return score/250
    else:
        return 0.5
    
def papers(keywords):
    tokens = keywords.split(" ")
    tokenString = '+'.join(tokens)
    URL = "https://api.semanticscholar.org/graph/v1/paper/search?query=" + tokenString + "&offset=10&limit=5&fields=title,url,authors,abstract,year,referenceCount,citationCount,influentialCitationCount,journal,publicationDate"
    return ((requests.get(url = URL )).json()['data'])
