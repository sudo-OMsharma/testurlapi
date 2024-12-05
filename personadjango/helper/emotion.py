import logging
from openai import OpenAI
from nltk.tokenize import word_tokenize
from django.http import JsonResponse
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from langdetect import detect

sid = SentimentIntensityAnalyzer()

def get_emotion(text):
    """
    Analyze the sentiment of the given text and return the corresponding emotion.

    Parameters:
    text (str): The text to analyze.

    Returns:
    str: The detected emotion, which can be one of the following: 
         'joy', 'excitement', 'contentment', 'neutral', 'sadness', 'anger', or 'despair'.
         Defaults to 'neutral' in case of an error.
    """
    try:
        sentiment = sid.polarity_scores(text)
        if sentiment['compound'] >= 0.75:
            return 'joy'
        elif sentiment['compound'] >= 0.5:
            return 'excitement'
        elif sentiment['compound'] >= 0.25:
            return 'contentment'
        elif sentiment['compound'] > 0:
            return 'neutral'
        elif sentiment['compound'] > -0.5:
            return 'sadness'
        elif sentiment['compound'] > -0.75:
            return 'anger'
        else:
            return 'despair'
    except Exception as e:
        logging.error(f"Error in getting emotions: {e}, defaulting to neutral emotion")
        return 'neutral'

def get_voice_settings(emotion):
    """
    Determine the voice settings based on the given emotion.

    Parameters:
    emotion (str): The emotion for which the voice settings are required. It should be one of the following:
                   'joy', 'excitement', 'contentment', 'neutral', 'annoyance', 'sadness', 'anger', or 'despair'.

    Returns:
    dict: A dictionary containing the voice settings:
          - 'stability' (float): The stability setting for the voice.
          - 'similarity_boost' (float): The similarity boost setting for the voice.
          - 'style' (float): The style setting for the voice.
          - 'use_speaker_boost' (bool): The speaker boost setting for the voice.
          Defaults to neutral settings in case of an error.
    """
    try:
        settings = {
            'stability': 0.5,
            'similarity_boost': 0.5,
            'style': 0.5,
            'use_speaker_boost': False
        }
        if emotion == 'joy':
            settings['stability'] = 0.8
            settings['similarity_boost'] = 0.7
            settings['style'] = 0.9
        elif emotion == 'excitement':
            settings['stability'] = 0.8
            settings['similarity_boost'] = 0.6
            settings['style'] = 0.9
        elif emotion == 'contentment':
            settings['stability'] = 0.8
            settings['similarity_boost'] = 0.7
            settings['style'] = 0.8
        elif emotion == 'neutral':
            settings['stability'] = 0.25
            settings['similarity_boost'] = 0.8
            settings['style'] = 0.3
        elif emotion == 'annoyance':
            settings['stability'] = 0.2
            settings['similarity_boost'] = 0.5
            settings['style'] = 0.8
        elif emotion == 'sadness':
            settings['stability'] = 0.1
            settings['similarity_boost'] = 0.5
            settings['style'] = 1.0
        elif emotion == 'anger':
            settings['stability'] = 0.2
            settings['similarity_boost'] = 0.4
            settings['style'] = 0.9
        elif emotion == 'despair':
            settings['stability'] = 0.3
            settings['similarity_boost'] = 0.5
            settings['style'] = 0.9

        return settings
    except Exception as e:
        logging.error(f"Error in getting voice settings: {e}, defualting to neutral settings")
        return {
            'stability': 0.5,
            'similarity_boost': 0.5,
            'style': 0.5,
            'use_speaker_boost': False
        }

def detect_language(text):
    """
    Detect the language of the given text.

    Parameters:
    text (str): The text for which the language needs to be detected.

    Returns:
    str: The detected language code (e.g., 'en' for English). 
         Returns None in case of an error.
    """

    try:
        return detect(text)
    except Exception as e:
        logging.error(f"Error detecting language: {e}")
        return None

def payload_return(text, language):
    """
    Prepare the payload for the Eleven Labs API request based on the given text and emotion.

    Parameters:
    text (str): The text to be synthesized.
    emotion (str): The emotion used to determine the voice settings.
    language (str): The language of the output text.
    toxic_filter (str): The toxic filter, whether to filter the answer or not

    Returns:
    dict: A dictionary containing the payload with the following keys:
          - 'text' (str): The text to be synthesized.
          - 'model_id' (str): The model ID for the Eleven Labs API.
          - 'voice_settings' (dict): The voice settings determined by the emotion.
          - 'seed' (None): Seed value for the API request.
          - 'language' (str): The detected or default language code.
    """
    try:
        # voice_settings = get_voice_settings(emotion)

        if not language:
            logging.warning("Language detection failed, using default language : english")
            language = "en"
        payload = {
            "answer": text,
            # "model_id": "eleven_multilingual_v2",
            # "voice_settings": voice_settings,
            # "seed": None,
            "language": language
        }
        return payload
    except Exception as e:
        language = "en"
        voice_settings = {
            'stability': 0.5,
            'similarity_boost': 0.5,
            'style': 0.5,
            'use_speaker_boost': False
        }
        payload = {
            "text": text,
            # "model_id": "eleven_multilingual_v2",
            # "voice_settings": voice_settings,
            # "seed": None,
            "language": language
        }
        logging.error("payload return parameters failed to load, defaulting to normal parameters.")
        return payload
