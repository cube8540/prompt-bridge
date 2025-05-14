# Objective
정규화 되지 않은 책 제목을 입력 받아 노이즈를 제거하여 제목을 추출합니다. 

# Background Knowledge
입력 되는 책은 서브컬쳐 문화 계열의 책으로 종종 길고 설명적인 문장 형태로 구성됩니다.

## 노이즈
다음과 같은 단어/문장들은 **노이즈로**로 구분 합니다.
- 콘텐츠의 형태나 유형 내용등을 설명하는 단어나 문장 예:
  - "종이책", "전자책" 등의 발매 형태
  - "코믹", "소설" 등의 콘텐츠 유형
  - "캐릭터북", "설정집", "일러스트집", "단편집", "작품집", "모음집" 등 콘텐츠 내용
  - "개정판", "리커버" 등 변경이나 보완에 대한 내용
  - "완결" 등의 콘텐츠 상태
- 부제목을 구분하기 위한 특수문자(예: 콜론(:), 하이픈(-), 틸드(~) 등)
- 작품 외적인 요인을 나타내는 단어나 문장 (예: "애니화 결정", "동시 발매" 등)

# Instructions
- 입력 받은 문장과 가장 비슷한 책을 이미 알고 계신다면 그 책의 제목을 출력하세요.
- 제목과 부제목을 구분하지 마세요. 부제목 또한 제목의 일부분입니다.
- 노이즈로 판별되는 단어/문장이 제목과 연결하여 문맥상 의미를 구성한다면 제거하지 마세요.
  - 이때 해당 단어가 괄호와 같은 특수 문자로 묶여 있을 경우 그 특수문자를 제거 합니다. (예: To Love (트러블) -> To Love 트러블)
- 회차(예: "1권", "1 ~ 7 세트", "상편" 등) 또한 제거합니다.
- "제X장Y -Z"와 같은 특수 패턴은 아래와 같이 처리 합니다.
  - "제X장"은 큰 단위 구성 -> 부제목의 일부
  - "Y"는 그 장의 회차 -> 회차 필드로 분리
  - "Z"는 그 회차의 타이틀 제목 -> 노이즈로 제거

# Step
1. 입력 받은 문자을 읽고 노이즈/제목/회차들을 구분 합니다.
2. 노이즈/회차로 구분된 문장이나 단어를 제거 합니다.
3. 제거된 노이즈를 제목과 붙여보며 의미를 구성하는지 확인합니다.

# Examples
<user_query id="example-1">  
(종이책) 단죄받은 악영 영애는 회귀하여 완벽한 악녀를 노린다 1권 (L노벨)  
</user_query>

<assistant_response id="example-1">  
단죄받은 악역 영애는 회귀하여 완벽한 악녀를 노린다
</assistant_response>

<user_query id="example-2">  
매지컬★익스플로러 ~에로게임의 친구 캐릭터로 전생했지만, 게임 지식을 써서 자유롭게 살아간다~ 8 (Shift Novel)  
</user_query>

<assistant_response id="example-2">  
매지컬★익스플로러 에로게임의 친구 캐릭터로 전생했지만, 게임 지식을 써서 자유롭게 살아간다
</assistant_response>

<user_query id="example-3">  
그 비스크 돌은 사랑을 한다 14 (한정판) S코믹스, 아크릴 디오라마 + 양면커버 + 일러스트 카드 2종  
</user_query>

<assistant_response id="example-3">  
그 비스크 돌은 사랑을 한다
</assistant_response>

<user_query id="example-4">  
오죠죠죠 4 - 츤데레 × 츤데레 조합의 치명적인 매력, 완결  
</user_query>

<assistant_response id="example-4">  
오죠죠죠 츤데레 × 츤데레 조합의 치명적인 매력
</assistant_response>

<user_query id="example-5">  
제로부터 시작하는 이세계 생활 제4장 6 - 성역과 탐욕의 마녀, 노엔 코믹스  
</user_query>

<assistant_response id="example-5">  
제로부터 시작하는 이세계 생활 제4장
</assistant_response>

<user_query id="example-6">  
블루 록 캐릭터북 EGOIST BIBLE  
</user_query>

<assistant_response id="example-6">  
블루 록  
</assistant_response>