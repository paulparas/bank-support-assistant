from flask import Flask, app, jsonify, request, g
from flasgger import Swagger
from core.application import get_app_conversation, get_response, is_message_flagged, sanitize_input, seed_app_database

app = Flask(__name__)
swagger = Swagger(app)

@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/conversation/<conversationId>', methods=['GET'])
def get_conversation(conversationId):
    """
    Get the conversation
    ---
    parameters:
      - name: conversationId
        in: path
        type: string
        required: true
    responses:
      200:
        description: The conversation
        schema:
          type: object
          properties:
            conversation:
              type: array
    """
    # get the conversation id from the route
    conversation_id = conversationId
    
    # return the conversation
    return get_app_conversation(conversation_id)

@app.route('/conversation/<conversationId>', methods=['POST'])
def create_conversation(conversationId):
    """
    Create or update a conversation
    ---
    parameters:
      - name: conversationId
        in: path
        type: string
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            message:
              type: string
    responses:
      200:
        description: The response from the GPT-3 model
        schema:
          type: object
          properties:
            response:
              type: string
    """
    # get the conversation data from the request
    conversation_data = request.get_json()
    # get the conversation id from the route
    try:
      conversation_id = conversationId
      # get the message from the conversation data
      message = conversation_data['message']

      if is_message_flagged(message):
        return "I'm sorry, I can't help with that."
      
      message = sanitize_input(message)
      
      # get the response from the GPT-4o model
      response = get_response(conversation_id, message)

      if is_message_flagged(response):
        return "I'm sorry, I can't help with that."
    except ValueError:
      # Handle the ValueError here
      return "I'm sorry, I can't help with that."
    # return the response
    return response

if __name__ == "__main__":
    #seed_app_database()
    app.run(debug=True)