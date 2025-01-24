import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pymysql

url = "https://www.hyundai.com/kr/ko/e/customer/center/faq"

# 질문, 답변 리스트 생성
question_list = []
answer_list = []
# ChromeDriver 실행
driver = webdriver.Chrome()  # ChromeDriver 경로 지정
driver.get(url)  # 웹사이트 열기

# 대기 후 종료
time.sleep(7)
# 모든 질문 요소 찾기
faq_questions = driver.find_elements(By.CLASS_NAME, "list-content")

# 질문 클릭 및 답변 추출
for idx, question in enumerate(faq_questions, 1):
    actions = webdriver.ActionChains(driver).move_to_element(question)
    actions.perform()
    question.click()
    print(f"Index {idx}: {question.text}")  # 각 요소 확인
    # 현대 faq 페이지는 기아 faq 페이지와 달리 다음 질문을 클릭하면 이전 질문 토글이 hidden되므로
    # 질문을 누를때마다 답변을 저장해야 된다!
    answer = driver.find_element(By.CLASS_NAME, "conts")
    answer_list.append(answer.text.strip())
    question_list.append(question.text)
    time.sleep(2)

time.sleep(7)
driver.quit()  # 브라우저 닫기

#DB 연결 user, password, db 변경할것
conn = pymysql.connect(
    host='localhost',
    user='SKN_10_2',
    password='s1234',
    database='car_db',
    charset='utf8mb4'
)


cur = conn.cursor()
for i in range(len(question_list)) :
    sql = f"""insert faq (question, answer, company) values ('{question_list[i]}','{conn.escape_string(answer_list[i])}','현대')"""
    cur.execute(sql) # sql문 실행

# commit!
conn.commit()
# 연결 종료
cur.close()
conn.close()
