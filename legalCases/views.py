from django.shortcuts import get_object_or_404, render
import tempfile
# Create your views here.
from django.http import HttpResponse, FileResponse, HttpResponseNotFound

from django.core.files.storage import FileSystemStorage
from .models import *
import PyPDF2
from django.core.files.base import ContentFile
import contractions
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
from num2words import num2words
from spellchecker import SpellChecker
import spacy
import io
import os
import zipfile
# import StringIO
from legalsystem import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import JsonResponse
from .utils import NLP_Processing, nest_sentences, summerize, summerize_doc, NER, Keywords, query, score, score1
import pandas as pd
from .models import judgements
import json
from django.contrib.auth.decorators import login_required

# @login_required(login_url="/accounts/signin")
def summarySearch(request):
     print(request.user.id)
     if request.method == 'POST':
            summary = request.POST.get('summary')
            print("print",summary)
            print(request.POST)
            keywords = Keywords(summary)
            print(keywords)
            df = pd.DataFrame(columns=['names','keywords'])
            print("ehhlo")
            names = []
            keywords_list = []
            summary_list = dict()

            for i in judgements.objects.all():
                if str(i.filename).count('.PDF') >0:
                    names.append(str(i.filename).replace('.PDF',''))
                else:
                    names.append(str(i.filename))
                     
                     
                keywords_list.append(i.keywords.split(","))
                file = i.summary_path.open('r')
                summary_list[names[-1]] = file.read()
                file.close()
                print("#$"*10)
                # df = pd.concat([df, pd.DataFrame({'names':i.filename,'keywords':i.keywords.split(',')})])
            # df['names'] = names
            # df['keywords'] = keywords_list
            # print(list(df['names']))
            # print(list(df['keywords']))
            print("55",names)
            scores=dict()
            for i in range(len(keywords_list)):
                scor = score1(keywords,keywords_list[i])
                print("59",scor)
                print(names[i])
                scores[names[i]] = scor
            print("60",scores)
            scores = sorted(scores.items(), key=lambda x:x[1], reverse=True)
            scores = dict(scores)
            print(scores)
            summ = []
            for i in list(scores.keys())[:20]:
                 print(i)
                 summ.append(summary_list[i])
            print("65,  summ",summ)
            xdc = NLP_Processing(summary,summ)
            print(xdc)
            for i,j in zip(list(scores.keys())[:20],xdc[0]):
                scores[i] = j * 100
                 
            print("#"*12)
            print(xdc)
            
            # df['scores'] = scores
            # df = df.sort_values(by=['scores'])
            # print(df)
            scores = sorted(scores.items(), key=lambda x:x[1], reverse=True)
            scores = dict(scores)
            print(scores)
            print("&"*29)
            # print(list(summary_list))
            return JsonResponse({"data": scores},safe=False)

@login_required(login_url="/accounts/signin")
def index(request):
    if request.method == 'POST':
        print(request.POST)
        query_df = pd.DataFrame(columns= ['source'])
        kg_df = pd.read_csv('media/kg_df.csv')
        labels = list(kg_df['relation'].value_counts().index)
        input_labels =[]
        input_values =[]
        for i in request.POST:
            # print(request.POST.getlist(i))
            var_lst = request.POST.getlist(i)
            for var in var_lst:
                if var != 'none': 
                    input_values.append(var)
                    input_labels.append(str(i).replace('[]',''))
        print(input_values)
        print(input_labels)
        for i in range(len(input_values)):
            query_df = query(input_labels[i],input_values[i] ,kg_df , query_df)
        print((query_df.columns))
        query_df = score(query_df)
        query_df.sort_values(by='score', ascending=False,inplace=True)
        queries = {}
        for file,score1 in zip(query_df['source'],query_df['score']):
             queries[file]=score1
        
        print(queries)
        return JsonResponse({"data": queries},safe=False)



    kg_df = pd.read_csv('media/kg_df.csv')
    ner = dict()
    for i in list(kg_df['relation'].value_counts().index):
                ner[i] = list(kg_df[kg_df['relation']==i]['target'])
    # print(ner)
    return render(request , 'dashboard/dashboard.html',{"NER":ner})

