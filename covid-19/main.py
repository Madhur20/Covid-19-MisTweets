from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel
import os
from transformers import BertTokenizer
import pytorch_lightning as pl
from transformers import BertModel, BertConfig
from torch import nn
import torch
 

app = FastAPI()

# origins = [
#     "http://localhost",
#     "http://localhost:8000"
#     "http://localhost:8080",
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# load this at the start of your API ONCE
class CovidTwitterStanceModel(pl.LightningModule):
  def __init__(self, pre_model_name, threshold=0.8):
    super().__init__()
    self.pre_model_name = pre_model_name
    self.threshold = threshold
    self.config = BertConfig.from_pretrained(pre_model_name)
    self.bert = BertModel(self.config)
    self.score_func = torch.nn.Softmax(dim=-1)
    self.classifier = nn.Linear(self.config.hidden_size,3)
 
  def get_predictions(self, logits, threshold):
    probs = self.score_func(logits)
    pos_probs = probs[:, 1:]
    pos_probs = pos_probs * ((pos_probs > threshold).float())
    pos_any_above = ((pos_probs > threshold).int().sum(dim=-1) > 0).int()
    pos_predictions = (pos_probs.max(dim=-1)[1] + 1)
    predictions = pos_predictions * pos_any_above
    return probs, predictions
 
  def forward(self, input_ids, attention_mask, token_type_ids):
    outputs = self.bert(
        input_ids,
        attention_mask=attention_mask,
        token_type_ids=token_type_ids
    )
    contextualized_embeddings = outputs[0]
    classifier_inputs = contextualized_embeddings[:, 0]
    logits = self.classifier(classifier_inputs)
    probs, preds = self.get_predictions(logits, self.threshold)
    return probs, preds
 
 
model_path = '/Users/madhurjajoo/Desktop/Spring 2022/CS 4V98/model/stance-cvfl-HLTRI_COVID_LIES_STANCE_ds-cvfl-v1'
labels = {
  0: "Not Relevant",
  1: "Accept",
  2: "Reject"
}
mists = {
 'CVF-F18': 'The COVID-19 vaccine interacts with human DNA such as altering DNA with RNA.',
 'CVF-F3': 'The COVID vaccine renders pregnancies risky and unsafe for unborn babies by causing causes infertility or miscarriages.',
 'CVL-4': "The COVID-19 vaccine causes Bell's palsy.",
 'CVL-7': 'The COVID-19 vaccine contains tissue from aborted fetuses.',
 'CVF-F39': 'The COVID-19 Vaccine is a satanic plan to microchip people by controling the general population either through microchip tracking or nanotransducers in our brains.',
 'CVL-9': 'More people will die as a result of a negative side effect to the COVID-19 vaccine than would actually die from the coronavirus.',
 'CVL-10': 'There are severe side effects of the COVID-19 vaccines, worse than having the virus.',
 'CVF-F23': 'The COVID-19 vaccines have not been tested for at least 5 years, as they should, and are therefore not safe experimentation.',
 'CVF-F36': 'The COVID-19 Vaccine contains unsafe toxins which are injected into your bloodstream such as formaldehyde, mercury aluminum, or the spike protein.',
 'CVF-F26': 'COVID-19 Vaccines using mRNA override and destroy the immune system by stopping the natural immune system from fighting every other disease.',
 'CVF-F27': "COVID-19 Vaccines are gene modifying injections which make children's immune system attack organs, including brain and will kill you."
}
 
 
model = CovidTwitterStanceModel(model_path)
model.load_state_dict(torch.load(os.path.join(model_path, 'pytorch_model.bin')))
model.eval()
tokenizer = BertTokenizer.from_pretrained(model_path)

def run_model(text):
  m_preds = {}
  for m_id, m_text in mists.items():
    batch = tokenizer(m_text, text, truncation='only_second', max_length=512, return_tensors='pt')
    probs, preds = model(**batch)
    probs = probs[0].tolist()
    pred = labels[preds[0].item()]
    if pred != 'Not Relevant':
      m_preds[m_id] = {'text': m_text, 'stance': pred, 'prob': probs}
  return m_preds

class Item(BaseModel):
    prob: str
    pred: str
    # is_offer: Optional[bool] = None


@app.get("/mist/{text}")
def read_item(text: str):
    return run_model(text)
