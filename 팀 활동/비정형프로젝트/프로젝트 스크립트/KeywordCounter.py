from konlpy.tag import Okt
import pandas as pd

class KeywordCounter:
    def __init__(
        self,
        items:list[str],
        colours:list[str],
        materials:list[str]
    ):
        """
        items : 아이템 리스트
        colours : 색상 리스트
        materials : 재질 리스트
        """
        # 키워드 카테고리의 시작 인덱스를 기억
        self.__colourIndex = len(items)
        self.__materialIndex = self.__colourIndex + len(colours)

        # 모든 키워드 병합
        self.__keywords = items
        for key in colours:
            self.__keywords.append(key)
        for key in materials:
            self.__keywords.append(key)

        # 키워드 계측 수를 0으로 초기화
        self.__counts = pd.Series()
        for keyword in self.__keywords:
            self.__counts.loc[keyword] = 0

        # 명사 추출 용도
        self.__okt = Okt()

        # 출력
        print(f"items : {len(items)}, colours : {len(colours)}, materials : {len(materials)}")



    def BeginCounting(
        self,
        text:str,
        textReturn:list[None] = None
    ):
        """
        키워드 계측

        text : 대상 글
        textReturn : 가공된 텍스트 반환
        """
        # 결측치 확인
        if pd.isna(text) or (text == None):
            return

        # 명사만 추출
        text = self.__okt.nouns(text)

        # 텍스트에서 키워드가 포함된 횟수를 계측
        for keyword in self.__keywords:
            for word in text:
                if keyword in word:
                    self.__counts[keyword] += 1

        # 가공된 텍스트 반환
        if textReturn != None:
            textReturn.append(text)



    def GetCounts(self) -> tuple[pd.Series, pd.Series, pd.Series]:
        """
        키워드 계측 수 반환
        
        반환 : (아이템 Series, 색상 Series, 재질 Series)
        """
        # 각각의 Series로 생성
        items = self.__counts[ : self.__colourIndex]
        colours = self.__counts[self.__colourIndex : self.__materialIndex]
        materials = self.__counts[self.__materialIndex : ]

        # 이름 부여
        items.name = "items"
        colours.name = "colours"
        materials.name = "materials"
        
        # 튜플로 반환
        return (items, colours, materials)



    def ClearCounts(self):
        """
        키워드 계측 수 초기화
        """
        self.__counts[:] = 0