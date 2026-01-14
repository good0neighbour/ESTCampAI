import os
import httpx
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

class FashionChatbot:
    def __init__(
        self,
        model_name:str = "openai:gpt-4.1-nano",
        temperature:int = 0,
        max_tokens:int = 256
    ):
        # 모델 생성
        self.__llm = FashionChatbot.__RegisterAPIKey(model_name, temperature, max_tokens)
        if self.__llm == None:
            raise Exception("모델 생성 실패")

        # 채팅 내역 담을 리스트
        self.__history = [SystemMessage(content = (
            "당신은 패션 전문가다. "
            "패션 관련헤서 추천할 때 추천 아이템, 피해야될 소재를 말한다. "
            "코디맵을 제시하고 해당하는 상품 링크와 이미지를 보여준다. "
            "상품 링크를 가져올 때 query에 들어갈 값에는 띄어쓰기 대신 +를 사용한다. "
            "이미지를 가져올 때는 url을 지어내지 않고 상품 링크에 있는 이미지 하나를 가져온다. "
            "답변은 마크다운언어로 작성하고 이미지도 마크다운언어 내에서 이미지로 표시되도록 한다."
        ))]


        
    def __RegisterAPIKey(
        model_name,
        temperature,
        max_tokens
    ):
        """
        API 키 등록

        반환 : LLM 모델
        """
        while True:
            # API 키 유효성 확인용 모델
            apiKey = input("API 키 입력 >> ")
            llm = init_chat_model(
                api_key = apiKey,
                model = "openai:gpt-4.1-nano",
                temperature = 0,
                max_tokens = 1
            )
            
            # 테스트 요청, 실패 시 예외 발생
            llm.invoke("ping")
            
            # 성공 시 실제로 사용하기 위한 모델 반환
            return init_chat_model(
                api_key = apiKey,
                model = model_name,
                temperature = temperature,
                max_tokens = max_tokens
            )



    def RequestResponse(
        self,
        message:str
    ):
        """
        응답 요청

        반환 : AIMessage

        message : 사용자 입력
        """
        # 사용자 메세지 추가
        self.__history.append(HumanMessage(content = message))

        # 응답 요청
        response = self.__llm.invoke(self.__history)

        # 응답 추가
        self.__history.append(response)
        
        # 응답 반환
        return response



    def GetHistory(
        self
    ):
        """
        대화 내역
        """
        return self.__history