def download_zip(request):
    print(request.POST)
    print("Heelo")
    byte_data = io.BytesIO()
    # response = HttpResponse(content_type='application/zip')
    zip_file = zipfile.ZipFile(byte_data, 'w')
    print("143",request.POST.getlist('judegments[]'))
    for file in request.POST.getlist('judegments[]'):
        print("file:-",file)
        filename = os.path.join(settings.MEDIA_ROOT, 'judgment/{}.pdf'.format(file))
        print(filename)
        zip_file.write(filename)
        # pdfFileObj =io.BytesIO(  open(os.path.join(settings.MEDIA_ROOT, 'media/judgment/{}.pdf'.format(file)), 'rb').read())

    zip_file.close()
    response = HttpResponse(byte_data.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=files.zip'

    # Print list files in zip_file
    zip_file.printdir()
    return response

def pdf_view(request,document):
    print("download")
    fs = FileSystemStorage()
    filename = os.path.join(settings.MEDIA_ROOT, 'judgment/{}'.format(document+'.pdf'))
    
    if fs.exists(filename):
        with fs.open(filename) as pdf:
            print(pdf)
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(pdf.name) #user will be prompted with the browser’s open/save file
            # response['Content-Disposition'] = 'inline; filename="mypdf.pdf"' #user will be prompted display the PDF in the browser
            # FileResponse(open(os.path.join(settings.MEDIA_ROOT, 'judgment/4_Whether_This_Case_Involves_A_vs_State_Of_Gujarat_on_28_April_2017.PDF.pdf'), 'rb'),content_type="application/pdf")
            return response
    else:
        return HttpResponseNotFound('The requested pdf was not found in our server.')
    
def download(request, document_id):
    print("151",document_id)
    if str(document_id).count('.PDF') == 0:
        document = get_object_or_404(judgements, filename=document_id+".PDF")
        response = HttpResponse(document.judgment_path, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{document.judgment_path.name}"'
        return response
    
    document = get_object_or_404(judgements, filename=document_id)
    response = HttpResponse(document.judgment_path, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{document_id}"'
    return response

@login_required(login_url="/accounts/signin")
def make_summary(request):

    if request.method == 'POST':
        # files = os.listdir(os.path.join(settings.MEDIA_ROOT,"temp"))
        # for file in files:
        # pdfFileObj =io.BytesIO(  open(os.path.join(settings.MEDIA_ROOT, 'temp/{}'.format(file)), 'rb').read())
        if judgements.objects.filter(filename=request.FILES['judgement'].name).exists():
            
            return JsonResponse({"summary": "None","NER":"None"},safe=False)

        dict_names = {}
        data_source = []
        names = []
        # print(file)
        pdfFileObj = request.FILES['judgement'].open()
        print("filename", request.FILES['judgement'].name)
        pdfReader = PyPDF2.PdfReader(pdfFileObj)
        NumPages = len(pdfReader.pages)
        print("num pages",NumPages)
        i = 0
        text1 = []
        abs_summ=""

        for page in pdfReader.pages:
                lines = page.extract_text().split("\n")
                newline = []
                for line in lines[:len(lines)-1]:
                    words = [w.strip() for w in line.split()]
                    words = [w.lower() for w in words]
                    newline.append(" ".join(words))
                text1.append("\n".join(newline))

        data_source.append("\n".join(text1))
        names.append(request.FILES['judgement'].name)
        # names.append(file)
        
        dict_names[names[-1]] = len(data_source[-1])*(40/100)
        print(data_source)
        print("&&&"*10)
        print(names)
        print("&&&"*10)
        print(len(data_source[-1]))
        print(dict_names)
        print("&&&"*10)
        ner = dict()

        for i in range(len(data_source)):   
            name = names[i]
            doc = data_source[i]
            input_len = len(doc.split(" "))
            req_len = 560
            print(str(i) + ": " + name +  " - " + str(input_len) + " : " + str(req_len), end = ", ")
            print(doc)
            nested = nest_sentences(doc,512)
            
            p = float(req_len/input_len)
            print("p-> ",p)
            abs_summ = summerize_doc(nested,p)
            print("abs-summ",abs_summ)
            abs_summ = " ".join(abs_summ)
            print(len((abs_summ.split(" "))))
            
            if len(abs_summ.split(" ")) > req_len:
                abs_summ = abs_summ.split(" ")
                abs_summ = abs_summ[:req_len]
                abs_summ = " ".join(abs_summ)
            print(abs_summ)
            in_memory_file = io.StringIO()
            in_memory_file.write(abs_summ)
            in_memory_file.filename = name+".txt"
            in_memory_file.seek(0)
        
            keywords = ",".join(Keywords(abs_summ))
            file = InMemoryUploadedFile(in_memory_file, "text", "{}.txt".format(name), None, in_memory_file.tell(), None)
            pdffile =InMemoryUploadedFile(pdfFileObj, "text", "{}.pdf".format(name), None, pdfFileObj.tell(), None)
            kg_df = pd.read_csv('media/kg_df.csv')
            # print(kg_df)
            kg_df1 = NER(data_source[-1],names[-1])

            kg_df = pd.concat([kg_df ,kg_df1])
            kg_df = kg_df.drop_duplicates()
            kg_df.to_csv('media/kg_df.csv')
            judgements.objects.create(filename=names[-1],judgment_path=pdffile,summary_path=file,keywords=keywords)
        

        for i in list(kg_df1['relation'].value_counts().index):
            ner[i] = list(kg_df1[kg_df1['relation']==i]['target'])
        print(ner)
        # abs_summ =  """On March 17, 2023, the high court of Madhya Pradesh issued an order restraining the Chief Electoral Officer of Madhya Pradesh from taking any further action against the former Chief Minister of Madhya Pradesh, Shivraj Singh Chouhan, for allegedly violating the provisions of Section 164 of the Election Act, 2000. The order was issued after the Election Commission of India (ECI) 
        #            filed an application in the high court of Madhya Pradesh seeking an order restraining Chouhan from taking further action against the former Chief Minister. The ECI's application was filed on March 17, 2023. The high court issued an order restraining Chou The election petition filed by the election petitioner alleges that the returned candidate has suppressed the aforesaid facts by not disclosing
        #              same which amounts to fraud and corrupt practice and the aforesaid election be declared as null and void. The election petition also alleges that the returned candidate has not disclosed any information or particulars regarding registration of fir which amounts to fraud and corrupt practice as mandate by provisions of the act of 1951. The election petition filed by election petitioner deserves to be dismissed on this preliminary
        #                objection raised by respondent no.1 that mere non-disclosure of information or particulars regarding registration of fir amounts to fraud and corrupt practice as mandate by provisions of the On March 3, 2023, the Election Commission of India (ECI) issued an order suspending the registration of the election petition filed by the candidate for the election to the state legislature of Madhya Pradesh. 
        #                The ECI's order came after a petition filed by the candidate for the election to the state legislature of Madhya Pradesh seeking suspension of the registration of the election petition filed by the candidate for the election to the state legislature of Madhya Pradesh. The petition alleges that the candidate has deliberately denied the fact on oath or affidavit mentioning that he has no knowledge about the registration of the election petition. The petition further alleges that the election 
        #                petition is The Election Commission of India (ECI) has issued a notice to the Chief Electoral Officer (CEO) of the State Election Commission (SEC) seeking explanation as to why the Chief Electoral Officer (CEO) of the State Election Commission (SEC) did not take action against Govind singh, the Chief Electoral Officer (CEO) of the State Election Commission (SEC) for failing to disclose his criminal antecedents. The SEC has issued a notice to the Chief Electoral Officer (CEO) of the State Election Commission (SEC) seeking explanation as to why the Chief Electoral On March 17, 2023, the Election Commission of India (ECI) issued a notice to the Chief Electoral Officer (CEO)
        #                  of the State of Madhya Pradesh for alleged forgery of nomination form of Govind singh, candidate for the forthcoming general election for the post of Deputy Chief Minister of Madhya Pradesh. The ECI issued the notice after an objection was raised by Mr. Dig"""
        # ner= {"PROVISION": ["section 190,or section 200", "section 190,,,or section 200", "section 41 a of crpc", "sections 465, 468, 469, 471, 472,,474 , 120 b", "sections 465, 468, 469, 471, 472,,474 , 120 b", "sections 465, 468, 469, 471, 472,,474 , 120 b", "sections 465, 468, 469, 471, 472,,474 , 120 b", "sections 465, 468, 469, 471, 472,,474 , 120 b", "sections 465, 468, 469, 471, 472,,474 , 120 b", "sections 465, 468, 469, 471, 472,,474 , 120 b", "section,100(10", "rule 4a", "section 340", "sections 193, 200 , 463", "sections 193, 200 , 463", "sections 193, 200 , 463"], "LAWYER": ["anoop george chaudhary", "kuber boddh", "manas dubey", "govind singh", "naman nagrath", "soumya\npawaiya", "karan virwani", "sumer singh solanki", "sanjay shukla", "digvijay singh", "mahendra barik", "govind\nsingh"], "DATE": ["01-03-2023", "17 march, 2023", "27-01-2023", "27-01-2023", "27-01-2023:-", "27.9.2018", "03-03-2023", "16-03-2020", "5th april, 2023", "17 march, 2023", "3/20/2023", "17 march, 2023"], "PRECEDENT": ["govind singh vs mr. jyotiraditya m. scindia", "baban singh & another vs. jagdish singh & others, 1966 3 scr 552", "govind singh vs mr. jyotiraditya m. scindia", "govind singh vs mr. jyotiraditya m. scindia", "govind singh vs mr. jyotiraditya m. scindia"], "OTHER_PERSON": ["mahendra barik", "mahendra barik", "mahendra barik", "digvijay singh", "mahendra barik"], "PETITIONER": ["govind singh", "govind singh", "govind singh", "govind singh"], "RESPONDENT": ["jyotiraditya m. scindia", "jyotiraditya m. scindia", "jyotiraditya", "jyotiraditya"], "COURT": ["high court of madhya pradesh\nat gwalior", "apex court"], "JUDGE": ["mahendra barik", "deepak kumar agarwal"], "WITNESS": ["mahendra barik"]}
        
        return JsonResponse({"summary": abs_summ,"NER":ner},safe=False)
        # return JsonResponse({"staus":"save"},safe=False)
    return render(request, 'judgement-summary.html')

@login_required(login_url="/accounts/signin")
def CreateFolder(request):
    if SearchFolders.objects.filter(title=request.POST.get('title')).exists():
        return JsonResponse({"msg":"Try Unique Title","is_valid":True},safe=False)
         
    xx=  SearchFolders.objects.create(title=request.POST.get('title'),user_id=request.user)
    # tt = SearchFolders.objects.get(title="as")
    for i in request.POST.getlist('judegments[]'):
        SearchJudgement.objects.create(searchfolders_id=xx,judgements_id=judgements.objects.get(filename=i))
    return JsonResponse({"msg":"Success"},safe=False)

def get_pdfs(request,title):
     
    if request.method == "GET":
        xd = SearchFolders.objects.get(title=title)
        data = SearchJudgement.objects.filter(searchfolders_id=xd).values_list('judgements_id__filename',flat=True)
        print(data)
        return JsonResponse({"data":list(data)},safe=False)
    elif request.method == "DELETE":
        print("Hello")
        SearchFolders.objects.get(title=title).delete()
        return JsonResponse({"data":"Deleted"},safe=False)
    
@login_required(login_url="/accounts/signin")   
def getHistory(request):
    datas = []
    # data = SearchFolders.objects.filter(user_id=request.user).values()
    # print(data)

    for folder in SearchFolders.objects.filter(user_id=request.user):
         datas.append({'title':folder.title,'start_time':folder.start_time,'last_modify':folder.last_modify,'count':len(SearchJudgement.objects.filter(searchfolders_id=folder))})
        #  print(list(SearchJudgement.objects.filter(searchfolders_id=folder).values_list('judgements_id__filename', flat=True)))
    return render(request , 'user-history.html',{"data":datas})
     

# def download(request):
#     if request.method == "GET":
#         print(request)
#         if str(document_id).count('.PDF') == 0:
#             document = get_object_or_404(judgements, filename=document_id+".PDF")
#             response = HttpResponse(document.judgment_path, content_type='application/pdf')
#             response['Content-Disposition'] = f'attachment; filename="{document.judgment_path.name}"'
#             return response
        
#         document = get_object_or_404(judgements, filename=document_id)
#         response = HttpResponse(document.judgment_path, content_type='application/pdf')
#         response['Content-Disposition'] = f'attachment; filename="{document_id}"'
#         return response
