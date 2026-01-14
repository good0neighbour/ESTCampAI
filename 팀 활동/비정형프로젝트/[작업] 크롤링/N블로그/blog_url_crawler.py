import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def crawl_blog_headlines(target_count=20, output_file="blog_headlines.json"):
    # 1. 크롬 옵션 설정
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True) # 브라우저 꺼짐 방지
    chrome_options.add_argument("--log-level=3") # 불필요한 로그 숨김
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    # 2. 브라우저 실행
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 3. 네이버 검색 페이지 이동
    keyword = input("검색할 키워드를 입력하세요: ")
    url = f"https://search.naver.com/search.naver?ssc=tab.blog.all&sm=tab_jum&query={keyword}"
    driver.get(url)
    time.sleep(3) # 페이지 로딩 대기

    collected_links = set()
    
    print(f"🚀 크롤링 시작... (목표: {target_count}개)")
    print("타겟: 'headline1' 클래스를 가진 메인 게시글")

    # 무한 스크롤 루프
    while len(collected_links) < target_count:
        
        # [핵심 로직]
        # 1. span 태그 중에 'headline1' 스타일을 가진 녀석들을 먼저 찾습니다.
        #    (이게 아까 말씀하신 작은 링크(body2)를 거르고 큰 제목만 찾는 필터가 됩니다.)
        headline_spans = driver.find_elements(By.CSS_SELECTOR, "span[class*='type-headline1']")
        
        current_step_count = 0
        
        for span in headline_spans:
            if len(collected_links) >= target_count:
                break
            
            try:
                # 2. span의 부모 태그인 <a> 태그를 찾습니다. (XPath 사용)
                parent_a = span.find_element(By.XPATH, "./ancestor::a")
                
                # 3. [중요] href 대신 'cru' 속성을 먼저 확인합니다.
                #    cru에 깔끔한 원본 링크(https://blog.naver.com/...)가 들어있습니다.
                link = parent_a.get_attribute("cru")
                
                # 만약 cru가 없으면 href를 가져오되, 리다이렉트 주소일 수 있음
                if not link:
                    link = parent_a.get_attribute("href")

                # 4. 링크 유효성 검사
                if link and "blog.naver.com" in link:
                    if link not in collected_links:
                        collected_links.add(link)
                        current_step_count += 1
                        # print(f"수집됨: {link}") # 확인용 출력

            except Exception:
                # 스크롤 도중 요소가 사라지거나 구조가 다를 경우 패스
                continue
        
        print(f"현재 수집된 링크: {len(collected_links)}개")

        if len(collected_links) >= target_count:
            break

        # 5. 더 수집해야 하면 스크롤 내리기
        #    (화면 끝까지 내리고 잠시 대기하여 로딩 유도)
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(2) 
        
        # 만약 스크롤을 내려도 더 이상 새로운게 안 나오면 종료하는 로직이 필요하다면 추가 가능
        # (현재는 목표 개수 채울 때까지 계속 내립니다)

    driver.quit()

    # 결과 저장
    result_list = list(collected_links)[:target_count]
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result_list, f, ensure_ascii=False, indent=4)
        print("\n" + "="*40)
        print(f"✅ 크롤링 완료! 총 {len(result_list)}개 저장됨.")
        print(f"📂 파일명: {output_file}")
        print("="*40)
    except Exception as e:
        print(f"저장 중 오류 발생: {e}")

if __name__ == "__main__":
    crawl_blog_headlines(target_count=50)