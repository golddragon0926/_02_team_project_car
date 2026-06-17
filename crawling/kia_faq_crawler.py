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
    # 2. 기아자동차 FAQ 페이지 접속
    url = "https://www.kia.com/kr/customer-service/center/faq"
    print(f"[INFO] {url} 주소로 접속을 시도합니다.")
    driver.get(url)
    driver.implicitly_wait(10)
    time.sleep(5)  # 동적 데이터 컴포넌트 로딩 대기

    # 3. 아코디언 아이템 전체 목록 수집
    faq_items = driver.find_elements(By.CSS_SELECTOR, ".cmp-accordion__item")
    total_count = len(faq_items)
    print(f"[INFO] 수집된 FAQ 질문 항목: 총 {total_count}개")
    print("-" * 60)

    count = 1
    for idx, item in enumerate(faq_items, 1):
        try:
            # 질문 버튼 엘리먼트 추출
            btn = item.find_element(By.CSS_SELECTOR, ".cmp-accordion__button")

            # 질문 텍스트 수집 및 공백 정제
            raw_title = btn.get_attribute("textContent")
            if not raw_title:
                raw_title = item.find_element(By.CSS_SELECTOR, ".cmp-accordion__title").get_attribute("textContent")

            full_title = " ".join(raw_title.split()).strip()

            if not full_title or len(full_title) < 4:
                continue

            # [데이터 고도화] 질문 텍스트에서 카테고리와 실제 질문 분리 시도
            # 예: "Kia Digital Key(NFC)란 무엇인가요?" -> 카테고리 추출이 모호할 경우 전체를 title에 배정
            category = "일반"
            title_text = full_title

            if "]" in full_title:
                parts = full_title.split("]", 1)
                category = parts[0].replace("[", "").strip()
                title_text = parts[1].strip()

            # JavaScript를 활용해 아코디언 버튼 클릭 (답변 영역 활성화)
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(0.6)  # 비동기 데이터 로딩 및 애니메이션 대기

            # 4. 답변 영역(.cmp-accordion__panel) 추출
            try:
                answer_element = item.find_element(By.CSS_SELECTOR, "[class*='__panel'], [class*='__content']")
                content_text = answer_element.get_attribute("textContent").strip()
            except:
                try:
                    header = item.find_element(By.CSS_SELECTOR, ".cmp-accordion__header")
                    answer_element = header.find_element(By.XPATH, "./following-sibling::div")
                    content_text = answer_element.get_attribute("textContent").strip()
                except:
                    content_text = "답변 데이터 구조 매칭 실패"

            # 답변 텍스트 공백 압축 정제
            content_text = " ".join(content_text.split())

            # 프로젝트 요구 형식(title, content)에 맞춰 딕셔너리 구조 생성
            faq_list.append({
                "id": count,
                "category": category,
                "title": title_text,
                "content": content_text
            })

            print(f"[{count}] title  : {title_text}")
            print(f"    content: {content_text[:50]}...")  # 터미널 가독성을 위해 말줄임 처리
            print("-" * 60)

            count += 1

        except KeyboardInterrupt:
            print("\n[SYSTEM] 사용자의 요구로 크롤링이 중단되었습니다. 현재까지의 수집 데이터를 저장합니다.")
            break
        except Exception:
            continue

    # 5. Pandas 데이터프레임 변환 및 파일 저장 (지정된 열 이름 반영)
    if faq_list:
        df = pd.DataFrame(faq_list)
        output_dir = "./data"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        csv_path = os.path.join(output_dir, "kia_faq_data.csv")
        # 컬럼 순서를 명시적으로 지정하여 저장합니다.
        df = df[["title", "content", "id", "category"]]
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"\n[SUCCESS] 크롤링 완료! 총 {len(df)}개의 데이터셋이 '{csv_path}'에 정상 저장되었습니다.")
    else:
        print("\n[ERROR] 저장할 유효 FAQ 데이터셋이 존재하지 않습니다.")

except KeyboardInterrupt:
    print("\n[SYSTEM] 초기화 단계에서 작업이 중단되었습니다.")
except Exception as e:
    print(f"[ERROR] 시스템 예외 발생: {e}")

finally:
    driver.quit()
    print("[SYSTEM] 브라우저 세션을 안전하게 종료하고 크롤링 프로세스를 마칩니다.")