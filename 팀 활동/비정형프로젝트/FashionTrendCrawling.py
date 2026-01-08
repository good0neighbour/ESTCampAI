from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import requests
import emoji
import time
import re

class FashionTrendCrawling:
    """
    크롤링 기본 동작

    BeginCrawling : 웹 페이지에서 태그 수집
    GetSpecific : 수집한 태그에서 특정 요소 추출
    ToDataFrame : DataFrame 리스트를 한 DataFrame으로 병합
    """
    def __Scrolling(
        driver,
        deltaTime:float,
        timeout:float,
        scrollCountLimit:int
    ) -> str:
        """
        페이지 스크롤
        
        반환 : str(html 페이지)
        
        page : 현재 페이지
        detaTime : 스크롤 후 페이지가 렌더링 됐는지 확인할 시간 간격 (초)
        timeout : 스크롤 후 페이지가 렌더링 되는지 확인할 최대 시간 (초)
        scrollCountLimit : 스크롤 횟수 제한. 0일때 무한.
        """
        # 스크롤 전 페이지 소스
        previous = driver.page_source
        
        # 동적 페이지 전체 스크롤할 때까지 무한반복
        timePatience = 0.0
        count = 0
        while timePatience < timeout:
            body = driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.END)
            
            # 페이지 로드 확인
            while timePatience < timeout:
                current = driver.page_source
                
                # 페이지 로드가 안 됐을 시
                if previous == current:
                    timePatience += deltaTime
                    time.sleep(deltaTime)
                
                # 페이지가 로드 됐을 시
                else:
                    # 스크롤 횟수 제한 확인
                    if scrollCountLimit > 0:
                        count += 1
                        if scrollCountLimit <= count:
                            return current
                    # 스크롤 반복
                    timePatience = 0.0
                    previous = current
                    break
        
        # 최종 로드된 페이지 반환
        return current
        
        
        
    @classmethod
    def __GetSoupWithScrolling(
        cls,
        url:str,
        timeout:int,
        scrollCountLimit:int,
        showLogs:bool
    ):
        """
        헤드리스 브라우저 실행
        웹 페이지 접속
        페이지 스크롤
        정보 수집
        
        반환 : BeautifulSoup
        
        url : 웹 페이지 주소
        timeout : 웹 패이지 로드를 기다릴 최대 시간 (초)
        scrollCountLimit : 스크롤 횟수 제한. 0일때 무한.
        showLogs : 로그 출력
        """
        # 페이지 상태 확인
        status = requests.get(url).status_code
        if showLogs: print("페이지 상태 : ", status)
        if status > 300:
            return None
        
        # 브라우저 옵션
        options = Options()
        options.add_argument("--headless=new") # 헤드리스 모드
        options.add_argument("--no-sandbox") # 샌드박스 모드에서는 브라우저 실행인 안 되는 경우가 있어 비활성화
        options.add_argument("--disable-dev-shm-usage") # 공유 메모리 대신 일반 디스크 사용. 공유 메모리는 크기가 작아서 크롬이 충분한 공간을 확보하지 못하면 크래시가 발생할 수 있음.
        options.add_argument("--start-maximized")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        # 헤드리스 브라우저 열기
        driver = webdriver.Chrome(options = options)
        if showLogs: print("헤드리스 브라우저 실행")
        
        # 페이지 로드
        driver.set_page_load_timeout(timeout)
        driver.get(url)
        if showLogs: print("페이지 로드")
        
        # 페이지 스크롤
        if showLogs: print("스크롤 시작")
        html = cls.__Scrolling(driver, 0.1, timeout / 1000.0, scrollCountLimit)
        if showLogs: print("스크롤 완료")
        
        # 브라우저 종료
        driver.quit()
        if showLogs: print("브라우저 종료")
        
        # BeautifulSoup로 파싱
        html = BeautifulSoup(html, "lxml")
        if showLogs: print("BeautifulSoup로 파싱")
        
        # 반환
        return html



    def __GetSoupWithoutScrolling(
        url:str,
        showLogs:bool
    ):
        """
        웹 페이지 요청
        
        반환 : BeautifulSoup
        
        url : 웹 페이지 주소
        showLogs : 로그 출력
        """
        # 페이지 요청
        res = requests.get(
            url,
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )
        
        # 페이지 상태 확인
        if showLogs: print("페이지 상태 : ", res.status_code)
        if res.status_code > 300:
            return None

        # 반환
        return BeautifulSoup(res.text, "lxml")



    def __GetElements(
        soup,
        selectors:list[str],
        element_names:list[str],
        showLogs:bool
    ) -> pd.DataFrame:
        """
        요소 가져오기
        
        반환 : DataFrame

        soup : BeautifulSoup로 파싱한 html
        selectors : 가져올 요소 리스트
        element_names : 수집한 요소를 구분할 이름
        showLogs : 로그 출력
        """
        # 요소 수집
        result = pd.DataFrame()
        i = 0
        while i < len(selectors):
            # 요소 수집
            elements = soup.select(selectors[i])
            if showLogs: print(f"{element_names[i]} {len(elements)}개 찾음")
            
            # 이미 존재하는 컬럼에 추가
            if element_names[i] in result.columns:
                temp = pd.DataFrame()
                temp[element_names[i]] = elements
                result = pd.concat([result, temp])
                result.index = range(0, len(result))

            # 새로운 컬럼 추가
            else:
                result[element_names[i]] = elements
            
            i += 1

        # 반환
        return result



    @classmethod
    def BeginCrawling(
        cls,
        url:str,
        selectors:list[str],
        element_names:list[str],
        timeout:int = 5000,
        scrolling:bool = True,
        scrollCountLimit:int = 0,
        showLogs:bool = True,
        soupReturn:list[None] = None
    ) -> pd.DataFrame:
        """
        크롤링 시작. 태그 수집.
        
        반환 : DataFrame

        url : 웹 페이지 주소
        selector : 가져올 요소 리스트
        element_names : 수집한 요소를 구분할 이름
        timeout : 웹 패이지 로드를 기다릴 최대 시간 (ms)
        scrolling : 페이지 스크롤 여부
        scrollCountLimit : 스크롤 횟수 제한. 0일때 무한.
        showLogs : 로그 출력
        soupReturn : html 반환
        """
        # 오류 확인
        if len(selectors) != len(element_names):
            print("\n오류\nFashionTrendCrawling.BeginCrawling()\nselectors 길이와 element_names 길이가 같아야됩니다.")
            print(f"selectors : {len(selectors)}, element_names : {len(element_names)}\n")
            return None
        elif len(selectors) < 1:
            print("\n오류\nFashionTrendCrawling.BeginCrawling()\nselectors에 하나 이상의 선택자가 들어가야됩니다.")
            return None
        
        # 페이지 요청
        if scrolling:
            soup = cls.__GetSoupWithScrolling(url, timeout, scrollCountLimit, showLogs)
        else:
            soup = cls.__GetSoupWithoutScrolling(url, showLogs)

        # 페이지 상태 확인
        if soup == None:
            print(f"\n오류\nFashionTrendCrawling.BeginCrawling()\n페이지를 요청할 수 없습니다.\n{url}")
            return None

        # 필요 시 html 반환
        if soupReturn != None:
            soupReturn.append(soup)
            if showLogs: print("BeautifulSoup로 파싱한 html 반환")
            
        # 요소 수집
        return cls.__GetElements(
            soup,
            selectors,
            element_names,
            showLogs
        )



    def GetSpecific(
        tags:pd.Series,
        element:str
    ) -> list[str]:
        """
        태그 내에서 특정 요소 추출

        반환 : 리스트

        tags : 수집한 태그 Series
        element : 추출하려는 요소
        """
        results = []

        # 요소 수집
        for tag in tags:
            results.append(tag.get(element, ""))

        # 반환
        return results



    def ToDataFrame(dataList:list[pd.DataFrame]) -> pd.DataFrame:
        """
        DataFrame 리스트를 한 DataFrame으로 병합

        반환 : DataFrame

        dataList : DataFrame 리스트
        """
        # 컬럼 확인
        for data in dataList:
            if len(data.columns) > 0:
                columns = data.columns
                break

        # 빈 DataFrame을 결측치로 생성
        i = 0
        while i < len(dataList):
            if dataList[i].empty:
                dataList[i] = pd.DataFrame(index = [0], columns = columns, data = pd.NA)
            i += 1

        # DataFrame을 병합
        dataList = pd.concat(dataList)
        dataList.index = range(0, len(dataList))

        # 반환
        return dataList



    def CleanText(text:str) -> str:
        """
        특수문자, 다중 공백, 이모지 제거

        반환 : 문자열
        """
        # 괄호 안의 광고성 문구 제거 (예: (내돈내산), (협찬), (사진=블로그주인) 등)
        text = re.sub(r'\(.*?\)', '', text)
        # 줄바꿈 및 다중 공백 정리
        text = re.sub(r'[\n\r\t]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()

        # 이모지 제거 후 반환
        return emoji.replace_emoji(text, replace = "")