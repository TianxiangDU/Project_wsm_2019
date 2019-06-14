from flask import Flask
from flask import request

import mysql.connector

# 连接database

conn = mysql.connector.connect(user='root', password='123456', database='baidu',charset='utf8mb4')

# 得到一个可以执行SQL语句的光标对象
cursor = conn.cursor()
# 定义要执行的SQL语句

sql_1 = "SELECT * FROM zhidao_question"
Q_id = []#问题的id
Q_body = []#问题内容
Q_numAns = []#问题的回答数量
try:
    # 执行SQL语句
    cursor.execute(sql_1)
    # 获取所有记录列表
    results = cursor.fetchall()
    for row in results:
        Q_id.append(row[0])
        Q_body.append(row[1])
        if (row[2][1] != '个'):
            Q_numAns.append(int(row[2][0]+row[2][1]))
        else:
            Q_numAns.append(int(row[2][0]))
except:
    print("Error: unable to fetch data")

sql_2 = "SELECT * FROM zhidao_answer"
A_id = []#回答的id
Q_id_forAns = []#此回答对应的问题
A_body = []#回答内容
A_numAgree = []#回答点赞
A_numDisagree = []#回答点蜡
A_accepted = []
    
try:
    # 执行SQL语句
    cursor.execute(sql_2)
    # 获取所有记录列表
    results = cursor.fetchall()
    for row in results:
        A_id.append(row[0])
        Q_id_forAns.append(row[1])
        A_body.append(row[2])
        A_numAgree.append(row[3])
        A_numDisagree.append(row[4])
        
        # 未被管理员推荐或提问者采纳
        if len(row[5]) == 0:
            A_accepted.append(0)
        #同时被管理员推荐或提问者采纳  
        elif len(row[5]) == 14:
            A_accepted.append(2)
        #只被管理员推荐or只被提问者采纳：
        else:
            A_accepted.append(1)
        
        
except:
    print("Error: unable to fetch data")
    
    
sql_3 = "SELECT * FROM baike_entry_unique"
B_id = []
B_title = []
B_url = []
B_subt = []
B_summary = []
B_imalink = []

try:
    # 执行SQL语句
    cursor.execute(sql_3)
    # 获取所有记录列表
    results = cursor.fetchall()
    for row in results:
        B_id.append(row[0])
        B_title.append(row[1])
        B_url.append(row[2])
        B_subt.append(row[3])
        B_summary.append(row[4])
        B_imalink.append(row[5])
except:
    print("Error: unable to fetch data")

    
# 关闭光标对象
cursor.close()
# 关闭数据库连接
conn.close()

#知道部分 重复问题删除
i = 0
l = len(Q_id)
while i<l:
    #print(i)
    j = Q_body.count(Q_body[i])
    if j>1:
        #print(Q_id[i],Q_body[i])
        Q_id = Q_id[:i]+Q_id[i+1:]
        Q_body = Q_body[:i]+Q_body[i+1:]
        Q_numAns = Q_numAns[:i]+Q_numAns[i+1:]
        l = len(Q_id)
    else:
        i = i+1

#len(Q_id)

#删除重复回答
i = 0
l = len(A_id)
while i<l:
    j = A_body.count(A_body[i])
    if j>1:
        A_id = A_id[:i]+A_id[i+1:]
        Q_id_forAns = Q_id_forAns[:i]+Q_id_forAns[i+1:]
        A_body = A_body[:i]+A_body[i+1:]
        A_numAgree = A_numAgree[:i]+A_numAgree[i+1:]
        A_numDisagree = A_numDisagree[:i]+A_numDisagree[i+1:]
        A_accepted = A_accepted[:i]+A_accepted[i+1:]
        l = len(A_id)
    else:
        i = i+1

import jieba.posseg as pseg
import codecs
from gensim import corpora
from gensim.summarization import bm25
import os
import re


stop_words = 'stop_words.txt'
stopwords = codecs.open(stop_words,'r',encoding='utf8').readlines()
stopwords = [ w.strip() for w in stopwords ]

stop_flag = ['x', 'c', 'u','d', 'p', 't', 'uj', 'm', 'f', 'r']

def tokenization(body):
    result = []
    words = pseg.cut(body)
    for word, flag in words:
        if flag not in stop_flag and word not in stopwords:
            result.append(word)
    return result

#分词
Q_body_split = []
for body in Q_body:
    Q_body_split.append(tokenization(body))

