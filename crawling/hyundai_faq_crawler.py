import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 1. 크롬 드라이버 및 브라우저 환경 설정
options = webdriver.ChromeOptions()
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
faq_list = []

try:
    # 2. 대상 웹페이지 접속 및 웹 컴포넌트 렌더링 대기
    url = "https://www.hyundai.com/kr/ko/faq.html"
    print(f"[INFO] {url} 주소로 접속을 시도합니다.")
    driver.get(url)
    driver.implicitly_wait(10)
    time.sleep(5)  # Handlebars 템플릿 엔진의 동적 데이터 바인딩을 위한 대기

    # 3. 아코디언 컨테이너 및 질문 리스트 요소를 구조적으로 지정
    accordion_container = driver.find_element(By.CSS_SELECTOR, ".ui_accordion, .result_area")
    dt_elements = accordion_container.find_elements(By.CSS_SELECTOR, "dl > dt")

    total_count = len(dt_elements)
    print(f"[INFO] 수집된 FAQ 질문 항목: 총 {total_count}개")
    print("-" * 60)

    count = 1
    for idx, dt in enumerate(dt_elements, 1):
        try:
            # 질문 제목 추출 및 데이터 정제
            raw_title = dt.text if dt.text else dt.get_attribute("textContent")
            question_text = raw_title.replace("more 열기", "").replace("more 닫기", "").strip()

            if "\n" in question_text:
                question_text = question_text.split("\n")[0].strip()

            if not question_text or len(question_text) < 4:
                continue

            # 아코디언 펼침 이벤트를 위한 버튼 클릭 (JavaScript 우회 호출)
            try:
                click_btn = dt.find_element(By.CSS_SELECTOR, "button.more")
                driver.execute_script("arguments[0].click();", click_btn)
            except:
                driver.execute_script("arguments[0].click();", dt)

            time.sleep(0.5)  # 답변 영역 활성화 애니메이션 대기

            # 4. 구조적 형제 노드(<dt> 다음의 <dd>) 내부의 답변(div.exp) 추출
            try:
                dd = dt.find_element(By.XPATH, "./following-sibling::dd")
                answer_element = dd.find_element(By.CSS_SELECTOR, "div.exp")
                answer_text = answer_element.get_attribute("textContent").strip()
            except:
                answer_text = "답변 데이터 구조 매칭 실패"

            # 문자열 최종 공백 압축 정제
            question_text = " ".join(question_text.split())
            answer_text = " ".join(answer_text.split())

            # 🎯 [업데이트] 스트림릿 연동 및 카테고리 필터링을 위한 출처(source) 자동 부여
            if "서비스" in question_text or "정비" in question_text or "블루핸즈" in question_text or "AS" in question_text or "A/S" in question_text:
                source = "현대차 서비스센터"
            elif "구매" in question_text or "계약" in question_text or "출고" in question_text or "인도" in question_text:
                source = "현대차 구매가이드"
            else:
                source = "현대차 일반안내"

            # 🎯 [업데이트] 판다스 매핑용 필드명을 title, content, source로 표준화
            faq_list.append({
                "title": question_text,
                "content": answer_text,
                "source": source
            })

            print(f"[{count}] [{source}]")
            print(f"    Q: {question_text}")
            print(f"    A: {answer_text}")
            print("-" * 60)

            count += 1

        except KeyboardInterrupt:
            print("\n[SYSTEM] 사용자의 요구로 크롤링이 중단되었습니다. 현재까지의 수집 데이터를 저장합니다.")
            break
        except Exception:
            continue

    # 5. Pandas를 통한 데이터프레임 변환 및 CSV 파일 내보내기
    if faq_list:
        df = pd.DataFrame(faq_list)
        # 만약의 중복 데이터 방지
        df = df.drop_duplicates(subset=['title'])

        output_dir = "./data"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        csv_path = os.path.join(output_dir, "hyundai_faq_data.csv")
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"\n[SUCCESS] 데이터 수집 및 정제 완료! 총 {len(df)}개의 데이터가 '{csv_path}'에 저장되었습니다.")
    else:
        print("\n[ERROR] 정제 조건에 일치하는 유효 FAQ 데이터셋이 존재하지 않습니다.")

except KeyboardInterrupt:
    print("\n[SYSTEM] 초기화 단계에서 작업이 중단되었습니다.")
except Exception as e:
    print(f"[ERROR] 시스템 예외 발생: {e}")

finally:
    driver.quit()
    print("[SYSTEM] 브라우저 세션을 안전하게 종료하고 크롤링 프로세스를 마칩니다.")
