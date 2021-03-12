"""
データ構造の定義と読み書きの抽象化
"""


import json
from typing import List, Union, NamedTuple, Optional, Callable, Awaitable, Generic, TypeVar, Sequence, Iterable, Dict


class Genre:
    """
    ジャンル

    Attributes
    ----------
    genre_id
        ジャンルの ID．一意
    name
        ジャンルの表示名
    """
    genre_id: str
    name: str

    def __init__(self, genre_id: str, name: str):
        self.genre_id = genre_id
        self.name = name
    
    def __str__(self):
        return self.name

    genres: Optional[Dict[str, 'Genre']] = None
    """ジャンル一覧"""

    @classmethod
    def _load_all(cls):
        """ジャンルを全てファイルからメモリに読み込む"""
        with open('./icebreak_bot/db/genre.json') as file:
            genres_raw = json.load(file)
            cls.genres = {odai_raw["id"]: Genre(odai_raw["id"], odai_raw["name"]) for odai_raw in genres_raw}

    @classmethod
    def from_id(cls, genre_id: str) -> Optional['Genre']:
        """
        ジャンルの ID から Genre インスタンスを取得する
        """
        if cls.genres is None:
            cls._load_all()
        assert cls.genres is not None
        if genre_id in cls.genres:
            return cls.genres[genre_id]
        else:
            return None
    
    @classmethod
    def query_all(cls) -> Iterable['Genre']:
        """
        全てのジャンルを取得する
        """
        if cls.genres is None:
            cls._load_all()
        assert cls.genres is not None
        return cls.genres.values()


class Odai:
    """
    お題

    Attributes
    ----------
    odai_id
        お題の ID．一意
    genre_id
        お題が属するジャンルの ID
    name
        お題の表示名
    filename
        お題に属する投票選択肢が記載されているファイルの名前
    """

    odai_id: str
    genre_id: str
    name: str
    filename: str

    def __init__(self, odai_id, genre_id, name, filename):
        self.odai_id = odai_id
        self.genre_id = genre_id
        self.name = name
        self.filename = filename
    
    def __str__(self):
        return self.name

    odais: Optional[Dict[str, 'Odai']] = None

    @classmethod
    def _load_all(cls):
        """全てのお題をファイルからメモリに読み込む"""
        with open('./icebreak_bot/db/odai.json') as file:
            odais_raw = json.load(file)
            cls.odais = {
                odai_raw["id"]: Odai(
                    odai_id=odai_raw["id"],
                    genre_id=odai_raw["genre_id"],
                    name=odai_raw["name"],
                    filename=odai_raw["filename"],
                )
                for odai_raw in odais_raw
            }

    @classmethod
    def from_id(cls, odai_id: str) -> Optional['Odai']:
        """
        お題の ID から Odai インスタンスを取得する
        """
        if cls.odais is None:
            cls._load_all()
        assert cls.odais is not None
        if odai_id in cls.odais:
            return cls.odais[odai_id]
        else:
            return None
    
    @classmethod
    def query(cls, genre: Genre) -> Iterable['Odai']:
        """
        ジャンルに属する全てのお題を取得する
        """
        if cls.odais is None:
            cls._load_all()
        assert cls.odais is not None
        return (odai for odai in cls.odais.values() if odai.genre_id == genre.genre_id)


class PollCandidate:
    """
    投票の選択肢

    Attributes
    ----------
    odai_id
        選択肢が属するお題の ID
    name
        選択肢の表示名
    """

    odai_id: str
    name: str

    def __init__(self, odai_id, name):
        self.odai_id = odai_id
        self.name = name
    
    def __str__(self):
        return self.name

    @staticmethod
    def query(odai: Odai) -> Iterable['PollCandidate']:
        """
        お題に属する全ての選択肢を取得する
        """
        with open(f'./icebreak_bot/poll/{odai.filename}.txt') as file:
            return [PollCandidate(odai_id=odai.odai_id, name=line.rstrip()) for line in file]

    @staticmethod
    def add(odai: Odai, name: str):
        """
        お題に選択肢を追加する
        """
        with open(f'./icebreak_bot/poll/{odai.filename}.txt', 'a') as file:
            file.write(f'\n{name}')