A_body_split = []
count = 0
for body in A_body:
    A_body_split.append(tokenization(body))

B_title_split = []#title分词
B_subt_split = []
B_summary_split = []

for i in range(len(B_title)):
    B_title_split.append(tokenization(B_title[i]))
    B_subt_split.append(tokenization(B_subt[i]))
    B_summary_split.append(tokenization(B_summary[i]))

#建立question 词袋，并排序
vec_sorted_Q = []
dictionary_q = corpora.Dictionary(Q_body_split)
doc_vectors_Q = [dictionary_q.doc2bow(body) for body in Q_body_split]
for vec in doc_vectors_Q:
    vec_sorted = sorted(vec, key=lambda x:x[1], reverse=True)
    vec_sorted_Q.append(vec_sorted)
    
#建立answer 词袋，并排序
vec_sorted_A = []
dictionary_ans = corpora.Dictionary(A_body_split)
doc_vectors_A = [dictionary_ans.doc2bow(body) for body in A_body_split]
for vec in doc_vectors_A:
    vec_sorted = sorted(vec, key=lambda x:x[1], reverse=True)
    vec_sorted_A.append(vec_sorted)

##其实好像并没有用到 排序部分……

#建立title词袋
vec_sorted_Btitle = []
vec_sorted_Bsubt = []
vec_sorted_Bsummary = []

dictionary_Btitle = corpora.Dictionary(B_title_split)
doc_vectors_Btitle = [dictionary_Btitle.doc2bow(body) for body in B_title_split]
for vec in doc_vectors_Btitle:
    vec_sorted = sorted(vec, key=lambda x:x[1], reverse=True)
    vec_sorted_Btitle.append(vec_sorted)
    
dictionary_Bsubt = corpora.Dictionary(B_subt_split)
doc_vectors_Bsubt = [dictionary_Bsubt.doc2bow(body) for body in B_subt_split]
for vec in doc_vectors_Bsubt:
    vec_sorted = sorted(vec, key=lambda x:x[1], reverse=True)
    vec_sorted_Bsubt.append(vec_sorted)


dictionary_Bsummary = corpora.Dictionary(B_summary_split)
doc_vectors_Bsummary = [dictionary_Bsummary.doc2bow(body) for body in B_summary_split]
for vec in doc_vectors_Bsubt:
    vec_sorted = sorted(vec, key=lambda x:x[1], reverse=True)
    vec_sorted_Bsubt.append(vec_sorted)

#document length
doc_len_Q = []
sum_Q = 0
for doc in Q_body_split:
    doc_len_Q.append(len(doc))
    sum_Q = sum_Q+len(doc)
avg_dl_Q = sum_Q/len(Q_body_split)

doc_len_A = []
sum_A = 0
for doc in A_body_split:
    doc_len_A.append(len(doc))
    sum_A = sum_A+len(doc)
avg_dl_A = sum_A/len(A_body_split)


doc_len_Btitle = []
sum_Btitle = 0
for doc in B_title_split:
    doc_len_Btitle.append(len(doc))
    sum_Btitle = sum_Btitle+len(doc)
avg_dl_Btitle = sum_Btitle/len(B_title_split)

doc_len_Bsubt = []
sum_Bsubt = 0
for doc in B_subt_split:
    doc_len_Bsubt.append(len(doc))
    sum_Bsubt = sum_Bsubt+len(doc)
avg_dl_Bsubt = sum_Bsubt/len(B_subt_split)

doc_len_Bsummary = []
sum_Bsummary = 0
for doc in B_summary_split:
    doc_len_Bsummary.append(len(doc))
    sum_Bsummary = sum_Bsummary+len(doc)
avg_dl_Bsummary = sum_Bsummary/len(B_summary_split)

#dl表示这个文档的长度-> doc_len[doc_id]
#avgdl表示所有文档的平均长度


#doc_id 可以是知道问题/回答/百科序号（不是Q_id，就是个index）

#qi是被查询的词，针对qi是否在这个doc里用另外的函数 查找
    
