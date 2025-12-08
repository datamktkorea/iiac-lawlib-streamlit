"""임베딩 생성 및 전처리 모듈.

이 모듈은 단어 임베딩을 로드하고, 텍스트 시퀀스를 인코딩 및 패딩하는 기능을 제공합니다.
"""

import json

import numpy as np
from tensorflow.keras.preprocessing import sequence

__all__ = ["load_embedding", "load_vocab", "encoding_and_padding"]


def load_embedding(embeddings_file):
    """임베딩 파일을 로드합니다.

    Args:
        embeddings_file (str): 임베딩 파일 경로.

    Returns:
        numpy.ndarray: 로드된 임베딩 배열.
    """
    return np.load(embeddings_file)


def load_vocab(vocab_path):
    """단어 사전을 로드합니다.

    Args:
        vocab_path (str): 단어 사전 파일 경로.

    Returns:
        tuple: (word2idx, idx2word) 딕셔너리 튜플.
    """
    with open(vocab_path) as f:
        data = json.loads(f.read())
    word2idx = data
    idx2word = dict([(v, k) for k, v in data.items()])
    return word2idx, idx2word


def encoding_and_padding(word2idx_dic, sequences, **params):
    """텍스트 시퀀스를 인덱스로 변환하고 패딩을 적용합니다.

    1. 항목을 인덱스로 변환
    2. 패딩 적용

    Args:
        word2idx_dic (dict): 단어를 인덱스로 매핑하는 사전.
        sequences (list): 시퀀스들의 리스트 (각 요소는 시퀀스).
        **params:
            maxlen (int): 최대 길이.
            dtype: 결과 시퀀스의 데이터 타입.
            padding (str): 'pre' 또는 'post'. 시퀀스 앞 또는 뒤에 패딩.
            truncating (str): 'pre' 또는 'post'. maxlen보다 긴 시퀀스의 앞 또는 뒤를 자름.
            value (float): 패딩에 사용할 값.

    Returns:
        numpy.ndarray: 패딩된 시퀀스 배열 (float32).
    """
    seq_idx = [[word2idx_dic.get(a, word2idx_dic["__ETC__"]) for a in i] for i in sequences]
    params["value"] = word2idx_dic["__PAD__"]
    return sequence.pad_sequences(seq_idx, **params).astype("float32")
