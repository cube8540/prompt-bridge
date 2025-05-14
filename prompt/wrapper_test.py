import os
import unittest

import dotenv
from openai import OpenAI

from prompt import SeriesPrompt

dotenv.load_dotenv("../.env.test")

openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
prompt = SeriesPrompt(
    openai,
    os.getenv("OPENAI_NORMALIZATION_PROMPT_ID"),
    os.getenv("OPENAI_SIMILARLY_PROMPT_ID")
)

class TitleNormalization(unittest.TestCase):
    def test_somthing(self):
        normalize = prompt.normalization("코믹 블루록 22")
        self.assertEqual(normalize.title, "블루록")

        normalize = prompt.normalization("블루 록 캐릭터북 EGOIST BIBLE")
        self.assertEqual(normalize.title, "블루 록")

        normalize = prompt.normalization("블루 록 : Episode 나기 2")
        self.assertEqual(normalize.title, "블루 록 Episode 나기")

        normalize = prompt.normalization("블루 아카이브 : 게임개발부 대모험! 1 (한정판) - PET 일러스트 카드 4장 + 아크릴 디오라마 + B6 클리어 파일 + 미즈 아사토 선생님의 자필 메시지 카드 1장")
        self.assertEqual(normalize.title, "블루 아카이브 게임개발부 대모험!")

        normalize = prompt.normalization("블루 아카이브 오피셜 아트웍스 2 (초판한정 스페셜 오리지널 티켓 1종 + 네컷사진 2종 + L홀더)")
        self.assertEqual(normalize.title, "블루 아카이브")

        normalize = prompt.normalization("To Love 트러블 : 다크니스 리커버 3")
        self.assertEqual(normalize.title, "To Love 트러블 다크니스")

        normalize = prompt.normalization("매지컬★익스플로러 ~에로게임의 친구 캐릭터로 전생했지만, 게임 지식을 써서 자유롭게 살아간다~ 8 (Shift Novel)")
        self.assertEqual(normalize.title, "매지컬★익스플로러 에로게임의 친구 캐릭터로 전생했지만, 게임 지식을 써서 자유롭게 살아간다")

        normalize = prompt.normalization("코믹 Re:제로부터 시작하는 이세계 생활 -제4장- 3 (성역과 탐욕의 마녀, 노엔 코믹스)")
        self.assertEqual(normalize.title, "Re:제로부터 시작하는 이세계 생활 제4장")

        normalize = prompt.normalization("검귀연가 : Re:제로부터 시작하는 이세계 생활 진명담 3 (노엔 코믹스)")
        self.assertEqual(normalize.title, "검귀연가 Re:제로부터 시작하는 이세계 생활 진명담")

        normalize = prompt.normalization("Re:제로부터 시작하는 이세계 생활 제4장 6 - 성역과 탐욕의 마녀, 노엔 코믹스")
        self.assertEqual(normalize.title, "Re:제로부터 시작하는 이세계 생활 제4장")

        normalize = prompt.normalization("Re:제로부터 시작하는 이세계 생활 35 (Novel Engine)")
        self.assertEqual(normalize.title, "Re:제로부터 시작하는 이세계 생활")

        normalize = prompt.normalization("Re:제로부터 시작하는 이세계 생활 Re:zeropedia 2 (Novel Engine)")
        self.assertEqual(normalize.title, "Re:제로부터 시작하는 이세계 생활")

        normalize = prompt.normalization("나의 히어로 아카데미아 -팀업 미션- 7 - 최고의 한 장")
        self.assertEqual(normalize.title, "나의 히어로 아카데미아 팀업 미션")

        normalize = prompt.normalization("나의 히어로 아카데미아: 팀업 미션 6 (고잉 마이웨이)")
        self.assertEqual(normalize.title, "나의 히어로 아카데미아 팀업 미션")

        normalize = prompt.normalization("나의 히어로 아카데미아 41 (트리플 특장판) ((초판한정) 히어로&빌런’ 일러스트 카드 + 일러스트 필름 카드 + (선착순 한정) 아크릴 일러스트 보드)")
        self.assertEqual(normalize.title, "나의 히어로 아카데미아")

        normalize = prompt.normalization("코믹 걸즈 2")
        self.assertEqual(normalize.title, "코믹 걸즈")

if __name__ == '__main__':
    unittest.main()
