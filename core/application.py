
import json
from redis import Redis
from data.data_access import get_account_details, get_credit_card_details, get_transaction_details, seed_database
from infrastructure.openai_client import get_openai_client
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from transformers import pipeline

def translate(input_lang, target_lang, text):      
    pipe = pipeline("translation", model="facebook/nllb-200-distilled-1.3B")
    tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-1.3B")
    model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-1.3B")
    translation_pipeline = pipeline('translation', 
                                    model=model, 
                                    tokenizer=tokenizer, 
                                    src_lang=input_lang, 
                                    tgt_lang=target_lang, 
                                    max_length = 400)
    output = translation_pipeline(text)
    print(output[0]['translation_text'])


def get_account_details_handler(tool_call, arguments):
    account_number = arguments.get('account_number')
    account_details = get_account_details(account_number)

    function_call_result_message = {}

    function_call_result_message = {
        "role": "tool",
        "content": json.dumps({
            "account_number": account_number if account_details else "",
            "account_holder": account_details[2] if account_details else "",
            "balance": account_details[3] if account_details else "",
            "error": "" if account_details else "Account number doesn't exist"
        }),
        "tool_call_id": tool_call.id
    }

    return function_call_result_message

def get_transaction_details_handler(tool_call, arguments):
    account_number = arguments.get('account_number')
    transaction_details = get_transaction_details(account_number)

    function_call_result_message = {
        "role": "tool",
        "content": json.dumps(transaction_details) if transaction_details else "",
        "tool_call_id": tool_call.id,
        "error": "" if transaction_details else "Transaction history for given account number not found."
    }

    return function_call_result_message

def get_credit_card_details_handler(tool_call, arguments):
    credit_card_number = arguments.get('credit_card_number')
    credit_card_details = get_credit_card_details(credit_card_number)

    function_call_result_message = {
        "role": "tool",
        "content": json.dumps({
            "credit_card_number": credit_card_details[0] if credit_card_details else "",
            "card_holder": credit_card_details[1] if credit_card_details else "",
            "expiry_date": credit_card_details[2] if credit_card_details else "",
            "cvv": credit_card_details[3] if credit_card_details else "",
            "credit_limit": credit_card_details[4] if credit_card_details else "",
            "available_credit": credit_card_details[5] if credit_card_details else "",
            "error": "" if credit_card_details else "Credit Card number not found"
        }),
        "tool_call_id": tool_call.id
    }

    return function_call_result_message

def handle_tool_call(tool_call, arguments):
    function_name = tool_call.function.name
    switcher = {
        "get_account_details": get_account_details_handler,
        "get_transaction_details": get_transaction_details_handler,
        "get_credit_card_details": get_credit_card_details_handler
    }
    handler = switcher.get(function_name)
    if handler:
        return handler(tool_call, arguments)
    else:
        pass

# Define the function to get the response from the GPT-3 model
def get_response(conversationId, prompt):
    # Initialize the Redis client
    redis_client = Redis(host='redis-15085.c264.ap-south-1-1.ec2.redns.redis-cloud.com', port=15085, username='default', password='woRE0pEMsk5FOUiyqqNFW5M6Hf0Clmt6')
    system_prompt = {"role": "assistant", "content": "You are a helpful banking virtual assistant for a south african bank that helps customers with their banking needs. You are friendly, professional, and knowledgeable. You can help customers with a variety of banking tasks, such as checking their balance, transferring money, and finding the nearest ATM. You can also answer general banking questions and provide information about the bank's products and services. You are always ready to assist customers and provide them with the information they need to manage their finances. Here are some examples of the types of questions you can answer: 1. What is my current balance? 2. Can I transfer money between accounts? 3. Where is the nearest ATM? 4. What are the bank's hours of operation? 5. How can I apply for a loan? 6. What are the bank's interest rates? 7. How can I open a new account? 8. What is the bank's routing number? 9. How can I report a lost or stolen card? 10. What is the bank's customer service number? Please ask followup questions to user such as asking for details like account number. Use the supplied tools to assist the user only if required. Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous. Please always return data in tabular format if data is a list of objects."}
    message = {"role": "user", "content": prompt}

    conversation = redis_client.get(conversationId)
    if conversation:
        conversation_data = json.loads(conversation)
    else:
        conversation_data = []
        conversation_data.append(system_prompt)
        
    conversation_data.append(message)

    # print('-----------------------------------------------------')
    # print(conversation_data)
    # print('-----------------------------------------------------')
    redis_client.set(conversationId, json.dumps(conversation_data))   
    
    model_id = "gpt-4o-mini"
    response_format = { "type": "json_object" }

    tools = []
    with open('tools.json') as f:
        tools = json.load(f)

    client = get_openai_client()
    # Get the response from the GPT-4o model
    response = client.chat.completions.create(
        model=model_id,
        messages=conversation_data,
        tools=tools
    )
    response_dict = response.model_dump() 
    conversation_data.append(response_dict["choices"][0]["message"])
    redis_client.set(conversationId, json.dumps(conversation_data))

    tool_call_finish = response.choices[0].finish_reason == "tool_calls"

    # print the response to console
    print(response.choices[0])

    if tool_call_finish:
        tool_call = response.choices[0].message.tool_calls[0]
        arguments = json.loads(tool_call.function.arguments)

        # Call the handle_tool_call function
        function_call_result_message = handle_tool_call(tool_call, arguments)
        conversation_data.append(function_call_result_message)

        print('------------------AFTER TOOL-----------------------------------')
        print(conversation_data)
        print('-----------------------------------------------------')

        response = client.chat.completions.create(
            model=model_id,
            messages=conversation_data
        )
        response_dict = response.model_dump() 
        conversation_data.append(response_dict["choices"][0]["message"])
        redis_client.set(conversationId, json.dumps(conversation_data))

    # Return the response
    
    
    return response.choices[0].message.content

def get_app_conversation(conversation_id):
    # initialize the Redis client
    redis_client = Redis()
    # get the conversation from the Redis cache
    conversation = redis_client.get(conversation_id)
    return conversation

def seed_app_database():
    seed_database()

def is_message_flagged(input):
    client = get_openai_client()
    moderation_response = client.moderations.create(input=input)
    output = moderation_response.results[0]
    return output.flagged

def sanitize_input(user_input):
    # List of common malicious keywords to filter out
    blacklist_keywords = ["ignore", "disregard", "override", "forget previous", "stop", "delete", "forget"]
    
    # Check for blacklisted keywords
    for keyword in blacklist_keywords:
        if keyword in user_input.lower():
            raise ValueError("Potential prompt injection detected. Input is not allowed.")

    # Limit input length (e.g., 500 characters)
    if len(user_input) > 500:
        raise ValueError("Input is too long and might contain malicious content.")

    return user_input