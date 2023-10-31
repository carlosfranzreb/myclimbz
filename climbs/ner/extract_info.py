"""
Given an audio file, transcribe it with Whisper and extract the following information
with string matching and the NER model:

- NAME (str): name of the climb (BERT).
- SECTOR (str): sector where the climb is located (BERT).
- GRADE (Grade): grade of the climb (BERT).
- GRADE_FELT (Grade): grade felt by the climber (BERT).
- N_TRIES (int): number of tries (BERT).
- LANDING (int): landing quality out of 10 (BERT).
- CRUX (list[str]): cruxes of the climb (BERT).
- HEIGHT (int): height of the climb (manual, succeeded by "meters").
- INCLINATION (int): inclination of the climb (manual, succeeded by "degrees").
- SIT_START (bool): whether the climb starts sitting or not (manual, inclusion of "sit").
- FLASH (bool): whether the climb was flashed (manual, inclusion of "flash").
- SEND (bool): whether the climb was sent or not (BERT).

Given a session report (str), it extracts:

- DATE (datetime): date of the session (BERT).
- AREA (str): area of the session (BERT).
- ROCK (str): rock type of the area (BERT).
- CONDITIONS (int): rating of the conditions out of 10 (BERT).

Projects are climbs where N_TRIES = 0.
"""


import torch
from whisper import Whisper
from climbs.ner.inference_model import ClimbsModel


TITLE_LABELS = ["NAME", "SECTOR", "AREA", "ROCK"]
INT_LABELS = ["N_TRIES", "LANDING", "INCLINATION", "CONDITIONS", "LANDING"]
FLOAT_LABELS = ["HEIGHT"]
BOOL_LABELS = ["SIT_START", "FLASH", "SEND"]


def transcribe(model: Whisper, audio_file: str) -> str:
    """Transcribe an audio file with Whisper."""
    return model.transcribe(audio_file)["text"]


def remove_punctuation(sentence: str, punctuation: str) -> str:
    """
    Remove punctuation from a sentence.
    """
    return sentence.translate(str.maketrans("", "", punctuation))


def parse_climb(model: ClimbsModel, report: str) -> dict[str, str]:
    """
    Extract information from a climb report, as described above.

    Args:
        model: NER model that predicts certain labels.
        report (str): climb report.

    Returns:
        dict[str, str]: dictionary of extracted information.
    """

    punctuation = ".,;:!?-()[]"
    report = report.translate(str.maketrans("", "", punctuation))
    out = dict()
    words = report.split()
    out = predict(model, report)

    if "AREA" not in out:
        out["SIT_START"] = "sit" in words
        out["FLASH"] = "flash" in report.lower()
        manual_labels = [("HEIGHT", "meter"), ("INCLINATION", "degree")]
        for key, suffix in manual_labels:
            suffix_idx = max(get_index(words, suffix), get_index(words, suffix + "s"))
            if suffix_idx > 0:
                out[key] = int(words[suffix_idx - 1])
    else:
        del out["SEND"]

    for key, value in out.items():
        out[key] = value.strip()

    for key in INT_LABELS:
        if key in out:
            out[key] = int(out[key])
    for key in FLOAT_LABELS:
        if key in out:
            out[key] = float(out[key])
    for key in BOOL_LABELS:
        if key in out:
            out[key] = out[key] == "True"
    for key in TITLE_LABELS:
        if key in out:
            out[key] = out[key].title()

    return out


def get_index(words: list[str], word: str) -> int:
    """Return the first index of a word in a list of words, or -1 if not found."""
    try:
        return words.index(word)
    except ValueError:
        return -1


def predict(model: ClimbsModel, text: str) -> dict[str, str]:
    """
    Predict the labels of a text with the given model. We assume that there is no
    punctuation in the text.

    Args:
        text (str): text to predict.

    Returns:
        dict mapping labels to their predicted values (ignoring the outside label "O").
    """

    tokens = model.tokenizer.tokenize(text)
    tokens = ["[CLS]"] + tokens + ["[SEP]"]
    ids = torch.tensor(model.tokenizer.convert_tokens_to_ids(tokens))
    mask = torch.ones(len(ids), dtype=torch.long)
    token_logits, text_logits = model.forward(ids.unsqueeze(0), mask.unsqueeze(0))
    active_logits = token_logits.view(-1, len(model.token_labels))
    token_pred = torch.argmax(active_logits, axis=1)

    out = {"SEND": (text_logits[0, 0] > text_logits[0, 1]).item()}
    prev_label = "O"
    for token, label_idx in zip(tokens, token_pred):
        label = model.token_labels[label_idx.item()]
        text = token[2:] if token.startswith("##") else " " + token
        if label == "O":
            continue
        elif label == prev_label:
            out[label] += text
        else:
            out[label] = text
        prev_label = label

    return out
