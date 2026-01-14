import os
import json
import time
import requests
import multiprocessing
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# ==========================================
# ⚙️ 설정
# ==========================================
PROCESS_COUNT = 4         # 🚀 동시에 띄울 크롬 창 개수 (컴퓨터 사양에 따라 4~8 조절)
URL_FILE = "all_urls.json" # 1단계에서 만든 파일 이름
BASE_DIR = "./raw_data"

# ==========================================
# 🛠️ 워커 함수 (각 프로세스가 할 일)
# ==========================================
def worker_task(process_id, urls):
    print(f"🤖 프로세스 {process_id} 시작! (담당 URL: {len(urls)}개)")
    
    # 프로세스별 저장 폴더/파일 설정
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)
        
    save_file = f"./result_part_{process_id}.json"
    results = []

    # 옵션: 병렬 처리 시에는 창을 안 띄우는게(Headless) 성능에 좋음
    chrome_options = Options()
    chrome_options.add_argument("--headless") # ⭐ 화면 안 보이기 (속도 향상)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # 이미 다운받은 ID 체크 (재시작 시 유용)
    downloaded_ids = set()

    count = 0
    for url in urls:
        try:
            driver.get(url)
            time.sleep(1.5) # 로딩 대기

            target_img = None
            extracted_tags = []

            # -------------------------------------------------
            # [기존 로직] 상세 페이지 분석 (alt 태그 + 이미지 찾기)
            # -------------------------------------------------
            images = driver.find_elements(By.TAG_NAME, "img")
            
            for img in images:
                try:
                    alt_text = img.get_attribute("alt")
                    src = img.get_attribute("src")

                    # 조건: alt에 #이 있고, 코디맵/스냅 이미지
                    if alt_text and "#" in alt_text and src and ("codimap" in src or "snap" in src):
                        temp_id = src.split("/")[-1].split("?")[0].replace(".jpg", "")
                        
                        # 같은 프로세스 내 중복 방지
                        if temp_id in downloaded_ids:
                            continue
                            
                        target_img = img
                        downloaded_ids.add(temp_id)
                        extracted_tags = [t.strip() for t in alt_text.split("#") if t.strip()]
                        break
                except: continue
            
            if not target_img:
                continue # 못 찾으면 패스

            # 데이터 저장
            img_url = target_img.get_attribute("src")
            unique_id = img_url.split("/")[-1].split("?")[0].replace(".jpg", "")
            
            if len(unique_id) < 5: unique_id = f"snap_{int(time.time())}_{process_id}_{count}"

            img_filename = f"{unique_id}.jpg"
            img_path = os.path.join(BASE_DIR, img_filename)

            # 이미지 다운로드
            img_data = requests.get(img_url).content
            with open(img_path, "wb") as f:
                f.write(img_data)
            
            meta_data = {
                "id": unique_id,
                "tags": extracted_tags,
                "image_path": img_path,
                "url": url
            }
            results.append(meta_data)
            count += 1
            
            if count % 10 == 0:
                print(f"   [P{process_id}] {count}개 완료...")

        except Exception as e:
            continue
            
    # 최종 결과 저장
    with open(save_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    
    driver.quit()
    print(f"🏁 프로세스 {process_id} 종료! (총 {len(results)}개 저장)")


# ==========================================
# 🚀 메인 실행부
# ==========================================
if __name__ == "__main__":
    # 1. URL 파일 로드
    if not os.path.exists(URL_FILE):
        print(f"❌ '{URL_FILE}' 파일이 없습니다. 1단계 코드를 먼저 실행하세요.")
        exit()
        
    with open(URL_FILE, "r", encoding="utf-8") as f:
        all_urls = json.load(f)
        
    print(f"📂 총 {len(all_urls)}개의 URL을 불러왔습니다.")
    
    # 2. URL 분배 (N등분)
    # numpy가 없으면 아래 방식으로 분배 가능:
    # chunk_size = len(all_urls) // PROCESS_COUNT
    # url_chunks = [all_urls[i:i + chunk_size] for i in range(0, len(all_urls), chunk_size)]
    
    # 간단하게 리스트 슬라이싱으로 분배
    chunk_size = int(len(all_urls) / PROCESS_COUNT) + 1
    url_chunks = [all_urls[i:i + chunk_size] for i in range(0, len(all_urls), chunk_size)]
    
    # 3. 프로세스 생성 및 시작
    processes = []
    
    start_time = time.time()
    
    for i in range(len(url_chunks)):
        p = multiprocessing.Process(target=worker_task, args=(i+1, url_chunks[i]))
        processes.append(p)
        p.start()
        
    # 4. 모든 프로세스가 끝날 때까지 대기
    for p in processes:
        p.join()
        
    end_time = time.time()
    print(f"\n✨ 전체 작업 완료! 소요 시간: {round(end_time - start_time, 2)}초")
    print("각 'result_part_N.json' 파일에 데이터가 저장되었습니다.")