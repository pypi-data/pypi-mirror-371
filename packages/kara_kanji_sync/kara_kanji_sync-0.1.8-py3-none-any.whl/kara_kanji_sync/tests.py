import MeCab
import cutlet
import pysubs2
import pykakasi

from difflib import SequenceMatcher

import wanakana
from jisho_api.kanji import Kanji
from jisho_api.word import Word

from kara_kanji_sync import KanjiSyncer

katsu = cutlet.Cutlet()
katsu.use_foreign_spelling = False

kks = pykakasi.kakasi()
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def pykakasi_to_text(kanji_text: str) -> str:
    return "".join([word["hepburn"] for word in kks.convert(kanji_text)])

# wakati = MeCab.Tagger("-Owakati")
# a = "唱"
# romaji = pykakasi_to_text("唱")
# print(kks.convert(a))
# print(romaji)
# split_kanji = wakati.parse(a).split()
# print(split_kanji)
# #
# jisho_result = Kanji.request("唱")
# print(jisho_result)
# print([wanakana.to_romaji(read.split(".")[0])
#        for values in jisho_result.data.main_readings.dict().values()
#        for read in values])
#
# print(brut_force_solver('歌唱', 'utatona'))

# jisho_result = Word.request("被害者")
# print(jisho_result)
# for w in jisho_result.data:
#     for j in w.japanese:
#         print(j)
#         print(j.word)
#         print(j.reading)
# correspondence = next((j for w in jisho_result.data for j in w.japanese
#                     if j.word.startswith("被害者") and
#                        j.reading.startswith(wanakana.to_hiragana("isha"))),
#                                         None)
# print(correspondence)

song_names = [
              # "Mrs. GREEN APPLE – Boku no Koto",
              # "Vaundy – Kaijuu no Hanauta",
              # "Vaundy – Odoriko",
              # "Yorushika – Tada kimi ni hare",
              # "Yuuri – Reo",
              # "Suda Masaki – Machigai Sagashi",
              # "Mrs. GREEN APPLE – Ao to Natsu",
              # "tuki – Bansanka",
              # "Yuuri – Betelgeuse",
              # "Vaundy – Fuujin",
              # "eill – hikari",
              # "Aimer, Itsunomani, Wanuka, MAISONdes – Itsunomani",
              # "MONGOL800 – Chiisana Koi no Uta",
              # "DAOKO x Kenshi Yonezu – Uchiage Hanabi",
              "JPN - Mrs. GREEN APPLE - MV - Boku no Koto",
              ]

for song_name in song_names:
    print(song_name)
    subs = pysubs2.load(f"/home/louisq/Documents/Kara Japan7/{song_name}.ass")
    lyrics = open(f"/home/louisq/Documents/Kara Japan7/{song_name}.txt").read()
    lyrics = lyrics.replace('なぁ', "なあ").replace('ねぇ', "ねえ")
    kanji_syncer = KanjiSyncer()
    kanji_syncer.subtitles_file = subs
    kanji_syncer.lyrics = lyrics.splitlines()
    kanji_syncer.make_matches_and_groups()
    kanji_file = kanji_syncer.sync_subs()
    kanji_file.save(f'{song_name}.ass')
    print(kanji_syncer.errors)
