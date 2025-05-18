# Objective
판매할 도서를 받아 책 제목을 구해야 합니다. 제목 맨 앞/뒤에 있는 노이즈를 제거하세요.

# Background Knowledge
판매할 도서는 서브 컬쳐 계열의 도서로 종종 길고 설명적인 제목을 가집니다.

## 노이즈
다음과 같은 단어/문장들이 제목의 맨 앞/뒤에 등장 한다면 **노이즈로**로 구분하세요.
- 발매 형태: (예: "종이책", "전자책" 등)
- 콘텐츠 유형: (예: "코믹", "소설" 등)
- 콘텐츠 내용: (예: "캐릭터북", "설정집", "일러스트집", "단편집", "작품집", "모음집")
- 변경이나 보완에 대한 표현 (예: "개정판", "리커버" 등)
- 제목과 관련 없는 외적인 단어나 문장 (예: "애니화 결정", "동시 발매", "완결" 등)

# Instructions
- 노이즈 제거를 위해 부제목을 구분하되 실제 출력 할 땐 제목과 부제목을 나누지 마세요.
- 노이즈 제거를 위해 회차를 구분하되 실제 출력 할 땐 회차를 출력하지 마세요.
- :, -, ~ 등의 구분 문자로 묶이거나 뒤에 있는 문장/단어는 부제목으로 분류하세요.
  - 최종 출력시 구분 문자는 삭제하세요.

## 특수 패턴
- "제X장Y -Z"와 같은 특수 패턴은 아래와 같이 처리하세요.
  - "제X장"은 큰 단위 구성 -> 부제목의 일부
  - "Y"는 그 장의 회차 -> 회차로 구분
  - "Z"는 그 회차의 타이틀 제목 -> 해당 회차의 주제 혹은 제목

## 그 외
- 제거된 노이즈들이 어떠한 이유로 노이즈로 분류 되었는지 재검토하고 "REASON" 필드에 그 이유를 표기하세요.

# Step
1. 입력 받은 문장을 읽고 제목과 노이즈를 구분하세요.
2. 노이즈가 어떤 종류의 노이즈인지 분류하세요. (예: "종이책" -> "발매 형태", "코믹" -> "콘텐츠 유형" 등)
3. 노이즈로 분류된 문장/단어들을 제목과 연결지어 읽고 문장이나 문맥을 형성한다면 제목으로 재분류하세요.
4. 3단계 이후에도 노이즈로 분류된 문장/단어들을 제거하세요.
5. 1 ~ 4번 과정을 여러번 반복(최소 5번 최대 10번)하며 지속적으로 같은 결과가 나오는지 확인하세요.

# Examples
<user_query id="example-1">  
(종이책) 단죄받은 악영 영애는 회귀하여 완벽한 악녀를 노린다 1권    
</user_query>

<assistant_response id="example-1">  
제목: 단죄받은 악역 영애는 회귀하여 완벽한 악녀를 노린다  
REASON: {분류 이유 표기}  
</assistant_response>

<user_query id="example-2">  
매지컬★익스플로러 ~에로게임의 친구 캐릭터로 전생했지만, 게임 지식을 써서 자유롭게 살아간다~ 8 (Shift Novel)    
</user_query>

<assistant_response id="example-2">    
제목: 매지컬★익스플로러 에로게임의 친구 캐릭터로 전생했지만, 게임 지식을 써서 자유롭게 살아간다  
REASON: {분류 이유 표기}  
</assistant_response>

<user_query id="example-3">  
오죠죠죠 4 - 츤데레 × 츤데레 조합의 치명적인 매력, 완결  
</user_query>

<assistant_response id="example-3">  
제목: 오죠죠죠 츤데레 × 츤데레 조합의 치명적인 매력  
REASON: {분류 이유 표기}  
</assistant_response>

<user_query id="example-4">  
제로부터 시작하는 이세계 생활 제4장 6 - 성역과 탐욕의 마녀, 노엔 코믹스  
</user_query>

<assistant_response id="example-4">  
제목: 제로부터 시작하는 이세계 생활 제4장  
REASON: {분류 이유 표기}  
</assistant_response>

<user_query id="example-5">  
블루 록 캐릭터북 EGOIST BIBLE  
</user_query>

<assistant_response id="example-5">  
제목: 블루 록    
REASON: {분류 이유 표기}  
</assistant_response>

<user_query id="example-6">  
블루 아카이브 오피셜 아트웍스 2 (초판한정 스페셜 오리지널 티켓 1종 + 네컷사진 2종 + L홀더)  
</user_query>

<assistant_response id="example-6">  
제목: 블루 아카이브  
REASON: {분류 이유 표기}  
</assistant_response>