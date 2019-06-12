import requests
from bs4 import BeautifulSoup
import time
import re
import mysql.connector
import urllib

db_cnx = mysql.connector.connect(user='root', password='123456', database='BaiduZhidao',charset='utf8mb4')

def save_sql(data):
    cursor = db_cnx.cursor()
    
    add_question = ("INSERT INTO ZHIDAO_QUESTION" \
        "(Question, NumAns)" \
        "VALUES (%(title)s, %(number)s)")
    cursor.execute(add_question, data['question'])
    
    question_id = cursor.lastrowid
    for answer in data['answers']:
        add_answer = ("INSERT INTO ZHIDAO_ANSWER" \
            "(Question_id, Answer, agree, disagree, accept)" \
            "VALUES (%(question_id)s, %(answer)s, %(agree)s, %(disagree)s, %(accept)s)")
        answer['question_id'] = question_id
        cursor.execute(add_answer, answer)
        
    db_cnx.commit()
    cursor.close()
    

def get_answer(url):
    result = []
    wb_data = requests.get(url)
    wb_data.encoding = ('gbk')
    soup = BeautifulSoup(wb_data.text, 'lxml')
    
    # select all answer div
    answers = soup.select('div.bd.answer')
    for answer in answers:
        # get answer text
        answer_text = answer.select('div.best-text')
        best_mark = True
        if len(answer_text) == 0:  # if nothing selected
            answer_text = answer.select('div.answer-text')
            best_mark = False
            if len(answer_text) == 0:
                continue
        answer_text = answer_text[0].get_text()
        
        # get evaluate
        eva_good = answer.select('span.evaluate')
        if len(eva_good) == 0:
            eva_good = 0
        else:
            eva_good = int(eva_good[0]['data-evaluate'])

        eva_bad = answer.select('span.evaluate-bad')
        if len(eva_bad) == 0:
            eva_bad = 0
        else:
            eva_bad = int(eva_bad[0]['data-evaluate'])
    
        # get acception
        accept = answer.select('i.i-quality-icons')
        if len(accept) == 0:
            accept = ""
        else:
            accept = accept[0].parent.get_text()
        
        result.append({
            'answer': answer_text, 
        #     'is_best': best_mark,
            'agree': eva_good,
            'disagree': eva_bad,
            'accept': accept
        })
    
    # select remain pages
    remain_pages = soup.select('div.wgt-pager > a:not(.pager-next)')
    if len(remain_pages) > 0:
        remain_pages = [('https://zhidao.baidu.com' + page['href']) for page in remain_pages]
    
    return result, remain_pages

def get_page(url):
    wb_data = requests.get(url)
    wb_data.encoding = ('gbk')
    soup = BeautifulSoup(wb_data.text,'lxml')

    titles = soup.select('a.ti')
    numbers = soup.select('dd.explain > span:nth-of-type(3) > a')
    
    for title, number in zip(titles, numbers):
        # get all answers
        answers, remain_pages = get_answer(title['href'])
        if len(remain_pages) > 0:
            for page_url in remain_pages:
                remain_answers, _ = get_answer(page_url)
                answers += remain_answers

        # construct data
        data = {
            'question': {
                'title': title.get_text(),
                'number': number.get_text()
            },
            'answers': answers
        }
        
        # save data to file or db
        print(data)
        save_sql(data)
        # saveFile(data)

def saveFile(data):
    path = "PATH"
    file = open(path, 'a')
    file.write(str(data))
    file.write('\n')
    file.close()

keyword = input('请输入关键词\n')
pages = input('请输入页码\n')

url = 'https://zhidao.baidu.com/search?word=' + urllib.parse.quote(keyword, encoding='gbk')  + '&ie=gbk&site=-1&sites=0&date=0&pn='

for pn in range(0, int(pages) * 10, 10):
    get_page(url + str(pn))

db_cnx.close()