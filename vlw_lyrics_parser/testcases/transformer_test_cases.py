from dataclasses import dataclass

from ..classes.collection import (
  ParsedResults, 
  ParsedLyrics, 
  ParsedTranslators,
  ReferenceItem
)
from typing import List

@dataclass
class ExpectTestCase:
  description: str
  page_title: str
  page_contents: str
  expected: ParsedResults

testcases: List[ExpectTestCase]

def populate():
  global testcases

  t1 = ExpectTestCase(
    description="A simple Japanese song page",
    page_title="SOME TITLE",
    page_contents="""{{Infobox Song
|songtitle = "'''SOME TITLE'''"
|color = gray; color: white
|original upload date = {{Date|2000|January|1}}
|singer = [[Hatsune Miku (VOCALOID)]]
|producer = [[someone]] (music, lyrics)
|#views = 10,000,000+
|link = {{#|https://www.youtube.com/watch?v=abcd1234fgh}}
|description = "A description"
|language = Japanese
}}

==Lyrics==
{{lyrics toggle|jp:Japanese|rom:Romaji|eng:English}}
{| {{lyrics table class}}
|- class="lyrics-table-header"
! {{lyrics header}}
|-
|いろはにほへと
|Iro fa nifofeto
|Even the blossoming flowers
|-
|ちりぬるを	
|Tirinuru wo
|Will eventually scatter
|-
|わかよたれそ	
|Wa ka yo tare so
|Who in our world
|-
|つねならむ
|Tune naramu
|Shall always be?
|-
|<br />
|-
|うゐのおくやま	
|Uwi no okuyama
|The deep mountains of conditions—
|-
|けふこえて
|Kefu koyete
|We cross them today
|-
|あさきゆめみし
|Asaki yume misi
|And we shall not have shallow dreams
|-
|ゑひもせす	
|Wefi mo sesu
|Nor be intoxicated.
|}
{{Translator|J. Doe}}

==External Links==
*{{VDB|S/1}}
""",
    expected=ParsedResults(
      title="SOME TITLE",
      vlw_page_id=0,
      table_ids=["1"],
      lyrics={
        "1": ParsedLyrics[str](
          headers=["Japanese", "Romaji", "English"],
          table_id="1",
          map_ids={
            "jp": "Japanese",
            "rom": "Romaji",
            "eng": "English"
          },
          translators={
            "eng": ParsedTranslators(
              col_id="eng",
              is_official=False,
              translators=["J. Doe"],
              text="English translation by J. Doe\n"
            )
          },
          data={
            "jp": [
              "いろはにほへと",
              "ちりぬるを",
              "わかよたれそ", 
              "つねならむ",
              "",
              "うゐのおくやま",
              "けふこえて",
              "あさきゆめみし",
              "ゑひもせす"
            ],
            "rom": [
              "Iro fa nifofeto",
              "Tirinuru wo",
              "Wa ka yo tare so",
              "Tune naramu",
              "",
              "Uwi no okuyama",
              "Kefu koyete",
              "Asaki yume misi",
              "Wefi mo sesu"
            ],
            "eng": [
              "Even the blossoming flowers",
              "Will eventually scatter",
              "Who in our world",
              "Shall always be?",
              "",
              "The deep mountains of conditions—",
              "We cross them today",
              "And we shall not have shallow dreams",
              "Nor be intoxicated."
            ]
          }
        )
      }
    )
  )

  t2 = ExpectTestCase(
    description="An untranslated Japanese song page",
    page_title="SOME TITLE",
    page_contents="""{{Infobox Song
|songtitle = "'''SOME TITLE'''"
|color = gray; color: white
|original upload date = {{Date|2000|January|1}}
|singer = [[Hatsune Miku (VOCALOID)]]
|producer = [[someone]] (music, lyrics)
|#views = 10,000,000+
|link = {{#|https://www.youtube.com/watch?v=abcd1234fgh}}
|description = "A description"
|language = Japanese
}}

==Lyrics==
{{lyrics toggle|jp:Japanese|rom:Romaji}}
{| {{lyrics table class}}
|- class="lyrics-table-header"
! {{lyrics header}}
|-
|いろはにほへと
|Iro fa nifofeto
|-
|ちりぬるを	
|Tirinuru wo
|-
|わかよたれそ	
|Wa ka yo tare so
|-
|つねならむ
|Tune naramu
|-
|うゐのおくやま	
|Uwi no okuyama
|-
|けふこえて
|Kefu koyete
|-
|あさきゆめみし
|Asaki yume misi
|-
|ゑひもせす	
|Wefi mo sesu
|}

==External Links==
*{{VDB|S/1}}
""",
    expected=ParsedResults(
      title="SOME TITLE",
      vlw_page_id=0,
      table_ids=["1"],
      lyrics={
        "1": ParsedLyrics[str](
          headers=["Japanese", "Romaji"],
          table_id="1",
          map_ids={
            "jp": "Japanese",
            "rom": "Romaji",
          },
          translators=None,
          data={
            "jp": [
              "いろはにほへと",
              "ちりぬるを",
              "わかよたれそ", 
              "つねならむ",
              "うゐのおくやま",
              "けふこえて",
              "あさきゆめみし",
              "ゑひもせす"
            ],
            "rom": [
              "Iro fa nifofeto",
              "Tirinuru wo",
              "Wa ka yo tare so",
              "Tune naramu",
              "Uwi no okuyama",
              "Kefu koyete",
              "Asaki yume misi",
              "Wefi mo sesu"
            ]
          }
        )
      }
    )
  )

  t3 = ExpectTestCase(
    description="A Japanese song page, with multiple templates",
    page_title="よくあるそこある (Yoku Aru Soko Aru)",
    page_contents="""{{Sort}}{{Questionable|there's like some shady stuff}}{{Infobox Song
|songtitle = "'''よくあるそこある'''"<br />Romaji: Yoku Aru Soko Aru<br />English: SOME TITLE
|color = black; color: white
|original upload date = {{Date|2000|January|1}}
|singer = [[Hatsune Miku (VOCALOID)]]
|producer = [[someone]] (music, lyrics)
|#views = 2,000+ (NN), 100,000+ (YT)
|link = {{#|https://www.nicovideo.jp/watch/sm00001}} {{#|https://www.youtube.com/watch?v=abcd1234fgh}}
|description = "A description"
|language = Japanese
}}

==Alternate Versions==
{{AlternateVersion
|title = Another version
|color = red; color:yellow
|date = January 5, 2024
|singer = someone
|producer = someone (music, lyrics)
|links = {{#|https://www.youtube.com/watch?v=abcd1234fgh}}
|description = This is an alt version
}}
{{AlternateVersion
|title = Another version
|color = red; color:yellow
|date = January 5, 2024
|singer = someone
|producer = someone (music, lyrics)
|links = {{#|https://www.youtube.com/watch?v=abcd1234fgh}}
|description = This is an alt version
}}
{{AlternateVersion
|title = Another version
|color = red; color:yellow
|date = January 5, 2024
|singer = someone
|producer = someone (music, lyrics)
|links = {{#|https://www.youtube.com/watch?v=abcd1234fgh}}
|description = This is an alt version
}}
{{AlternateVersion
|title = Another version
|color = red; color:yellow
|date = January 5, 2024
|singer = someone
|producer = someone (music, lyrics)
|links = {{#|https://www.youtube.com/watch?v=abcd1234fgh}}
|description = This is an alt version
}}

==Lyrics==
{{lyrics toggle|jp:Japanese|rom:Romaji|eng:English}}
{| {{lyrics table class}}
|- class="lyrics-table-header"
! {{lyrics header}}
|-
|いろはにほへと
|Iro fa nifofeto
|Even the blossoming flowers
|-
|ちりぬるを	
|Tirinuru wo
|Will eventually scatter
|-
|わかよたれそ	
|Wa ka yo tare so
|Who in our world
|-
|つねならむ
|Tune naramu
|Shall always be?
|-
|うゐのおくやま	
|Uwi no okuyama
|The deep mountains of conditions—
|-
|けふこえて
|Kefu koyete
|We cross them today
|-
|あさきゆめみし
|Asaki yume misi
|And we shall not have shallow dreams
|-
|ゑひもせす	
|Wefi mo sesu
|Nor be intoxicated.
|}
{{Translator|J. Doe}}

==External Links==
*{{VDB|S/1}}
""",
    expected=ParsedResults(
      title="よくあるそこある (Yoku Aru Soko Aru)",
      vlw_page_id=0,
      table_ids=["1"],
      lyrics={
        "1": ParsedLyrics[str](
          headers=["Japanese", "Romaji", "English"],
          table_id="1",
          map_ids={
            "jp": "Japanese",
            "rom": "Romaji",
            "eng": "English"
          },
          translators={
            "eng": ParsedTranslators(
              col_id="eng",
              is_official=False,
              translators=["J. Doe"],
              text="English translation by J. Doe\n"
            )
          },
          data={
            "jp": [
              "いろはにほへと",
              "ちりぬるを",
              "わかよたれそ", 
              "つねならむ",
              "うゐのおくやま",
              "けふこえて",
              "あさきゆめみし",
              "ゑひもせす"
            ],
            "rom": [
              "Iro fa nifofeto",
              "Tirinuru wo",
              "Wa ka yo tare so",
              "Tune naramu",
              "Uwi no okuyama",
              "Kefu koyete",
              "Asaki yume misi",
              "Wefi mo sesu"
            ],
            "eng": [
              "Even the blossoming flowers",
              "Will eventually scatter",
              "Who in our world",
              "Shall always be?",
              "The deep mountains of conditions—",
              "We cross them today",
              "And we shall not have shallow dreams",
              "Nor be intoxicated."
            ]
          }
        )
      }
    )
  )

  t4 = ExpectTestCase(
    description="A simple English song page, using {{Lyrics}}",
    page_title="SOME TITLE",
    page_contents="""{{Infobox Song
|songtitle = "'''SOME TITLE'''"
|color = gray; color: white
|original upload date = {{Date|2000|January|1}}
|singer = [[Hatsune Miku (VOCALOID)]]
|producer = [[someone]] (music, lyrics)
|#views = 10,000,000+
|link = {{#|https://www.youtube.com/watch?v=abcd1234fgh}}
|description = "A description"
|language = Japanese
}}

==Lyrics==
{{Lyrics|Daisy, Daisy,
Give me your answer, do!
I'm half crazy,
All for the love of you!

It won't be a stylish marriage,
I can't afford a carriage,
But you'll look sweet upon the seat
Of a bicycle built for two!
}}

==External Links==
*{{VDB|S/1}}
""",
    expected=ParsedResults(
      title="SOME TITLE",
      vlw_page_id=0,
      table_ids=["___poem-1"],
      lyrics={
        "___poem-1": ParsedLyrics[str](
          headers=["*"],
          table_id="___poem-1",
          map_ids={
            "*": "*"
          },
          translators=None,
          data={
            "*": [
              """Daisy, Daisy,
Give me your answer, do!
I'm half crazy,
All for the love of you!

It won't be a stylish marriage,
I can't afford a carriage,
But you'll look sweet upon the seat
Of a bicycle built for two!"""
            ]
          }
        )
      }
    )
  )

  t5 = ExpectTestCase(
    description="A simple English song page, using <poem>",
    page_title="SOME TITLE",
    page_contents="""{{Infobox Song
|songtitle = "'''SOME TITLE'''"
|color = gray; color: white
|original upload date = {{Date|2000|January|1}}
|singer = [[Hatsune Miku (VOCALOID)]]
|producer = [[someone]] (music, lyrics)
|#views = 10,000,000+
|link = {{#|https://www.youtube.com/watch?v=abcd1234fgh}}
|description = "A description"
|language = Japanese
}}

==Lyrics==
<poem>
Daisy, Daisy,
Give me your answer, do!
I'm half crazy,
All for the love of you!

It won't be a stylish marriage,
I can't afford a carriage,
But you'll look sweet upon the seat
Of a bicycle built for two!
</poem>

==External Links==
*{{VDB|S/1}}
""",
    expected=ParsedResults(
      title="SOME TITLE",
      vlw_page_id=0,
      table_ids=["___poem-1"],
      lyrics={
        "___poem-1": ParsedLyrics[str](
          headers=["*"],
          table_id="___poem-1",
          map_ids={
            "*": "*"
          },
          translators=None,
          data={
            "*": [
              """Daisy, Daisy,
Give me your answer, do!
I'm half crazy,
All for the love of you!

It won't be a stylish marriage,
I can't afford a carriage,
But you'll look sweet upon the seat
Of a bicycle built for two!"""
            ]
          }
        )
      }
    )
  )

  t6 = ExpectTestCase(
    description="A song page with translation notes",
    page_title="SOME TITLE",
    page_contents="""{{Infobox Song
|songtitle = "'''SOME TITLE'''"
|color = gray; color: white
|original upload date = {{Date|2000|January|1}}
|singer = [[Hatsune Miku (VOCALOID)]]
|producer = [[someone]] (music, lyrics)
|#views = 10,000,000+
|link = {{#|https://www.youtube.com/watch?v=abcd1234fgh}}
|description = "A description"
|language = Japanese
}}

==Lyrics==
{{lyrics toggle|jp:Japanese|rom:Romaji|eng:English}}
{| {{lyrics table class}}
|- class="lyrics-table-header"
! {{lyrics header}}
|-
|いろはにほへと
|Iro fa nifofeto
|Even the blossoming flowers<ref>this song is a perfect pangram, containing each character of the Japanese syllabary exactly once.</ref>
|-
|ちりぬるを	
|Tirinuru wo
|Will eventually scatter
|-
|わかよたれそ	
|Wa ka yo tare so
|Who in our<ref>tare = dare</ref> world
|-
|つねならむ
|Tune naramu
|Shall always be?<ref name=":abc">Reused ref</ref>
|-
|うゐのおくやま	
|Uwi no okuyama
|The deep mountains of conditions<ref>uwi = ui</ref>—
|-
|けふこえて
|Kefu koyete
|We cross them today<ref name=":abc" />
|-
|あさきゆめみし
|Asaki yume misi
|And we shall not have shallow dreams
|-
|ゑひもせす	
|Wefi mo sesu
|Nor be intoxicated.
|}
{{Translator|J. Doe}}

==Translation Notes==
{{Reflist}}

==External Links==
*{{VDB|S/1}}
""",
    expected=ParsedResults(
      title="SOME TITLE",
      vlw_page_id=0,
      table_ids=["1"],
      lyrics={
        "1": ParsedLyrics[str](
          headers=["Japanese", "Romaji", "English"],
          table_id="1",
          map_ids={
            "jp": "Japanese",
            "rom": "Romaji",
            "eng": "English"
          },
          translators={
            "eng": ParsedTranslators(
              col_id="eng",
              is_official=False,
              translators=["J. Doe"],
              text="English translation by J. Doe\n"
            )
          },
          data={
            "jp": [
              "いろはにほへと",
              "ちりぬるを",
              "わかよたれそ", 
              "つねならむ",
              "うゐのおくやま",
              "けふこえて",
              "あさきゆめみし",
              "ゑひもせす"
            ],
            "rom": [
              "Iro fa nifofeto",
              "Tirinuru wo",
              "Wa ka yo tare so",
              "Tune naramu",
              "Uwi no okuyama",
              "Kefu koyete",
              "Asaki yume misi",
              "Wefi mo sesu"
            ],
            "eng": [
              "Even the blossoming flowers[1]",
              "Will eventually scatter",
              "Who in our[2] world",
              "Shall always be?[3]",
              "The deep mountains of conditions[4]—",
              "We cross them today[3]",
              "And we shall not have shallow dreams",
              "Nor be intoxicated."
            ]
          }
        )
      },
      notes={
        "*": {
          "*": [
            ReferenceItem(
              group_name=None,
              counter=1,
              text="this song is a perfect pangram, containing each character of the Japanese syllabary exactly once."
            ),
            ReferenceItem(
              group_name=None,
              counter=2,
              text="tare = dare"
            ),
            ReferenceItem(
              group_name=None,
              counter=3,
              text="Reused ref"
            ),
            ReferenceItem(
              group_name=None,
              counter=4,
              text="uwi = ui"
            )
          ]
        }
      }
    )
  )

  t7 = ExpectTestCase(
    description="A Japanese song page, with multiple translations",
    page_title="SOME TITLE",
    page_contents="""{{Infobox Song
|songtitle = "'''SOME TITLE'''"
|color = gray; color: white
|original upload date = {{Date|2000|January|1}}
|singer = [[Hatsune Miku (VOCALOID)]]
|producer = [[someone]] (music, lyrics)
|#views = 10,000,000+
|link = {{#|https://www.youtube.com/watch?v=abcd1234fgh}}
|description = "A description"
|language = Japanese
}}

==Lyrics==
{{lyrics toggle|jp:Japanese|rom:Romaji|eng:English|eng2:English 2}}
{{OfficialEnglishNotify}}
{| {{lyrics table class}}
|- class="lyrics-table-header"
! {{lyrics header}}
|-
|いろはにほへと
|Iro fa nifofeto
|Even the blossoming flowers
|Tu fui, ego eris
|-
|ちりぬるを	
|Tirinuru wo
|Will eventually scatter
|Be it that you sow
|-
|わかよたれそ	
|Wa ka yo tare so
|Who in our world
|In this world that we live
|-
|つねならむ
|Tune naramu
|Shall always be?
|Shall always be?
|-
|うゐのおくやま	
|Uwi no okuyama
|The deep mountains of conditions—
|For one is two and the other
|-
|けふこえて
|Kefu koyete
|We cross them today
|Thus we cross that which should not be crossed
|-
|あさきゆめみし
|Asaki yume misi
|And we shall not have shallow dreams
|No more shallow dreams
|-
|ゑひもせす	
|Wefi mo sesu
|Nor be intoxicated.
|Nor shall we be drunk on shallow days.
|}
{{Translator|The Society of Tophats}}
{{Translator|J. Doe|anchor-col=eng2}}

==External Links==
*{{VDB|S/1}}
""",
    expected=ParsedResults(
      title="SOME TITLE",
      vlw_page_id=0,
      table_ids=["1"],
      lyrics={
        "1": ParsedLyrics[str](
          headers=["Japanese", "Romaji", "English", "English 2"],
          table_id="1",
          map_ids={
            "jp": "Japanese",
            "rom": "Romaji",
            "eng": "English",
            "eng2": "English 2"
          },
          translators={
            "eng": ParsedTranslators(
              col_id="eng",
              is_official=True,
              translators=["The Society of Tophats"],
              text="English translation by The Society of Tophats\n"
            ),
            "eng2": ParsedTranslators(
              col_id="eng2",
              is_official=False,
              translators=["J. Doe"],
              text="English translation by J. Doe\n"
            )
          },
          data={
            "jp": [
              "いろはにほへと",
              "ちりぬるを",
              "わかよたれそ", 
              "つねならむ",
              "うゐのおくやま",
              "けふこえて",
              "あさきゆめみし",
              "ゑひもせす"
            ],
            "rom": [
              "Iro fa nifofeto",
              "Tirinuru wo",
              "Wa ka yo tare so",
              "Tune naramu",
              "Uwi no okuyama",
              "Kefu koyete",
              "Asaki yume misi",
              "Wefi mo sesu"
            ],
            "eng": [
              "Even the blossoming flowers",
              "Will eventually scatter",
              "Who in our world",
              "Shall always be?",
              "The deep mountains of conditions—",
              "We cross them today",
              "And we shall not have shallow dreams",
              "Nor be intoxicated."
            ],
            "eng2": [
              "Tu fui, ego eris",
              "Be it that you sow",
              "In this world that we live",
              "Shall always be?",
              "For one is two and the other",
              "Thus we cross that which should not be crossed",
              "No more shallow dreams",
              "Nor shall we be drunk on shallow days."
            ]
          }
        )
      }
    )
  )

  t8 = ExpectTestCase(
    description="A Japanese song page with ruby & HTML entities",
    page_title="SOME TITLE",
    page_contents="""{{Infobox Song
|songtitle = "'''SOME TITLE'''"
|color = gray; color: white
|original upload date = {{Date|2000|January|1}}
|singer = [[Hatsune Miku (VOCALOID)]]
|producer = [[someone]] (music, lyrics)
|#views = 10,000,000+
|link = {{#|https://www.youtube.com/watch?v=abcd1234fgh}}
|description = "A description"
|language = Japanese
}}

==Lyrics==
{{lyrics toggle|jp:Japanese|rom:Romaji|eng:English}}
{| {{lyrics table class}}
|- class="lyrics-table-header"
! {{lyrics header}}
|-
|{{ruby|以呂波|いろは}}にほへと
|Iro fa nifofeto
|Even the blossoming flowers
|-
|ちりぬるを	
|Tirinuru wo
|Will eventually scatter
|-
|わかよたれそ	
|Wa ka yo tare so
|Who in our world
|-
|つねならむ
|Tune naramu
|Shall&nbsp;always be?
|-
|うゐのおくやま	
|Uwi no okuyama
|The deep mountains of conditions&mdash;
|-
|けふこえて
|Kefu koyete
|We cross them today
|-
|あさき{{ruby|喩女|ゆめ}}みし
|Asaki yume misi
|And we shall not have shallow dreams
|-
|ゑひもせす	
|Wefi mo sesu
|Nor be intoxicated.
|}
{{Translator|J. Doe}}

==External Links==
*{{VDB|S/1}}
""",
    expected=ParsedResults(
      title="SOME TITLE",
      vlw_page_id=0,
      table_ids=["1"],
      lyrics={
        "1": ParsedLyrics[str](
          headers=["Japanese", "Romaji", "English"],
          table_id="1",
          map_ids={
            "jp": "Japanese",
            "rom": "Romaji",
            "eng": "English"
          },
          translators={
            "eng": ParsedTranslators(
              col_id="eng",
              is_official=False,
              translators=["J. Doe"],
              text="English translation by J. Doe\n"
            )
          },
          data={
            "jp": [
              "以呂波(いろは)にほへと",
              "ちりぬるを",
              "わかよたれそ", 
              "つねならむ",
              "うゐのおくやま",
              "けふこえて",
              "あさき喩女(ゆめ)みし",
              "ゑひもせす"
            ],
            "rom": [
              "Iro fa nifofeto",
              "Tirinuru wo",
              "Wa ka yo tare so",
              "Tune naramu",
              "Uwi no okuyama",
              "Kefu koyete",
              "Asaki yume misi",
              "Wefi mo sesu"
            ],
            "eng": [
              "Even the blossoming flowers",
              "Will eventually scatter",
              "Who in our world",
              "Shall\xa0always be?",
              "The deep mountains of conditions—",
              "We cross them today",
              "And we shall not have shallow dreams",
              "Nor be intoxicated."
            ]
          }
        )
      }
    )
  )

  t9 = ExpectTestCase(
    description="A Japanese song page with multiple singers",
    page_title="SOME TITLE",
    page_contents="""{{Infobox Song
|songtitle = "'''SOME TITLE'''"
|color = gray; color: white
|original upload date = {{Date|2000|January|1}}
|singer = [[Hatsune Miku (VOCALOID)]]
|producer = [[someone]] (music, lyrics)
|#views = 10,000,000+
|link = {{#|https://www.youtube.com/watch?v=abcd1234fgh}}
|description = "A description"
|language = Japanese
}}

==Lyrics==
{{lyrics toggle|jp:Japanese|rom:Romaji|eng:English}}
{| border="1" cellpadding="4" style="border-collapse:collapse; border:1px groove; line-height:1.5"
! style="background-color:white; color:black" |Singer
|<span style="color:deeppink">Jia</span>
|<span style="color:darkorange">Yi</span>
|<span style="color:#39c065">Bing</span>
|<span style="color:blueviolet">Ding</span>
|All
|}
{| {{lyrics table class}}
|- class="lyrics-table-header"
! {{lyrics header}}
|- style="color:deeppink;"
|いろはにほへと
|Iro fa nifofeto
|Even the blossoming flowers
|- style="color: darkorange"
|ちりぬるを	
|Tirinuru wo
|Will eventually scatter
|-
|<span style="#39c065">わかよ<span style="blueviolet">たれそ</span></span>
|<span style="#39c065">Wa ka yo<span style="blueviolet"> tare so</span></span>
|<span style="#39c065">Who in<span style="blueviolet"> our world</span></span>
|-
|つねならむ<span style="color:deeppink">■<span style="color:#39c065">■</span></span>
|Tune naramu<span style="color:deeppink">■<span style="color:#39c065">■</span></span>
|Shall always be?<span style="color:deeppink">■<span style="color:#39c065">■</span></span>
|-
|<br />
|-
|うゐのおくやま<span style="color:#39c065">■</span><span style="color:blueviolet">■</span>
|Uwi no okuyama<span style="color:#39c065">■</span><span style="color:blueviolet">■</span>
|The deep mountains of conditions—<span style="color:#39c065">■</span><span style="color:blueviolet">■</span>
|- style="color:deeppink;"
|けふ<span style="#39c065">こえて</span>
|Kefu <span style="#39c065">koyete</span>
|We cross <span style="#39c065">them today</span>
|-
|あさきゆめみし<span style="color:deeppink">■<span style="color:#39c065">■</span><span style="color:#39c065">■<span style="color:blueviolet">■</span></span></span>
|Asaki yume misi<span style="color:deeppink">■<span style="color:#39c065">■</span><span style="color:#39c065">■<span style="color:blueviolet">■</span></span></span>
|And we shall not have shallow dreams<span style="color:deeppink">■<span style="color:#39c065">■</span><span style="color:#39c065">■<span style="color:blueviolet">■</span></span></span>
|-
|ゑひもせす	
|Wefi mo sesu
|Nor be intoxicated.
|}
{{Translator|J. Doe}}

==External Links==
*{{VDB|S/1}}
""",
    expected=ParsedResults(
      title="SOME TITLE",
      vlw_page_id=0,
      table_ids=["1"],
      lyrics={
        "1": ParsedLyrics[str](
          headers=["Japanese", "Romaji", "English"],
          table_id="1",
          map_ids={
            "jp": "Japanese",
            "rom": "Romaji",
            "eng": "English"
          },
          translators={
            "eng": ParsedTranslators(
              col_id="eng",
              is_official=False,
              translators=["J. Doe"],
              text="English translation by J. Doe\n"
            )
          },
          data={
            "jp": [
              "いろはにほへと",
              "ちりぬるを",
              "わかよたれそ", 
              "つねならむ",
              "",
              "うゐのおくやま",
              "けふこえて",
              "あさきゆめみし",
              "ゑひもせす"
            ],
            "rom": [
              "Iro fa nifofeto",
              "Tirinuru wo",
              "Wa ka yo tare so",
              "Tune naramu",
              "",
              "Uwi no okuyama",
              "Kefu koyete",
              "Asaki yume misi",
              "Wefi mo sesu"
            ],
            "eng": [
              "Even the blossoming flowers",
              "Will eventually scatter",
              "Who in our world",
              "Shall always be?",
              "",
              "The deep mountains of conditions—",
              "We cross them today",
              "And we shall not have shallow dreams",
              "Nor be intoxicated."
            ]
          }
        )
      }
    )
  )

  t10 = ExpectTestCase(
    description="A Japanese song page, with shared columns",
    page_title="SOME TITLE",
    page_contents="""{{Infobox Song
|songtitle = "'''SOME TITLE'''"
|color = gray; color: white
|original upload date = {{Date|2000|January|1}}
|singer = [[Hatsune Miku (VOCALOID)]]
|producer = [[someone]] (music, lyrics)
|#views = 10,000,000+
|link = {{#|https://www.youtube.com/watch?v=abcd1234fgh}}
|description = "A description"
|language = Japanese
}}

==Lyrics==
{{lyrics toggle|jp:Japanese|rom:Romaji|eng:English}}
{| {{lyrics table class}}
|- class="lyrics-table-header"
! {{lyrics header}}
|-
|{{shared}} Iro fa nifofeto
|-
|ちりぬるを	
|Tirinuru wo
|Will eventually scatter
|-
| colspan="3" | Wa ka yo tare so
|-
|{{shared|2}} Tune naramu
|Shall always be?
|-
|<br />
|-
|colspan="1"|うゐのおくやま	
|Uwi no okuyama
|The deep mountains of conditions—
|-
|{{shared|3}}Kefu koyete
|-
|{{shared|3}} Asaki yume misi
|-
|ゑひもせす	
|Wefi mo sesu
|Nor be intoxicated.
|}
{{Translator|J. Doe}}

==External Links==
*{{VDB|S/1}}
""",
    expected=ParsedResults(
      title="SOME TITLE",
      vlw_page_id=0,
      table_ids=["1"],
      lyrics={
        "1": ParsedLyrics[str](
          headers=["Japanese", "Romaji", "English"],
          table_id="1",
          map_ids={
            "jp": "Japanese",
            "rom": "Romaji",
            "eng": "English"
          },
          translators={
            "eng": ParsedTranslators(
              col_id="eng",
              is_official=False,
              translators=["J. Doe"],
              text="English translation by J. Doe\n"
            )
          },
          data={
            "jp": [
              "Iro fa nifofeto",
              "ちりぬるを",
              "Wa ka yo tare so", 
              "Tune naramu",
              "",
              "うゐのおくやま",
              "Kefu koyete",
              "Asaki yume misi",
              "ゑひもせす"
            ],
            "rom": [
              "Iro fa nifofeto",
              "Tirinuru wo",
              "Wa ka yo tare so",
              "Tune naramu",
              "",
              "Uwi no okuyama",
              "Kefu koyete",
              "Asaki yume misi",
              "Wefi mo sesu"
            ],
            "eng": [
              "Iro fa nifofeto",
              "Will eventually scatter",
              "Wa ka yo tare so",
              "Shall always be?",
              "",
              "The deep mountains of conditions—",
              "Kefu koyete",
              "Asaki yume misi",
              "Nor be intoxicated."
            ]
          }
        )
      }
    )
  )

  t11 = ExpectTestCase(
    description="An English song page with singing parts",
    page_title="SOME TITLE",
    page_contents="""{{Infobox Song
|songtitle = "'''SOME TITLE'''"
|color = gray; color: white
|original upload date = {{Date|2000|January|1}}
|singer = [[Hatsune Miku (VOCALOID)]]
|producer = [[someone]] (music, lyrics)
|#views = 10,000,000+
|link = {{#|https://www.youtube.com/watch?v=abcd1234fgh}}
|description = "A description"
|language = Japanese
}}

==Lyrics==
{| border="1" cellpadding="4" style="border-collapse:collapse; border:1px groove; line-height:1.5"
! style="background-color:white; color:black" |Singer
|<span style="color:deeppink">Jia</span>
|<span style="color:darkorange">Yi</span>
|<span style="color:#39c065">Bing</span>
|<span style="color:blueviolet">Ding</span>
|All
|}
<poem>
<span style="color:deeppink">Daisy, Daisy,</span>
<span style="color:darkorange">Give me your <span style="color:deeppink">answer, do!</span></span>
<span style="color:#39c065">I'm half crazy,</span>
<span style="color:blueviolet">All for the love of you!</span>

It won't be a stylish marriage,<span style="color:deeppink">■<span style="color:#39c065">■</span>
I can't afford a carriage,<span style="color:darkorange">■<span style="color:blueviolet">■</span>
But you'll look sweet upon the seat<span style="color:deeppink">■<span style="color:#39c065">■<span style="color:darkorange">■<span style="color:blueviolet">■</span></span>
Of a bicycle built for two!
</poem>

==External Links==
*{{VDB|S/1}}
""",
    expected=ParsedResults(
      title="SOME TITLE",
      vlw_page_id=0,
      table_ids=["___poem-1"],
      lyrics={
        "___poem-1": ParsedLyrics[str](
          headers=["*"],
          table_id="___poem-1",
          map_ids={
            "*": "*"
          },
          translators=None,
          data={
            "*": [
              """Daisy, Daisy,
Give me your answer, do!
I'm half crazy,
All for the love of you!

It won't be a stylish marriage,
I can't afford a carriage,
But you'll look sweet upon the seat
Of a bicycle built for two!"""
            ]
          }
        )
      }
    )
  )

  t12 = ExpectTestCase(
    description="A Japanese song page with multiple versions",
    page_title="SOME TITLE",
    page_contents="""{{Infobox Song
|songtitle = "'''SOME TITLE'''"
|color = gray; color: white
|original upload date = {{Date|2000|January|1}}
|singer = [[Hatsune Miku (VOCALOID)]]
|producer = [[someone]] (music, lyrics)
|#views = 10,000,000+
|link = {{#|https://www.youtube.com/watch?v=abcd1234fgh}}
|description = "A description"
|language = Japanese
}}

==Alternate Versions==
{{AlternateVersion
|title = Another version
|color = red; color:yellow
|date = January 5, 2024
|singer = someone
|producer = someone (music, lyrics)
|links = {{#|https://www.youtube.com/watch?v=abcd1234fgh}}
|description = This is an alt version
}}

==Lyrics==
<tabber>
{{lyrics toggle|jp:Japanese|rom:Romaji|eng:English}}
{| {{lyrics table class}}
|- class="lyrics-table-header"
! {{lyrics header}}
|-
|いろはにほへと
|Iro fa nifofeto
|Even the blossoming flowers
|-
|ちりぬるを	
|Tirinuru wo
|Will eventually scatter
|-
|わかよたれそ	
|Wa ka yo tare so
|Who in our world
|-
|つねならむ
|Tune naramu
|Shall always be?
|-
|<br />
|-
|うゐのおくやま	
|Uwi no okuyama
|The deep mountains of conditions—
|-
|けふこえて
|Kefu koyete
|We cross them today
|-
|あさきゆめみし
|Asaki yume misi
|And we shall not have shallow dreams
|-
|ゑひもせす	
|Wefi mo sesu
|Nor be intoxicated.
|}
{{Translator|J. Doe}}
|-|
{{lyrics toggle|jp:Japanese|rom:Romaji|eng:English}}
{| {{lyrics table class}}
|- class="lyrics-table-header"
! {{lyrics header}}
|-
|以呂波耳本へ止
|Iro wa nioedo
|Even the blooming flowers
|-
|千利奴流乎
|Chirinuru o
|Will eventually scatter
|-
|和加餘多連曽
|Wa ga yo dare zo
|Who in our world
|-
|津祢那良牟
|Tsune naran
|Shall always be?
|-
|<br />
|-
|有為能於久耶万
|Ui no okuyama
|We cross the deep 
|-
|計不己衣天
|Kyou koete
|mountains of conditions today
|-
|阿佐伎喩女美之
|Asaki yume miji
|Neither shall we have shallow dreams
|-
|恵比毛勢須
|Yoi mo sezu
|Nor be intoxicated.
|}
{{Translator|A. Thompson}}
</tabber>

==External Links==
*{{VDB|S/1}}
""",
    expected=ParsedResults(
      title="SOME TITLE",
      vlw_page_id=0,
      table_ids=["1", "2"],
      lyrics={
        "1": ParsedLyrics[str](
          headers=["Japanese", "Romaji", "English"],
          table_id="1",
          map_ids={
            "jp": "Japanese",
            "rom": "Romaji",
            "eng": "English"
          },
          translators={
            "eng": ParsedTranslators(
              col_id="eng",
              is_official=False,
              translators=["J. Doe"],
              text="English translation by J. Doe\n"
            )
          },
          data={
            "jp": [
              "いろはにほへと",
              "ちりぬるを",
              "わかよたれそ", 
              "つねならむ",
              "",
              "うゐのおくやま",
              "けふこえて",
              "あさきゆめみし",
              "ゑひもせす"
            ],
            "rom": [
              "Iro fa nifofeto",
              "Tirinuru wo",
              "Wa ka yo tare so",
              "Tune naramu",
              "",
              "Uwi no okuyama",
              "Kefu koyete",
              "Asaki yume misi",
              "Wefi mo sesu"
            ],
            "eng": [
              "Even the blossoming flowers",
              "Will eventually scatter",
              "Who in our world",
              "Shall always be?",
              "",
              "The deep mountains of conditions—",
              "We cross them today",
              "And we shall not have shallow dreams",
              "Nor be intoxicated."
            ]
          }
        ),
        "2": ParsedLyrics[str](
          headers=["Japanese", "Romaji", "English"],
          table_id="2",
          map_ids={
            "jp": "Japanese",
            "rom": "Romaji",
            "eng": "English"
          },
          translators={
            "eng": ParsedTranslators(
              col_id="eng",
              is_official=False,
              translators=["A. Thompson"],
              text="English translation by A. Thompson\n"
            )
          },
          data={
            "jp": [
              "以呂波耳本へ止",
              "千利奴流乎",
              "和加餘多連曽",
              "津祢那良牟",
              "",
              "有為能於久耶万",
              "計不己衣天",
              "阿佐伎喩女美之",
              "恵比毛勢須",
            ],
            "rom": [
              "Iro wa nioedo",
              "Chirinuru o",
              "Wa ga yo dare zo",
              "Tsune naran",
              "",
              "Ui no okuyama",
              "Kyou koete",
              "Asaki yume miji",
              "Yoi mo sezu",
            ],
            "eng": [
              "Even the blooming flowers",
              "Will eventually scatter",
              "Who in our world",
              "Shall always be?",
              "",
              "We cross the deep",
              "mountains of conditions today",
              "Neither shall we have shallow dreams",
              "Nor be intoxicated.",
            ]
          }
        )
      }
    )
  )

  testcases = [
    t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12
  ]

populate()