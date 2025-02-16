# -*- coding: utf-8 -*-
"""TweetEval_sentiment_LLM

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/#fileId=https%3A//storage.googleapis.com/kaggle-colab-exported-notebooks/tweeteval-sentiment-llm-3debcf27-bb22-4191-a2bb-3ef7ee340269.ipynb%3FX-Goog-Algorithm%3DGOOG4-RSA-SHA256%26X-Goog-Credential%3Dgcp-kaggle-com%2540kaggle-161607.iam.gserviceaccount.com/20240410/auto/storage/goog4_request%26X-Goog-Date%3D20240410T073710Z%26X-Goog-Expires%3D259200%26X-Goog-SignedHeaders%3Dhost%26X-Goog-Signature%3D01c487cdf6b528dbc5c5235f435856cb01ed2d75f464c1cd1a60c1056ebab0a5d3282a9755fa2475ea30520dde7f71b1e400aa0b74d26aef1eda6f35637bab06bea02fe81a3e70d2ea2fd82765cfd07c1762230e0d636218a116d88a5d053d86938e9513f994360f5c7eb83986276f33b23a87ebd4d52dd53f15ba743076e01797d9ac916287c487eab76742dddbfb0c8d8f72d9149248c218ed1159b710ca0d0c670c10682379d61f9ff72127fb9e29b40d912f2230621d8f67c3cb56faa337ec2a3e470b7d6f0ac961e34b7d290d35f12c63829880d49e5fa990a812be319dfe6a32d73afd61f8523d92e7872886fe2a5a9e8ee20bf43e977ba88ce37a59a3
"""

!pip install transformers datasets

from datasets import load_dataset

# Load the sentiment analysis task from the TweetEval dataset
dataset = load_dataset("tweet_eval", "sentiment")

dataset

# 1. View dataset features
print("Features of the dataset:", dataset['train'].features)

print("Details of the first row in the training set:")
print(dataset['train'][0])

# Class Distribution
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import seaborn as sns

labels = dataset['train']['label']
label_counter = Counter(labels)

plt.figure(figsize=(7, 5))
sns.barplot(x=list(label_counter.keys()), y=list(label_counter.values()))
plt.title('Class Distribution')
plt.xlabel('Sentiment')
plt.ylabel('Number of Samples')
plt.show()

# Visualize word counts with a word cloud
all_text = ' '.join(dataset['train']['text'])
wordcloud = WordCloud(width=800, height=400).generate(all_text)

plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from collections import Counter

from transformers import AutoTokenizer

# Initialize the tokenizer with a pre-trained model
tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')

from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
from datasets import load_dataset
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# Load the tokenizer and model from Hugging Face
from transformers import AutoModelForSequenceClassification
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = AutoModelForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=3)

# Preprocess the data
def tokenize_function(examples):
    return tokenizer(examples['text'], padding='max_length', truncation=True)
tokenized_datasets = dataset.map(tokenize_function, batched=True)

# Split the data into training and validation sets
small_train_dataset = tokenized_datasets['train'].shuffle(seed=42).select(range(2000)) # smaller size for quicker training
small_eval_dataset = tokenized_datasets['test'].shuffle(seed=42).select(range(500))

!pip install transformers[torch] accelerate -U

import os
os.environ["WANDB_DISABLED"] = "true"

from transformers import Trainer, TrainingArguments
import numpy as np

training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./logs',
    evaluation_strategy='epoch',
    save_strategy="epoch",
    load_best_model_at_end=True,
)

def compute_metrics(pred):
    labels = pred.label_ids
    preds = np.argmax(pred.predictions, axis=1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='macro')
    acc = accuracy_score(labels, preds)
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=small_train_dataset,
    eval_dataset=small_eval_dataset,
    compute_metrics=compute_metrics,
)

trainer.train()
trainer.evaluate()