def R(doc_id,word_id,t,qfi):#qfi 根据query 要变 
    if t=='all':
        doc_vector = doc_vectors_all[doc_id]
        dl = doc_len_all[doc_id]
        avgdl = avg_dl_all
    elif t=='ques':
        doc_vector = doc_vectors_Q[doc_id]
        dl = doc_len_Q[doc_id]
        avgdl = avg_dl_Q
    elif t == 'ans':
        doc_vector = doc_vectors_A[doc_id]
        dl = doc_len_A[doc_id]
        avgdl = avg_dl_A
    elif t == 'btitle':
        doc_vector = doc_vectors_Btitle[doc_id]
        dl = doc_len_Btitle[doc_id]
        avgdl = avg_dl_Btitle
    elif t == 'bsubt':
        doc_vector = doc_vectors_Bsubt[doc_id]
        dl = doc_len_Bsubt[doc_id]
        avgdl = avg_dl_Bsubt
    elif t == 'bsummary':
        doc_vector = doc_vectors_Bsummary[doc_id]
        dl = doc_len_Bsummary[doc_id]
        avgdl = avg_dl_Bsummary
        
    ###这边可以改一个 二分法搜索？###
    for tu in doc_vector:
        #print(word_id,tu)
        if word_id == tu[0]:
            #print(term,freq)
            term,freq = tu
            break
        
    k1 = 2
    k2 = 2
    b = 0.75
    #以上三个是参数
    
    K = k1*(1-b+b*dl/avgdl)
    return freq*(k1+1)/(freq+K)*qfi*(k2+1)/(qfi+k2)

from nltk.text import TextCollection
def IDF(qi,t):
    if t=='all':
        corpus = TextCollection(body_split)
    elif t=='ques':
        corpus = TextCollection(Q_body_split)
    elif t == 'ans':
        corpus = TextCollection(A_body_split)
    elif t == 'btitle':
        corpus = TextCollection(B_title_split)
    elif t == 'bsubt':
        corpus = TextCollection(B_subt_split)
    elif t == 'bsummary':
        corpus = TextCollection(B_summary_split)
        
    
    idf=corpus.idf(qi) 
    return idf
    
def score(qi,doc_id,word_id,qfi,t):
    #查询词qi,document,词在doc里的位置，词在query里出现的次数，t是选择哪个表查询
    idf = IDF(qi,t)
    r = R(doc_id,word_id,t,1)
    return idf*r
import numpy as np

app = Flask(__name__)

@app.route('/')
def put_index():
    index_html = '''<form action = "/result" method="POST"> 
请输入关键字:<br>
<input type="text" name="Keyword">
<br>

请输入需要查找的范围:<br>
<input type="text" name="Region">
<br>
<input type="radio" name="type" value="normal" checked>Normal
<br>
<input type="radio" name="type" value="filter unrelated answer">Filter unrelated answer
<br>
<p><input type="submit" value="Submit"></p>
</form>

<p>范围类型：</p>

<p>ques:  只搜索知道问题。</p>
<p>ans:   只搜索知道回答。</p>
<p>qa:    将问题与回答看作一个整体。</p>
<p>baike: 百科模式。</p>
<p>image: 返回图片url。</p>
<p>all:   整体搜索。</p>'''
    return index_html

@app.route('/result', methods=['POST'])
def get_result_html():
    submit = request.form
    if submit['type'] == 'normal':
        result = query_all([submit['Keyword']],submit['Region'])
    elif submit['type'] == 'filter unrelated answer':
        result = query_all_delete_unrelated([submit['Keyword']],submit['Region'])
    result_html = html_outputer(result)
    return result_html


def html_outputer(result):
    count=0
    result_html=''
    result_html_head=''
    for res in result:
        result_html += '<tr>'
        for r in res[1:]:
            result_html += '<td>%s</td>' % r
        count = len(res[1:])
        result_html += '</tr>'
    result_html_head += '<tr>'
    for c in range(count):
        result_html_head += '<th>VALUE</th>'
    result_html_head += '</tr>'
    result_html = '<table>' + result_html_head + result_html + '</table>'
    return result_html

