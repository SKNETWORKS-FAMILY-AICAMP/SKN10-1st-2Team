import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pymysql
import pandas as pd
import openpyxl

url = "https://www.kia.com/kr/customer-service/center/faq?msockid=1ddb4aa3ce1e64ec3db35fd8cf98652d"

#질문 리스트, 답변 리스트 생성성
question_list = []
answer_list = []

# ChromeDriver 실행
driver = webdriver.Chrome()  # ChromeDriver 경로 지정
driver.get(url)  # 웹사이트 열기

# 대기 후 종료
time.sleep(7)
# 모든 질문 요소 찾기
faq_questions = driver.find_elements(By.CLASS_NAME, "cmp-accordion__title")

# 질문 클릭 및 답변 추출
for idx, question in enumerate(faq_questions, 1):
    # 질문 클릭
    question.click()
    time.sleep(1)  # 클릭 후 로드 대기

    # 질문 텍스트 가져오기
    question_text = question.text.strip()
    print(question_text)
    question_list.append(question_text)
    time.sleep(1)

answer_value = driver.find_elements(By.CLASS_NAME, "faqinner__wrap")

# find_elements()를 하면 WebElement 객체가 반환되므로 .text를 이용해 정제해줘야함.
for answer in answer_value :
    answer_list.append(answer.text.strip())
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
    sql = f"""insert faq (question, answer, company) values ('{question_list[i]}','{conn.escape_string(answer_list[i])}','기아')"""
    cur.execute(sql) # sql문 실행

# commit!
conn.commit()
# 연결 종료
cur.close()
conn.close()

