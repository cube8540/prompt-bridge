# Instruction
- 신간 도서 정보와 기존 시리즈 도서 목록을 입력으로 받아 신간이 해당 시리즈에 속하는 도서인지 판단하세요.
- 판단 결과는 True/False로 표기하세요.
- REASON 필드에 분류 이유를 표기하세요.

# Input
사용자는 아래의 JSON 스키마 형식으로 입력합니다.
{"type":"object","properties":{"new":{"type":"object","description":"신간 도서 정보","properties":{"title":{"type":"string","description":"신간 도서 제목"},"publisher":{"type":"integer","description":"신간 도서 출판사 아이디"},"author":{"type":"string","description":"저자"}},"required":["title","publisher_id"]},"series":{"type":"array","description":"기존 시리즈 리스트","items":[{"type":"object","properties":{"title":{"type":"string","description":"도서 제목"},"publisher":{"type":"integer","description":"도서 출판사 아이디"},"author":{"type":"string","description":"저자"}},"required":["title","publisher_id"]}]}},"required":["new","series"]}

# Output
판단결과: {True/False},
REASON: {판단 이유 표기}