def query_all(query,t):#企图 删掉 image
    #1.处理query
    query_split = []
    for body in query:
        query_split.append(tokenization(body))
    #query 词袋：
    vec_sorted_query = []
    dictionary_query = corpora.Dictionary(query_split)
    doc_vectors_query = [dictionary_query.doc2bow(body) for body in query_split]
    
    ranklist = []
    lst = []
    
    #2.在qa里 搜索：
    if t == 'qa':
        #wa = 0.5 #这个wa是回答的weight 可改
        for i in range(len(Q_body_split)):
            s = 0
            sa1 = 0
            sa2 = 0
            sa_tem = 0
            ind1 = -1
            ind2 = -1
            for term in doc_vectors_query[0]:
                qfi=term[1]
                qi = dictionary_query[term[0]]
                if qi in Q_body_split[i]:
                    s = s+score(qi,i,dictionary_q.doc2bow([qi])[0][0],qfi,'ques')#score(qi,doc_id,word_id,qfi,t)
                try:#可能还有个 企业回答东西 要改一改
                    l_ans = Q_id_forAns.count(Q_id[i])
                    in_ans = Q_id_forAns.index(Q_id[i])
                    #相关度叠加
                    for j in range(l_ans):
                        ind = j+in_ans
                        if qi in A_body_split[ind]:
                            sa_tem = score(qi,ind,dictionary_ans.doc2bow([qi])[0][0],qfi,'ans')
                            if sa_tem > sa1 and sa_tem > sa2:
                                sa2 = sa1
                                sa1 = sa_tem
                                ind2 = ind1
                                ind1 = ind
                            elif sa_tem <= sa1 and sa_tem > sa2:
                                sa2 = sa_tem
                                ind2 = ind
                except ValueError:
                    continue
            s = s + 0.5*sa1+0.5*sa2 
            if (s!=0) :
                if (ind1!=-1)and(ind2!=-1):
                    ranklist.append((s,Q_body[i],A_body[ind1],A_body[ind2]))
                elif (ind1!=-1)and (ind2==-1):
                    ranklist.append((s,Q_body[i],A_body[ind1],''))
                elif (ind1==-1)and(ind2==-1):
                    ranklist.append((s,Q_body[i],'',''))
                s = 0
                
    #3.在 ques 里搜索
    elif t == 'ques':
        for i in range(len(Q_body_split)):
            s = 0
            for term in doc_vectors_query[0]:
                qfi=term[1]
                qi = dictionary_query[term[0]]
                if qi in Q_body_split[i]:
                    s = s+score(qi,i,dictionary_q.doc2bow([qi])[0][0],qfi,'ques')#score(qi,doc_id,word_id,qfi,t)
            if (s!=0):
                ranklist.append((s,Q_body[i]))
    #4.在ans里搜索
    elif t == 'ans':
        for i in range(len(A_body_split)):
            s = 0
            for term in doc_vectors_query[0]:
                qfi=term[1]
                qi = dictionary_query[term[0]]
                if qi in A_body_split[i]:
                    s = s+score(qi,i,dictionary_ans.doc2bow([qi])[0][0],qfi,'ans')#score(qi,doc_id,word_id,qfi,t)
            if (s!=0):
                ranklist.append((s,A_body[i]))
    #5.在baike里搜索
    elif t == 'baike':
        for i in range(len(B_title_split)):
            s_Bt = 0
            s_Bsubt = 0
            s_Bsum = 0
            s = 0
            for term in doc_vectors_query[0]:
                qfi=term[1]
                qi = dictionary_query[term[0]]
                if qi in B_title_split[i]:
                    s_Bt = s_Bt+score(qi,i,dictionary_Btitle.doc2bow([qi])[0][0],qfi,'btitle')#score(qi,doc_id,word_id,qfi,t)
                if qi in B_subt_split[i]:
                    s_Bsubt = s_Bsubt+score(qi,i,dictionary_Bsubt.doc2bow([qi])[0][0],qfi,'bsubt')#score(qi,doc_id,word_id,qfi,t)
                if qi in B_summary_split[i]:
                    s_Bsum = s_Bsum+score(qi,i,dictionary_Bsummary.doc2bow([qi])[0][0],qfi,'bsummary')#score(qi,doc_id,word_id,qfi,t)
            s = s_Bt+s_Bsum+0.5*s_Bsubt
            if (s!=0):
                ranklist.append((s,B_title[i],B_subt[i],B_summary[i]))
    elif t == 'image':
        for i in range(len(B_title_split)):
            s_Bt = 0
            s_Bsubt = 0
            s_Bsum = 0
            s = 0
            for term in doc_vectors_query[0]:
                qfi=term[1]
                qi = dictionary_query[term[0]]
                if len(B_imalink[i])!=0:
                    if qi in B_title_split[i]:
                        s_Bt = s_Bt+score(qi,i,dictionary_Btitle.doc2bow([qi])[0][0],qfi,'btitle')#score(qi,doc_id,word_id,qfi,t)
                    if qi in B_subt_split[i]:
                        s_Bsubt = s_Bsubt+score(qi,i,dictionary_Bsubt.doc2bow([qi])[0][0],qfi,'bsubt')#score(qi,doc_id,word_id,qfi,t)
                    if qi in B_summary_split[i]:
                        s_Bsum = s_Bsum+score(qi,i,dictionary_Bsummary.doc2bow([qi])[0][0],qfi,'bsummary')#score(qi,doc_id,word_id,qfi,t)
            s = s_Bt+s_Bsum+0.5*s_Bsubt
            if (s!=0):
                ranklist.append((s,B_imalink[i]))
                    
    elif t == 'all':
        ranklist1 = query_all(query,'baike')
        ranklist2 = query_all(query,'qa')
        if len(ranklist1) != 0 and len(ranklist2) != 0:
            ranklist1 = np.array(ranklist1)
            ranklist2 = np.array(ranklist2)
            data1 = np.array(list(map(float, ranklist1[:,[0]])))
            data2 = np.array(list(map(float, ranklist2[:,[0]])))
            sum1 = sum(data1)
            sum2 = sum(data2)
            data1 = data1/sum1
            data2 = data2/sum2
            ranklist1[:,0] = data1
            ranklist2[:,0] = data2
            ranklist = np.vstack((ranklist1,ranklist2))            
        elif len(ranklist1) != 0 and len(ranklist2) == 0:
            ranklist = ranklist1
        elif len(ranklist1) == 0 and len(ranklist2) != 0:
            ranklist = ranklist2
        
    ranklist = sorted(ranklist,key = lambda x:x[0], reverse = True)
    return ranklist

