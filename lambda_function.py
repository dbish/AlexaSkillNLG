import nltk
from random import randint
import cPickle as pickle

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to sentence helper " \
                    "Please start a sentence and I'll say the next word to continue it, we can build a story together, mad-lib style. "
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me a word to " \
                    "start the sentence."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the sentence helper " \
                    "Have a giraffe day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def create_sentence_attributes(favorite_color):
    return {"favoriteColor": favorite_color}

def add_to_sentence(intent, session):
    """ Sets the color in the session and prepares the speech to reply to the
    user.
    """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'Word' in intent['slots']:
        if session.get('attributes', {}) and "sentence" in session.get('attributes', {}):
            sentence = session['attributes']['sentence'] +" "+intent['slots']['Word']['value']
        else:
            sentence = intent['slots']['Word']['value']
        print(sentence)
        print(intent['slots']['Word']['value'])
        sentence = chooseNextWord(sentence)
        print(sentence)
        print(intent['slots']['Word']['value'])
        session_attributes = create_sentence_attributes(sentence)


        speech_output = "Ok here's what I have: " + \
                        sentence + \
                        ". You can build on this sentence by giving me the next word"
        reprompt_text = "You can build on this sentence by giving me the next word"
    else:
        speech_output = "I'm not sure what word you want to add to the sentence " \
                        "Please try again."
        reprompt_text = "I'm not sure what word you want to add to the sentence. " \
                        "You can tell me a sentence or word for me to continue in a fun way."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "AddToSentenceIntent":
        return add_to_sentence(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here




def chooseNextWord(sentence):
    #freq_brown = nltk.FreqDist(brown.words())
    pkl_file = open('bigrams.pkl', 'rb')

    cfreq_brown_2gram = pickle.load(pkl_file)

    words = sentence.split()


    if len(words) > 1:
        topWords = cfreq_brown_2gram[words[-1]].most_common(100)
    else:
        topWords = cfreq_brown_2gram[words[0]].most_common(100)

    nextWord = topWords[randint(0, len(topWords))]

    return sentence  + " " + nextWord[0]


def lambda_handler(event, context):
    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])

