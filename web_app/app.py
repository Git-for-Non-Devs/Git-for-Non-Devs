from flask import Flask, render_template, request, jsonify
import openai
import os
import requests
import re
from dotenv import load_dotenv
import json
import pandas as pd
import logging
from datetime import datetime

# TODO :: For dev
# import sys; print('Python %s on %s' % (sys.version, sys.platform))
# sys.path.extend(['/Users/kilian.lehn/GitHub/Git-for-Non-Devs/web_app'])
# dotenv_path = 'secrets/.env'
# load_dotenv(dotenv_path)

load_dotenv()
app = Flask(__name__)


# OPENAI_API_KEY = os.environ.get('OPEN_AI_KEY')
openai.api_key = os.environ.get('OPEN_AI_KEY')
print(openai.api_key)


current_time = datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')
local_log_file_name = f'logs_{current_time}.log'
logging.basicConfig(filename='temp_local/' + 'log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

logging.info('Logging started')


def create_graph_data(prompt, text):
    responses = text.split('\n')
    nodes = [{'id': 1, 'label': prompt}]
    edges = []

    for idx, response in enumerate(responses, start=2):
        nodes.append({'id': idx, 'label': response})
        if idx == 2:
            edges.append({'from': 1, 'to': idx})
        else:
            edges.append({'from': idx - 1, 'to': idx})

    return {'nodes': nodes, 'edges': edges}


def get_embedding(text, model="text-embedding-ada-002"):
    openai.api_key = os.environ.get('OPEN_AI_KEY')
    text = text.replace("\n", " ")
    logging.info(text)
    return openai.Embedding.create(input=[text], model=model)['data'][0]['embedding']


def generate_text(prompt, freshness, frequency_penalty, max_tokens, model_id):
    OPENAI_API_URL = "https://api.openai.com/v1/engines/" + model_id + "/completions"
    data = {
        'prompt': prompt,
        'temperature': float(freshness),
        'frequency_penalty': float(frequency_penalty),
        'max_tokens': int(max_tokens),
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {openai.api_key}',
    }
    response = requests.post(OPENAI_API_URL, json=data, headers=headers)
    if response.status_code != 200:
        return {'error': 'Failed to generate text'}
    try:
        response_data = response.json()
        choices = response_data['choices']
        text = choices[0]['text']
        unwanted_characters = r'[@#€]'  # Add any other unwanted characters inside the brackets
        text = re.sub(unwanted_characters, '', text)
        text = re.sub(r'\n+', '\n', text)  # Remove consecutive occurrences of '\n'

        # Get embeddings for the prompt, text (completion), and concatenated text
        prompt_embedding = get_embedding(prompt)
        text_embedding = get_embedding(text)
        concat_text = prompt + " " + text
        concat_text_embedding = get_embedding(concat_text)

        # Save the information in a pandas DataFrame
        df = pd.DataFrame(columns=['prompt_embedding', 'text_embedding', 'concat_text_embedding', 'concat_text'])
        df = df.append({
            'prompt_embedding': prompt_embedding,
            'text_embedding': text_embedding,
            'concat_text_embedding': concat_text_embedding,
            'concat_text': concat_text
        }, ignore_index=True)

        df.to_csv('embeddings.csv')

        graph_data = create_graph_data(prompt, text)
        graph_data_json = json.dumps(graph_data)

        return text
    except KeyError:
        return {'error': 'Invalid response from OpenAI'}


@app.route('/get_completion', methods=['POST'])
def get_completion():
    prompt = request.json['prompt']
    freshness = request.json['freshness']
    frequency_penalty = request.json['frequency_penalty']
    max_tokens = request.json['max_tokens']
    model_id = request.json['model_id']

    generated_text = generate_text(prompt, freshness, frequency_penalty, max_tokens, model_id)
    print(generated_text)
    logging.info(generated_text)
    return jsonify({"text": generated_text})


@app.route('/playground')
def playground():
    models = openai.Model.list()
    model_options = [{'label': model['id'], 'value': model['id']} for model in models['data']]
    return render_template('playground.html', model_options=model_options)

@app.route('/app_overview')
def app_overview():
    return render_template('app_overview.html')

@app.route('/')
def index():
    print('index')
    return render_template('app_overview.html')



@app.route('/update_nodes', methods=['POST'])
def update_nodes():
    text = request.json['text']
    graph_data = create_graph_data('Start', text)
    return jsonify(graph_data)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
