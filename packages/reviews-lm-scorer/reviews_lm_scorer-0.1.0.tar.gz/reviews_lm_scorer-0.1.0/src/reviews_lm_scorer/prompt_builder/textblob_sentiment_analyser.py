from textblob import TextBlob
from typing import Dict
import nltk


class TextBlobSentimentAnalyser:

    def __init__(self):
        self._check_corpora()

    def _check_corpora(self) -> None:

        required_corpora = ['punkt', 'averaged_perceptron_tagger', 'brown']
        
        for corpora in required_corpora:
            try:
                if corpora == 'punkt':
                    nltk.data.find(f'tokenizers/{corpora}') 
                else:
                    nltk.data.find(f'corpora/{corpora}')
            except LookupError:
                nltk.download(corpora)

    def analyse(self, text: str, **kwargs) -> Dict[str, float]:

        if not text or not isinstance(text, str):
            raise TypeError("Invalid Input: Text must in the string format.")
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            return {
                'polarity': polarity,
                'subjectivity': subjectivity,
            }
            
        except Exception as e:
            raise RuntimeError(f"Sentiment Analysis Failed: {str(e)}")



