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
    driver.implicitly_wait(5)
    time.sleep(5)  # 동적 UI 로딩 대기

    # ---------------------------------------------------------------------
    # [핵심 1] '전체' 탭 선택하기 로직
    # ---------------------------------------------------------------------
    print("[INFO] '전체' 카테고리 탭을 찾아 클릭을 시도합니다.")
    try:
        # '전체' 텍스트를 가진 버튼이나 링크 정밀 조준
        all_tab = driver.find_element(By.XPATH,
                                      "//button[contains(., '전체')] | //a[contains(., '전체')] | //span[contains(., '전체')]/..")
        driver.execute_script("arguments[0].click();", all_tab)
        print("[INFO] -> '전체' 탭 활성화 완료!")
        time.sleep(3.0)  # 카테고리 변경에 따른 데이터 재로딩 대기
    except Exception as e:
        print(f"[WARNING] '전체' 탭 클릭 중 예외 발생 (기본 탭으로 진행): {e}")

    # ---------------------------------------------------------------------
    # [핵심 2] 숫자 기반 페이징 무한 순회 로직 (5개씩 넘어가는 구조 대응)
    # ---------------------------------------------------------------------
    count = 1
    current_page_label = 1

    while True:
        print(f"\n[INFO] 현재 {current_page_label}페이지 수집 중...")

        # 아코디언 아이템 전체 목록 수집
        faq_items = driver.find_elements(By.CSS_SELECTOR, ".cmp-accordion__item")
        print(f"[INFO] -> 현재 페이지 감지된 질문 항목: {len(faq_items)}개")

        for item in faq_items:
            try:
                # 질문 버튼 엘리먼트 추출 및 텍스트 정제
                btn = item.find_element(By.CSS_SELECTOR, ".cmp-accordion__button")
                raw_title = btn.get_attribute("textContent")
                if not raw_title:
                    raw_title = item.find_element(By.CSS_SELECTOR, ".cmp-accordion__title").get_attribute("textContent")

                full_title = " ".join(raw_title.split()).strip()
                if not full_title or len(full_title) < 4:
                    continue

                # 카테고리 분리
                category = "일반"
                title_text = full_title
                if "]" in full_title:
                    parts = full_title.split("]", 1)
                    category = parts[0].replace("[", "").strip()
                    title_text = parts[1].strip()

                # 아코디언 열기 클릭
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(0.4)

                # 답변 본문 추출
                try:
                    answer_element = item.find_element(By.CSS_SELECTOR, "[class*='__panel'], [class*='__content']")
                    content_text = answer_element.get_attribute("textContent").strip()
                except:
                    content_text = "답변 데이터 구조 매칭 실패"

                content_text = " ".join(content_text.split())

                # 최종 데이터셋 포맷팅
                faq_list.append({
                    "title": title_text,
                    "content": content_text,
                    "id": count,
                    "category": category
                })

                print(f"  [{count}] title: {title_text[:25]}...")
                count += 1

            except Exception:
                continue

        # ---------------------------------------------------------------------
        # [페이지 전환 파트] 다음 숫자가 있는지 보거나, 넘기기 화살표 버튼 클릭
        # ---------------------------------------------------------------------
        try:
            # 1단계: 다음에 눌러야 할 숫자 버튼 타깃팅 (예: 현재 1페이지면 2번 버튼 조준)
            next_page_num = current_page_label + 1

            # 숫자 버튼 검색 후보 (속성이나 텍스트 매칭)
            page_buttons = driver.find_elements(By.XPATH,
                                                f"//button[text()='{next_page_num}'] | //a[text()='{next_page_num}'] | //span[text()='{next_page_num}']/..")

            target_btn = None
            for p_btn in page_buttons:
                if p_btn.is_displayed():
                    target_btn = p_btn
                    break

            # 2단계: 다음 숫자가 화면에 안 보인다면? (5번 페이지를 다 긁어서 다음 세트로 넘기는 화살표를 눌러야 함)
            if not target_btn:
                # 'next', 'arrow', 'right', '다음' 성격의 버튼 매칭 시도
                next_set_buttons = driver.find_elements(By.CSS_SELECTOR,
                                                        "button[class*='next'], a[class*='next'], [class*='arrow-right'], .btn_next")

                for ns_btn in next_set_buttons:
                    if ns_btn.is_displayed() and "prev" not in ns_btn.get_attribute("class").lower():
                        target_btn = ns_btn
                        break

            # 3단계: 다음 숫자도 없고, 넘어가는 화살표 버튼조차 없거나 비활성화라면 루프 진짜 종료!
            if not target_btn or target_btn.get_attribute("disabled") is not None:
                print(f"\n[INFO] 기아차 FAQ 마지막 페이지에 도달하여 수집을 마칩니다. (총 {current_page_label}페이지)")
                break

            # 타깃 버튼으로 스크롤 후 부드럽게 클릭 트리거
            driver.execute_script("arguments[0].scrollIntoView(true);", target_btn)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", target_btn)

            current_page_label += 1
            time.sleep(3.0)  # 기아차 서버 동적 페이지 렌더링 동기화 대기

        except Exception as paging_err:
            print(f"\n[INFO] 페이지 이동 중 제한 발생으로 수집 프로세스 마침 (사유: {paging_err})")
            break

    # 5. 데이터프레임 빌드 및 파일 내보내기
    if faq_list:
        df = pd.DataFrame(faq_list)
        output_dir = "./data"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        csv_path = os.path.join(output_dir, "kia_faq_data.csv")
        df = df[["title", "content", "id", "category"]]  # 요구한 순서 완벽 유지
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"\n[SUCCESS] 기아차 전수 수집 완료! 총 {len(df)}개의 데이터셋이 '{csv_path}'에 저장되었습니다.")
    else:
        print("\n[ERROR] 저장할 유효 FAQ 데이터셋이 없습니다.")

except KeyboardInterrupt:
    print("\n[SYSTEM] 사용자에 의해 작업이 중단되었습니다.")
except Exception as e:
    print(f"[ERROR] 시스템 예외 발생: {e}")

finally:
    driver.quit()
    print("[SYSTEM] 브라우저 세션을 종료하고 안전하게 프로세스를 마칩니다.")