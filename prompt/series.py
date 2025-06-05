import dataclasses
import json
import logging
import typing

from openai import OpenAI
from pydantic import BaseModel

from prompt import schema


@dataclasses.dataclass
class Normalized:
    """도서 제목 정규화 프롬프트의 응답 클래스

    이 클래스는 입력된 도서 제목에서 불필요한 정보를 제거하고
    표준화된 형태로 반환한 결과를 저장한다.
    """

    original: str
    """원본 도서 제목 (정규화 이전의 입력값)"""

    title: str
    """정규화된 도서 제목 (불필요한 정보가 제거된 값)"""

    reason: str | None
    """제목에서 제거된 요소들에 대한 설명"""

    def __str__(self):
        return f"original: {self.original}, title: {self.title}, reason: {self.reason}"


@dataclasses.dataclass
class NormalizeRequestSaleInfo:
    """도서 판매처별 상세 정보

    도서 제목 정규화 요청 시 필요한 판매처별 도서 정보를 포함한다.
    이 정보들은 더 정확한 도서 제목 정규화를 위해 참고 자료로 활용
    """

    site: str
    """판매 사이트

    사이트별로 코드값이 따로 정해져 있지 않으며 자연어로 적어도 무관하다.
    다만 INPUT 토큰 절약을 위해 사이트의 이니셜 등을 넣는 것을 추천한다.
    """

    title: str
    """판매처에 등록된 상품명"""

    price: int | None = None
    """판매처에 등록된 상품가"""

    desc: str | None = None
    """출판사에서 제공하는 도서 상세 설명"""

    series: typing.List[str] | None = None
    """시리즈 정보

    현재 도서가 속한 시리즈의 다른 도서 제목을 포함하는 리스트
    """


@dataclasses.dataclass
class NormalizeRequest:
    """도서 제목 정규화 요청 폼

    정규화 하고 싶은 도서명과 정규화 시 참고로 사용할 수 있는 판매처별 도서 정보를 포함한다.
    """

    title: str
    """정규화 하고 싶은 도서명"""

    sale_info: typing.List[NormalizeRequestSaleInfo] | None = None
    """판매처별 도서 정보"""

class _NormalizeModelResponse(BaseModel):
    """도서 제목 정규화 프롬프트 응답 포멧"""

    title: str
    """불필요한 정보가 제거된 도서 제목"""

    reason: str | None
    """제목에서 제거된 요소들에 대한 설명

    Note:
    이 필드는 디버깅 목적으로만 사용해야 한다.
    LLM이 제목에서 제거한 요소들을 자연어로 설명한 것으로 형식이 정규화 되어 있지 않아
    프로그램에 직접 활용하지 않아야 한다.
    """

@dataclasses.dataclass
class SeriesSimilarBookInfo:
    """도서의 시리즈 분류에 필요한 기본 정보를 담는 데이터 클래스

    시리즈 분류 알고리즘에서 사용되는 도서의 핵심 정보인 제목, 출판사, 저자 정보를 포함한다.
    모든 필드는 시리즈 판단에 중요한 요소로 활용된다.
    """

    title: str
    """도서 제목"""

    publisher: int
    """출판사 아이디"""

    author: str | None
    """저자"""

@dataclasses.dataclass
class SeriesSimilarRequest:
    """시리즈 도서 분류 요청을 위한 데이터 클래스

    신간 도서 정보와 비교 대상이 되는 기존 시리즈의 도서 목록을 포함한다.
    """

    new: SeriesSimilarBookInfo
    """분류하고자 하는 신간 도서의 정보"""

    series: typing.List[SeriesSimilarBookInfo]
    """비교 대상이 되는 기존 시리즈의 도서 목록"""

@dataclasses.dataclass
class SeriesSimilar:
    """시리즈 소속 판단 결과를 담는 데이터 클래스

    요청 하였던 신간 도서가 시리즈에 소속 되는지 여부를 저장한다.
    """

    result: bool
    """시리즈 소속 여부 (True: 시리즈에 속함/False: 시리즈에 속하지 않음)"""

    reason: str| None = None
    """시리즈 판단 근거 설명"""

class _SeriesSimilarResponse(BaseModel):
    """시리즈 소속 여부 프로프트 응답 포멧"""

    result: bool
    """시리즈 소속 판단 결과"""
    
    reason: str | None
    """시리즈 소속 판단 이유
    
    Note:
    이 필드는 디버깅 목적으로만 사용해야 한다.
    LLM이 제목에서 제거한 요소들을 자연어로 설명한 것으로 형식이 정규화 되어 있지 않아
    프로그램에 직접 활용하지 않아야 한다.
    """

class Bridge:
    """LLM을 활용한 도서 시리즈 자동 분류 브릿지 클래스

    이 클래스는 OpenAI API의 프롬프트와 연결하여 도서 시리즈 자동 분류를 위한
    정규화 작업을 수행하는 인터페이스를 제공한다.
    """

    def __init__(self, openai: OpenAI, repository: schema.PromptRepository):
        self._openai = openai
        self._repository = repository

    def normalize(self, req: NormalizeRequest) -> Normalized:
        """도서 제목을 정규화 하여 표준화된 형태로 변환한다.

        :param req: 정규화할 도서 제목과 참고할 판매처 정보를 담은 요청 객체
                    판매처 정보는 더 정확한 정규화를 위한 부가 정보로 활용 됨
        :return: 정규화된 도서 제목과 처리 내역을 담은 객체
        """

        # 향후 Google Search API를 이용해 판단 근거를 더 추가해 볼 예정으로 코드 중복 유지
        request_json = json.dumps(dataclasses.asdict(req), separators=(',', ':'), ensure_ascii=False)

        prompt = self._repository.find_prompt(schema.PromptCode.TITLE_NORMALIZE)
        logging.info(f"제목의 노이즈 제거를 요청 합니다: {request_json} (previous_response_id: {prompt.last_dialogue_id})")

        response = self._openai.responses.parse(
            model=prompt.model,
            previous_response_id=prompt.last_dialogue_id,
            text_format=_NormalizeModelResponse,
            input=request_json,
        )
        formated_response = response.output_parsed

        normalization = Normalized(
            original = req.title,
            title = formated_response.title,
            reason = formated_response.reason,
        )
        logging.info(f"노이즈 제거가 완료 되었습니다 (use: {prompt.last_dialogue_id}): {req.title} ===> {normalization}")
        logging.log(logging.NOTSET, f"{req.title} => {formated_response.reason}")

        return normalization

    def series_similar(self, req: SeriesSimilarRequest) -> SeriesSimilar:
        """신간 도서가 기존 시리즈에 속하는지 여부를 판단한다.

        :param req: 시리즈 소속 여부를 확인하고 싶은 신간 도서와 기존 시리즈 정보를 담은 요청 객체
        :return: 시리즈 소속 여부
        """
        request_json = json.dumps(dataclasses.asdict(req), separators=(',', ':'), ensure_ascii=False)

        prompt = self._repository.find_prompt(schema.PromptCode.SERIES_SIMILARITY)
        logging.info(f"시리즈 소속 여부를 판단합니다: {request_json} (previous_response_id: {prompt.last_dialogue_id})")

        response = self._openai.responses.parse(
            model=prompt.model,
            previous_response_id=prompt.last_dialogue_id,
            text_format=_SeriesSimilarResponse,
            input=request_json,
        )
        formated_response = response.output_parsed

        similar = SeriesSimilar(
            result = formated_response.result,
            reason = formated_response.reason,
        )
        logging.info(f"시리즈 소속 결과 (use: {prompt.last_dialogue_id}): {similar})")

        return similar