def query_all_delete_unrelated(query,t):
    #1.处理query
    query_split = []
    for body in query:
        query_split.append(tokenization(body))
    #query 词袋：
    vec_sorted_query = []
    dictionary_query = corpora.Dictionary(query_split)
    doc_vectors_query = [dictionary_query.doc2bow(body) for body in query_split]
    
    ranklist = []
    lst = []
    
    #2.在qa里 搜索：
    if t == 'qa':
        #wa = 0.5 #这个wa是回答的weight 可改
        for i in range(len(Q_body_split)):
            s = 0
            sa1 = 0
            sa2 = 0
            sa_tem = 0
            ind1 = -1
            ind2 = -1
            for term in doc_vectors_query[0]:
                qfi=term[1]
                qi = dictionary_query[term[0]]
                if qi in Q_body_split[i]:
                    s = s+score(qi,i,dictionary_q.doc2bow([qi])[0][0],qfi,'ques')#score(qi,doc_id,word_id,qfi,t)
                
                try:#可能还有个 企业回答东西 要改一改
                    l_ans = Q_id_forAns.count(Q_id[i])
                    in_ans = Q_id_forAns.index(Q_id[i])
                    #相关度叠加
                    for j in range(l_ans):
                        ind = j+in_ans
                        if qi in A_body_split[ind]:
                            if ((A_numAgree[ind] > A_numDisagree[ind]) and (A_accepted[ind] > 0)):
                                sa_tem = score(qi,ind,dictionary_ans.doc2bow([qi])[0][0],qfi,'ans')
                                if sa_tem > sa1 and sa_tem > sa2:
                                    sa2 = sa1
                                    sa1 = sa_tem
                                    ind2 = ind1
                                    ind1 = ind
                                elif sa_tem <= sa1 and sa_tem > sa2:
                                    sa2 = sa_tem
                                    ind2 = ind
                            else:
                                continue
                except ValueError:
                    continue
            s = s + 0.5*sa1+0.5*sa2 
            if (s!=0) :
                if (ind1!=-1)and(ind2!=-1):
                    ranklist.append((s,Q_body[i],A_body[ind1],A_body[ind2]))
                elif (ind1!=-1)and (ind2==-1):
                    ranklist.append((s,Q_body[i],A_body[ind1],''))
                elif (ind1==-1)and(ind2==-1):
                    ranklist.append((s,Q_body[i],'',''))
                s = 0
                
    #3.在 ques 里搜索
    elif t == 'ques':
        for i in range(len(Q_body_split)):
            s = 0
            for term in doc_vectors_query[0]:
                qfi=term[1]
                qi = dictionary_query[term[0]]
                if qi in Q_body_split[i]:
                    s = s+score(qi,i,dictionary_q.doc2bow([qi])[0][0],qfi,'ques')#score(qi,doc_id,word_id,qfi,t)
            if (s!=0):
                ranklist.append((s,Q_body[i]))
    #4.在ans里搜索
    elif t == 'ans':
        for i in range(len(A_body_split)):
            s = 0
            for term in doc_vectors_query[0]:
                qfi=term[1]
                qi = dictionary_query[term[0]]
                if qi in A_body_split[i]:
                    s = s+score(qi,i,dictionary_ans.doc2bow([qi])[0][0],qfi,'ans')#score(qi,doc_id,word_id,qfi,t)
            # 相关回答的条件：点好评数大于点差评数 and 被提问者采纳或管理员推荐
            if (s!=0) and ((A_numAgree[i] > A_numDisagree[i]) and (A_accepted[i] > 0)):
                ranklist.append((s,A_body[i]))
    #5.在baike里搜索
    elif t == 'baike':
        for i in range(len(B_title_split)):
            s_Bt = 0
            s_Bsubt = 0
            s_Bsum = 0
            s = 0
            for term in doc_vectors_query[0]:
                qfi=term[1]
                qi = dictionary_query[term[0]]
                if qi in B_title_split[i]:
                    s_Bt = s_Bt+score(qi,i,dictionary_Btitle.doc2bow([qi])[0][0],qfi,'btitle')#score(qi,doc_id,word_id,qfi,t)
                if qi in B_subt_split[i]:
                    s_Bsubt = s_Bsubt+score(qi,i,dictionary_Bsubt.doc2bow([qi])[0][0],qfi,'bsubt')#score(qi,doc_id,word_id,qfi,t)
                if qi in B_summary_split[i]:
                    s_Bsum = s_Bsum+score(qi,i,dictionary_Bsummary.doc2bow([qi])[0][0],qfi,'bsummary')#score(qi,doc_id,word_id,qfi,t)
            s = s_Bt+s_Bsum+0.5*s_Bsubt
            if (s!=0):
                ranklist.append((s,B_title[i],B_subt[i],B_summary[i]))
    elif t == 'image':
        for i in range(len(B_title_split)):
            s_Bt = 0
            s_Bsubt = 0
            s_Bsum = 0
            s = 0
            for term in doc_vectors_query[0]:
                qfi=term[1]
                qi = dictionary_query[term[0]]
                if len(B_imalink[i])!=0:
                    if qi in B_title_split[i]:
                        s_Bt = s_Bt+score(qi,i,dictionary_Btitle.doc2bow([qi])[0][0],qfi,'btitle')#score(qi,doc_id,word_id,qfi,t)
                    if qi in B_subt_split[i]:
                        s_Bsubt = s_Bsubt+score(qi,i,dictionary_Bsubt.doc2bow([qi])[0][0],qfi,'bsubt')#score(qi,doc_id,word_id,qfi,t)
                    if qi in B_summary_split[i]:
                        s_Bsum = s_Bsum+score(qi,i,dictionary_Bsummary.doc2bow([qi])[0][0],qfi,'bsummary')#score(qi,doc_id,word_id,qfi,t)
            s = s_Bt+s_Bsum+0.5*s_Bsubt
            if (s!=0):
                ranklist.append((s,B_imalink[i]))
    elif t == 'all':
        ranklist1 = query_all(query,'baike')
        ranklist2 = query_all(query,'qa')
        if len(ranklist1) != 0 and len(ranklist2) != 0:
            ranklist1 = np.array(ranklist1)
            ranklist2 = np.array(ranklist2)
            data1 = np.array(list(map(float, ranklist1[:,[0]])))
            data2 = np.array(list(map(float, ranklist2[:,[0]])))
            sum1 = sum(data1)
            sum2 = sum(data2)
            data1 = data1/sum1
            data2 = data2/sum2
            ranklist1[:,0] = data1
            ranklist2[:,0] = data2
            ranklist = np.vstack((ranklist1,ranklist2))            
        elif len(ranklist1) != 0 and len(ranklist2) == 0:
            ranklist = ranklist1
        elif len(ranklist1) == 0 and len(ranklist2) != 0:
            ranklist = ranklist2
        
    ranklist = sorted(ranklist,key = lambda x:x[0], reverse = True)
    return ranklist

app.run('0.0.0.0', 80)

