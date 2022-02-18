### Required Libraries ###
from datetime import datetime
from functools import cached_property
from xmlrpc.client import _datetime_type
from dateutil.relativedelta import relativedelta

### Functionality Helper Functions ###
def parse_int(n):
    """
    Securely converts a non-integer value to integer.
    """
    try:
        return int(n)
    except ValueError:
        return float("nan")
        
def risk_type(intent_request):
    if intent_request == 'None':
        return '100% bonds(AGG), 0% equities(SPY)'
    elif intent_request == 'Very Low':
        return '80% bonds (AGG), 20% equities (SPY)'
    elif intent_request == 'Low':
        return '60% bonds (AGG), 40% equities (SPY)'
    elif intent_request == 'Medium':
        return '40% bonds (AGG), 60% equities (SPY)'
    elif intent_request == 'High':
        return '20% bonds (AGG)m 80% equities (SPY)'
    elif intent_request == 'Very High':
        return '0% bonds (AGG), 100% equities (SPY)'

def build_validation_result(is_valid, violated_slot, message_content):
    """
    Define a result message structured as Lex response.
    """
    if message_content is None:
        return {"isValid": is_valid, "violatedSlot": violated_slot}

    return {
        "isValid": is_valid,
        "violatedSlot": violated_slot,
        "message": {"contentType": "PlainText", "content": message_content},
    }
def validation_data(age, investment_amount, intent_request):
    '''Validates the data provided by the user'''
    # Validate that the user is greater than 0 years old or less than 65 years old
    if age is not None:
        birth_date = datetime.strptime(age, '%Y-%m-%d')
        age = relativedelta(datetime.now(), birth_date).years
        if age < 18:
            return build_validation_result(
                False,
                'age',
                'You should be greater than 0 or less than 65 years old to use this service, '
                'please provide a different date of birth.',
            )
    # Validate the investment amount is => 5000
    if cad_amount is not None:
        cad_amount = parse_float(
            cad_amount
        ) # Cast string to values
        if cad_amount <= 5000:
            return build_validation_result(
                False,
                'cadAmount',
                'The amount invest should be greater than zero, '
                'please adjust your investment amount.'
            )
    # A True result is returned if age or amount are valid
    return build_validation_result(True, None, None)

### Dialog Actions Helper Functions ###
def get_slots(intent_request):
    """
    Fetch all the slots and their values from the current intent.
    """
    return intent_request["currentIntent"]["slots"]


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    """
    Defines an elicit slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "ElicitSlot",
            "intentName": intent_name,
            "slots": slots,
            "slotToElicit": slot_to_elicit,
            "message": message,
        },
    }


def delegate(session_attributes, slots):
    """
    Defines a delegate slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {"type": "Delegate", "slots": slots},
    }


def close(session_attributes, fulfillment_state, message):
    """
    Defines a close slot type response.
    """

    response = {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": fulfillment_state,
            "message": message,
        },
    }

    return response


### Intents Handlers ###
def recommend_portfolio(intent_request):
    """
    Performs dialog management and fulfillment for recommending a portfolio.
    """

    first_name = get_slots(intent_request)["firstName"]
    age = get_slots(intent_request)["age"]
    investment_amount = get_slots(intent_request)["investmentAmount"]
    risk_level = get_slots(intent_request)["riskLevel"]
    source = intent_request["invocationSource"]

    if source == "DialogCodeHook":
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt
        # for the first violation detected.
        # Get all the slots
        slots = get_slots(intent_request)
        
        #Validate user input using the validate_data function
        validation_result = validation_data(age, investment_amount, intent_request)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None #Cleans invalid slot

       # Returns an elicitSlot dialogue to request new data for the invalid slot
            return elicit_slot(
                intent_request['sessionAttributes'],
                intent_request['currentIntent']['name'],
                slots,
                validation_result['violatedSlot'],
                validation_result['message']
            )

        # Fetch current session attibutes
        output_session_attributes = intent_request["sessionAttributes"]

        return delegate(output_session_attributes, get_slots(intent_request))

    # Get the initial investment recommendation
def recommend_portfolio(intent_request):
    # Dialogue management
    source = intent_request['invocationSource']
    #Get invocation source for dialogues
    if source == 'DialogCodeHook'
    # Validate inputs - Get all slots
    slots = get_slots(intent_request)
    # Get session attributes
    output_session_attributes = intent_request['sessionAttributes']
    # Return delegate dialogue to choose next action
    return delegate(output_session_attributes), get_slots(intent_request))
    
    recommend_portfolio = risk_type(intent_request)

    ### YOUR FINAL INVESTMENT RECOMMENDATION CODE ENDS HERE ###

    # Return a message with the initial recommendation based on the risk level.
    return close(
        intent_request["sessionAttributes"],
        "Fulfilled",
        {
            "contentType": "PlainText",
            "content": """{} thank you for your information;
            based on the risk level you defined, my recommendation is to choose an investment portfolio with {}
            """.format(
                first_name, initial_recommendation
            ),
        },
    )


### Intents Dispatcher ###
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    intent_name = intent_request["currentIntent"]["name"]

    # Dispatch to bot's intent handlers
    if intent_name == "RecommendPortfolio":
        return recommend_portfolio(intent_request)

    raise Exception("Intent with name " + intent_name + " not supported")


### Main Handler ###
def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """

    return dispatch(event)
