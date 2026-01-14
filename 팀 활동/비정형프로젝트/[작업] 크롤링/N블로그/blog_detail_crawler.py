import time
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def crawl_details_from_file(input_file_name, output_file_name):
    # 1. JSON 파일에서 URL 리스트 로드
    if not os.path.exists(input_file_name):
        print(f"❌ 오류: '{input_file_name}' 파일을 찾을 수 없습니다.")
        return

    with open(input_file_name, 'r', encoding='utf-8') as f:
        url_list = json.load(f)

    print(f"📂 '{input_file_name}' 로드 완료. 총 {len(url_list)}개의 URL을 크롤링합니다.")

    # 2. 크롬 옵션 및 드라이버 설정
    chrome_options = Options()
    # 봇 탐지 방지용 User-Agent
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    chrome_options.add_argument(f"user-agent={user_agent}")
    chrome_options.add_experimental_option("detach", True)
    # chrome_options.add_argument("--headless") # 브라우저 안 보고 싶으면 주석 해제

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 10)

    results = []

    # 3. URL 순회하며 크롤링
    for i, url in enumerate(url_list):
        print(f"\n[{i+1}/{len(url_list)}] 이동 중: {url}")
        
        try:
            driver.get(url)
            
            # iframe 전환 (가장 중요)
            wait.until(EC.frame_to_be_available_and_switch_to_it("mainFrame"))

            # 데이터 추출
            # (1) 제목
            try:
                title_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.se-title-text')))
                title = title_element.text
            except:
                title = "제목 없음"

            # (2) 날짜
            try:
                date = driver.find_element(By.CSS_SELECTOR, '.se_publishDate').text
            except:
                date = "날짜 없음"

            # (3) 태그 (사용자님이 확인하신 tagList 구조 우선)
            tags = []
            try:
                # 하단 태그 리스트 영역
                tag_elements = driver.find_elements(By.CSS_SELECTOR, 'a.itemTagfont span.ell')
                
                # 만약 하단 태그가 없으면 본문 해시태그 시도
                if not tag_elements:
                    tag_elements = driver.find_elements(By.CSS_SELECTOR, '.se_hashtag')

                for tag in tag_elements:
                    tag_text = tag.text.replace("#", "").strip()
                    if tag_text and tag_text not in tags:
                        tags.append(tag_text)
            except:
                pass

            # 결과 출력
            print(f"   ✅ 제목: {title}")
            print(f"   ✅ 날짜: {date}")
            print(f"   ✅ 태그: {tags}")

            # 데이터 저장 구조 만들기
            post_data = {
                "title": title,
                "date": date,
                "tags": tags,
                "url": url
            }
            results.append(post_data)

            # 너무 빠른 요청 방지 (1~2초 휴식)
            time.sleep(1.5)

        except Exception as e:
            print(f"   ❌ 크롤링 실패: {e}")
            # 실패해도 멈추지 않고 다음 URL로 넘어갑니다.
            continue

    driver.quit()

    # 4. 결과를 JSON 파일로 저장
    with open(output_file_name, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print(f"\n🎉 모든 작업 완료! '{output_file_name}' 파일에 저장되었습니다.")

# --- 실행부 ---
if __name__ == "__main__":
    input_file = "blog_headlines.json"   # 읽어올 파일
    output_file = "blog_details.json"    # 저장할 파일
    
    crawl_details_from_file(input_file, output_file)