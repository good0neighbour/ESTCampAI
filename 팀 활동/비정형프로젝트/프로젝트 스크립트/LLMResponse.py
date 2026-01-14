from FashionTrendCrawling import FashionTrendCrawling as ftc
from KeywordCounter import KeywordCounter as kc
from FashionChatbot import FashionChatbot
from IPython.display import clear_output
import pandas as pd
import time


class LLMResponse:
    def __init__(self):
        # 계측기 생성
        self.__counter = kc(
            items = [
                "코트", "패딩", "자켓", "점퍼", "블레이저", "가디건", "니트", "스웨터",
                "셔츠", "블라우스", "티셔츠", "후드티", "바지", "청바지", "슬랙스", "스커트",
                "치마", "원피스", "부츠", "로퍼", "운동화", "스니커즈", "가방", "백팩",
                "머플러", "목도리", "장갑", "모자", "비니",
                "조거팬츠", "바라클라바", "스웻셔츠", "레깅스", "후리스", "롱부츠", "숄더백"
            ],
            colours = [
                "블랙", "화이트", "아이보리", "베이지", "그레이", "네이비", "브라운",
                "카키", "버건디", "레드", "핑크", "블루", "스카이블루", "옐로우", "오렌지",
                "민트", "퍼플",
                "크림", "오트밀", "라떼", "딥그린", "와인", "카멜", "톤온톤"
            ],
            materials = [
                "울", "캐시미어", "가죽", "코튼", "면", "데님", "린넨", "실크", "나일론",
                "폴리에스터", "스웨이드", "니트", "퍼", "벨벳",
                "아크릴", "레이온", "스판덱스", "코듀로이", "플리스",
                "다운", "웰론", "양털", "무스탕"
            ]
        )
        
        # 챗봇 참조할 변수
        self.__bot = None


    def __progressbar(self, startTime:float, progress:float, title:str = ""):
        """
        진행 막대 표시
        """
        remainingTime = (time.perf_counter() - startTime) / progress * (1 - progress)
        clear_output(wait = True)
        print(title)
        print(f"{"■" *  round(20 * progress)}{"□" * (20 - round(20 * progress))}", end = " ")
        print(f"{int(remainingTime // 3600):02d}:{int(remainingTime % 3600 // 60):02d}:{int(remainingTime % 60):02d}")
    
    
    def __TokenPrice(self, response_metadata:dict):
        """
        토큰 비용 출력
        """
        if "gpt-4.1-nano" in response_metadata["model_name"]:
            inputToken = 0.2 / 1000000
            outputToken = 0.8 / 1000000
        elif "gpt-4.1-mini" in response_metadata["model_name"]:
            inputToken = 0.8 / 1000000
            outputToken = 3.2 / 1000000
        elif "gpt-4.1" in response_metadata["model_name"]:
            inputToken = 3.0 / 1000000
            outputToken = 12.0 / 1000000
        else:
            print(f"사용 모델 {response_metadata["model_name"]}")
            return
    
        inputToken = response_metadata["token_usage"]["prompt_tokens"] * inputToken
        outputToken = response_metadata["token_usage"]["completion_tokens"] * outputToken
    
        return (
f"""
토큰 사용량
입력 토큰 | {response_metadata["token_usage"]["prompt_tokens"]} | US${inputToken}
출력 토큰 | {response_metadata["token_usage"]["completion_tokens"]} | US${outputToken}
총 토큰 | {response_metadata["token_usage"]["total_tokens"]} | US${inputToken + outputToken}
"""
        )
    

    def __NaverBlogCrawiling(
        self,
        query:str,
        scrollCountLimit:int = 0
    ) -> pd.DataFrame:
        """
        네이버 블로그 글 수집
    
        반환 : pd.DataFrame
    
        query : 검색 키워드
        scrollCountLimit : 최대 스크롤 수
        """
        print(f"{query} 네이버 블로그 검색")
        
        # 1. a 태그 수집
        elements = ftc.BeginCrawling(
            url = f"https://search.naver.com/search.naver?ssc=tab.blog.all&sm=tab_jum&query={query}",
            selectors = [
                "div > div > div > div > div > div.sds-comps-vertical-layout.sds-comps-full-layout.ubuDRz_QzPbskEJRLpc9 > div > div > a"
            ],
            element_names = [
                "블로그 a 태그"
            ],
            timeout = 1000,
            scrolling = True,
            scrollCountLimit = scrollCountLimit
        )
    
        # 2. 수집한 a 태그에서 링크 추출
        elements = pd.DataFrame(
            data = ftc.GetSpecific(elements["블로그 a 태그"], "href"),
            columns = ["url"]
        )
    
        # 3. 추출한 링크에서 iframe 태그 수집
        temp = []
        length = len(elements)
        i = 0
        startTime = time.perf_counter()
        while i < length:
            temp.append(
                ftc.BeginCrawling(
                    url = elements.loc[i, "url"],
                    selectors = [
                        "iframe"
                    ],
                    element_names = [
                        "iframe 태그"
                    ],
                    scrolling = False,
                    showLogs = False
                )
            )
            i += 1
            self.__progressbar(startTime, i / length, "추출한 링크에서 iframe 태그 수집")
        temp = ftc.ToDataFrame(temp)
    
        # 4. 수집한 iframe 태그에서 src 추출
        elements = pd.concat(
            [
                elements,
                pd.Series(ftc.GetSpecific(temp["iframe 태그"], "src"), name = "link")
            ],
            axis = 1
        )
    
        # 5. 수집한 src를 실제 주소로 변경
        i = 0
        while i < len(elements):
            elements.loc[i, "link"] = "https://m.blog.naver.com/" + elements.loc[i, "link"]
            i += 1
    
        # 6. 추출한 링크에서 본문 요소 수집
        temp = []
        length = len(elements)
        i = 0
        startTime = time.perf_counter()
        while i < length:
            temp.append(
                ftc.BeginCrawling(
                    url = elements.loc[i, "link"],
                    selectors = [
                        "#viewTypeSelector > div > div.se-main-container"
                    ],
                    element_names = [
                        "text"
                    ],
                    scrolling = False,
                    showLogs = False
                )
            )
            i += 1
            self.__progressbar(startTime, i / length, "추출한 링크에서 본문 요소 수집")
        temp = ftc.ToDataFrame(temp)
    
        # 7. 본문 요소에서 텍스트 추출
        texts = []
        i = 0
        while i < len(temp):
            if pd.isna(temp.loc[i, "text"]):
                texts.append(pd.NA)
            else:
                texts.append(ftc.CleanText(temp.loc[i, "text"].text))
            i += 1
        elements["text"] = texts
        
        # 8. 계측
        length = len(elements)
        i = 0
        while i < length:
            self.__counter.BeginCounting(elements.loc[i, "text"])
            i += 1
            self.__progressbar(startTime, i / length, "키워드 계측")
        
        # 9. 계측 결과 (아이템, 색상, 재질)
        result = self.__counter.GetCounts()
    
        # 출력물 모두 제거
        clear_output()
    
        # 반환
        return elements
    

    def GetLLMResponse(
        self,
        userInput:str,
        max_scroll_count:int = 0,
        model_name:str = "openai:gpt-4.1-nano",
        max_tokens:int = 512
    ) -> str:
        """
        LLM에서 답변 얻기.

        userInput : 사용자 입력
        max_tokens : 최대 토큰 수
        """
        
        # 계측기 초기화
        self.__counter.ClearCounts()
        
        # 정보 수집
        data = self.__NaverBlogCrawiling(
            query = userInput.replace(" ", "+"),
            scrollCountLimit = max_scroll_count
        )
        
        # 빈도수 가져오기
        counts = self.__counter.GetCounts()
        counts = [
            counts[0].sort_values(ascending = False).head(5),
            counts[1].sort_values(ascending = False).head(5),
            counts[2].sort_values(ascending = False).head(5)
        ]
        
        # 챗봇 생성
        if self.__bot == None:
            self.__bot = FashionChatbot(
                model_name = model_name,
                max_tokens = max_tokens
            )
        clear_output(wait = True)
        
        # 응답 요청
        response = self.__bot.RequestResponse(
        f"""
        다음 링크의 내용을 참고하라.
        {data["link"].str.cat(sep = "\n")}
        
        
        다음 키워드 언급 횟수를 참고하라.
        아이템 언급 수 top5
        {"\n".join(f"{index} : {value}" for index, value in counts[0].items())}
        
        색상 언급 수 top5
        {"\n".join(f"{index} : {value}" for index, value in counts[1].items())}
        
        재질 언급 수 top5
        {"\n".join(f"{index} : {value}" for index, value in counts[2].items())}
        
        
        네이버 블로그 내용을 요약하고 \"{userInput}\"에 대해 추천하라.
        """
        )
        
        # 응답 반환
        return (
            f"```검색 키워드 >> {userInput}```\n\n{response.content}\n\n```{self.__TokenPrice(response.response_metadata)}```",
            counts[0],
            counts[1],
            counts[2]
        )