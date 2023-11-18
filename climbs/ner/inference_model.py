import pytorch_lightning as pl
import torch
from transformers import BertModel
from transformers.models.auto.tokenization_auto import AutoTokenizer


TOKEN_LABELS = [
    "O",
    "GRADE",
    "GRADE_FELT",
    "NAME",
    "SECTOR",
    "CRUX",
    "LANDING",
    "N_ATTEMPTS",
    "AREA",
    "ROCK",
    "CONDITIONS",
    "DATE",
]
TEXT_LABELS = ["send", "no_send"]


class ClimbsModel(pl.LightningModule):
    def __init__(self):
        super().__init__()
        self.encoder = BertModel.from_pretrained("bert-base-uncased")
        self.tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
        self.token_labels = TOKEN_LABELS
        self.text_labels = TEXT_LABELS
        self.token_classifier = torch.nn.Linear(
            self.encoder.config.hidden_size, len(self.token_labels)
        )
        self.text_classifier = torch.nn.Linear(
            self.encoder.config.hidden_size, len(self.text_labels)
        )

    def forward(self, x, masks):
        enc_out = self.encoder(x, attention_mask=masks)
        token_logits = self.token_classifier(enc_out[0])
        text_logits = self.text_classifier(enc_out[1])
        return token_logits, text_logits
