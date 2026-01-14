import os
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# ==========================================
# ⚙️ 설정
# ==========================================
TARGET_COUNT = 36000    # 목표 수집 개수
SAVE_FILE = "all_urls.json"
TARGET_URL = "https://www.musinsa.com/app/codimap/lists"

# ==========================================
# 🚀 URL 수집기 (성공한 로직 그대로)
# ==========================================
def collect_urls_exact_copy():
    print(f"🚀 URL 수집 시작 (목표: {TARGET_COUNT}개)")
    
    # 1. 설정 (아까 성공한 옵션 그대로)
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # 2. 초기화
    detail_urls = []
    visited_urls = set()
    
    # 이어하기 기능 (기존 파일 있으면 로드)
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            try:
                loaded_data = json.load(f)
                detail_urls = loaded_data
                visited_urls = set(loaded_data)
                print(f"📂 기존 데이터 {len(detail_urls)}개를 불러왔습니다.")
            except: pass

    driver.get(TARGET_URL)
    time.sleep(3) # 초기 로딩

    print("📋 URL 수집 중...")
    
    # 3. 무한 루프 (아까 성공한 방식)
    while len(detail_urls) < TARGET_COUNT:
        
        # 화면의 모든 'a' 태그 찾기
        links = driver.find_elements(By.CSS_SELECTOR, "a")
        
        # 이번 스크롤에서 새로 찾은 개수
        new_found_count = 0
        
        for link in links:
            # 목표 달성하면 즉시 종료
            if len(detail_urls) >= TARGET_COUNT:
                break
            
            try:
                href = link.get_attribute("href")
                # 유효성 검사 (codimap/views 또는 /snap/)
                if href and ("codimap/views" in href or "/snap/" in href):
                    # 중복 확인
                    if href not in visited_urls:
                        detail_urls.append(href)
                        visited_urls.add(href)
                        new_found_count += 1
                        
                        # 진행 상황 출력 (너무 자주 찍히면 정신없으니 100개 단위나, 새로 찾았을 때만)
                        # print(f"  📌 링크 확보 [{len(detail_urls)}/{TARGET_COUNT}]")
            except:
                continue
        
        print(f"⬇️ 현재 수집: {len(detail_urls)}개 (방금 +{new_found_count}개)")
        
        # 목표 달성 체크
        if len(detail_urls) >= TARGET_COUNT:
            break
            
        # 4. 스크롤 내리기 (아까 코드 그대로)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2) # 로딩 대기

        # 5. 중간 저장 (데이터 보호용)
        # 파일 저장은 안전을 위해 500개 추가될 때마다 수행
        if len(detail_urls) % 500 < 60: 
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(detail_urls, f, ensure_ascii=False, indent=4)
                print("   💾 중간 저장 완료")

    # 최종 저장
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(detail_urls, f, ensure_ascii=False, indent=4)
        
    driver.quit()
    print(f"\n🎉 URL 수집 끝! 총 {len(detail_urls)}개가 '{SAVE_FILE}'에 저장되었습니다.")

if __name__ == "__main__":
    collect_urls_exact_copy()