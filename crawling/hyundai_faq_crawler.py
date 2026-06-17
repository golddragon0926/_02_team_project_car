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
    # 2. 현대자동차 FAQ 페이지 접속
    url = "https://www.hyundai.com/kr/ko/faq.html"
    print(f"[INFO] {url} 주소로 접속을 시도합니다.")
    driver.get(url)
    driver.implicitly_wait(3)
    time.sleep(5)  # 초기 템플릿 로딩 대기

    page_num = 1
    count = 1

    # =========================================================================
    # [핵심] 다음 페이지 버튼이 없을 때까지 무한 반복 순회 크롤링
    # =========================================================================
    while True:
        print(f"\n[INFO] 현재 {page_num}페이지 데이터를 수집 중입니다...")

        # 현재 페이지의 아코디언 컨테이너 내 <dt>(질문) 리스트 일괄 수집
        accordion_container = driver.find_element(By.CSS_SELECTOR, ".ui_accordion, .result_area")
        dt_elements = accordion_container.find_elements(By.CSS_SELECTOR, "dl > dt")

        print(f"[INFO] -> {page_num}페이지에서 발견된 질문 항목: {len(dt_elements)}개")

        # 현재 페이지 내의 FAQ 항목들 순차 수집
        for dt in dt_elements:
            try:
                # 질문 제목 추출 및 정제
                raw_title = dt.text if dt.text else dt.get_attribute("textContent")
                full_title = raw_title.replace("more 열기", "").replace("more 닫기", "").strip()

                if "\n" in full_title:
                    full_title = full_title.split("\n")[0].strip()

                full_title = " ".join(full_title.split())
                if not full_title or len(full_title) < 4:
                    continue

                # 카테고리와 질문 텍스트 분리
                category = "일반"
                title_text = full_title

                if "]" in full_title:
                    parts = full_title.split("]", 1)
                    category = parts[0].replace("[", "").strip()
                    title_text = parts[1].strip()

                # 질문 아코디언 버튼 클릭 (답변 펼치기)
                try:
                    click_btn = dt.find_element(By.CSS_SELECTOR, "button.more")
                    driver.execute_script("arguments[0].click();", click_btn)
                except:
                    driver.execute_script("arguments[0].click();", dt)
                time.sleep(0.4)

                # 구조적 형제 노드(<dt> 다음의 <dd>) 내부의 답변(div.exp) 추출
                try:
                    dd = dt.find_element(By.XPATH, "./following-sibling::dd")
                    answer_element = dd.find_element(By.CSS_SELECTOR, "div.exp")
                    content_text = answer_element.get_attribute("textContent").strip()
                except:
                    content_text = "답변 데이터 구조 매칭 실패"

                content_text = " ".join(content_text.split())

                # 수집 양식 적재
                faq_list.append({
                    "title": title_text,
                    "content": content_text,
                    "id": count,
                    "category": category
                })

                print(f"  [{count}] title: {title_text[:30]}...")
                count += 1

            except Exception:
                continue

        # ---------------------------------------------------------------------
        # [네비게이션 페이지 이동 로직] 네가 찾아준 핵심 클래스 조준!
        # ---------------------------------------------------------------------
        try:
            # 네가 찍어준 button.navi.next 요소를 정확하게 추적
            next_btn = driver.find_element(By.CSS_SELECTOR, "button.navi.next")

            # 버튼이 비활성화(disabled)되어 있거나 화면에 안 보이면 마지막 페이지임
            if not next_btn.is_displayed() or next_btn.get_attribute("disabled") is not None:
                print(f"\n[INFO] 마지막 페이지에 도달했습니다. (최종 페이지: {page_num}명)")
                break

            # 다음 페이지로 화면 스크롤 이동 후 클릭
            driver.execute_script("arguments[0].scrollIntoView(true);", next_btn)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", next_btn)

            page_num += 1
            time.sleep(3.0)  # 다음 페이지 데이터가 완전히 렌더링될 때까지 안전 대기

        except Exception:
            print(f"\n[INFO] 다음 페이지 이동 버튼을 찾을 수 없어 수집을 종료합니다. (최종 페이지: {page_num})")
            break

    # 5. Pandas를 통한 데이터프레임 변환 및 최종 CSV 저장
    if faq_list:
        df = pd.DataFrame(faq_list)
        output_dir = "./data"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        csv_path = os.path.join(output_dir, "hyundai_faq_data.csv")
        df = df[["title", "content", "id", "category"]]
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"\n[SUCCESS] 전체 수집 완료! 총 {len(df)}개의 데이터셋이 '{csv_path}'에 저장되었습니다.")
    else:
        print("\n[ERROR] 저장할 유효 FAQ 데이터셋이 없습니다.")

except KeyboardInterrupt:
    print("\n[SYSTEM] 사용자에 의해 작업이 중단되었습니다.")
except Exception as e:
    print(f"[ERROR] 시스템 예외 발생: {e}")

finally:
    driver.quit()
    print("[SYSTEM] 브라우저 세션을 안전하게 종료하고 프로세스를 마칩니다.")