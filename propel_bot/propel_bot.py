import json

from flask import Flask, request, jsonify
import redis

from settings import REDIS_HOST, USE_REDIS

if USE_REDIS:
    redis_connection = redis.Redis(host=REDIS_HOST, port=6379, db=0)
app = Flask(__name__)

gainz_storage = {}


def load_storage_from_redis():
    if not USE_REDIS:
        return

    global gainz_storage
    loaded_value = redis_connection.get('gainz_storage')
    gainz_storage = json.loads(loaded_value)


def save_storage_to_redis():
    if not USE_REDIS:
        return

    global gainz_storage
    redis_connection.set('gainz_storage', json.dumps(gainz_storage))


@app.route('/health')
def health():
    return 'YES'


@app.route('/', methods=['POST'])
def give_point():
    acting_user = '@{}'.format(request.form['user_name'])
    command = request.form['command']
    text = request.form['text']
    tokenized = text.split(' ')

    if command == '/gainz_give':
        return jsonify(manage_points(acting_user, tokenized))
    elif command == '/gainz_take':
        return jsonify(manage_points(acting_user, tokenized, give=False))
    elif command == '/gainz_list':
        return jsonify(list_leaderboard())
    elif command == '/gainz_reset':
        return jsonify(reset())

    return 'Nothing to do'


def reset():
    global gainz_storage
    gainz_storage = {}

    return {
        'text': 'Scoreboard Reset',
        "response_type": "in_channel",
    }


def list_leaderboard():
    global gainz_storage
    tuples = [(k, v) for k, v in gainz_storage.items()]
    tuples.sort(key=lambda item: item[1], reverse=True)

    return_string = 'Scoreboard:\n'
    for i, item in enumerate(tuples):
        return_string += '{}. <{}>: {} {}\n'.format(
            i + 1,
            item[0],
            item[1],
            'point' if item[1] == 1 else 'points'
        )

    return {
        'text': return_string,
        "response_type": "in_channel"
    }


def manage_points(acting_user, tokenized_values, give=True):
    global gainz_storage
    number = int(tokenized_values[0])
    users = tokenized_values[2:]
    if len(users) == 0:
        return {'text': 'You must specify who to give points to'}
    elif (acting_user in users):
        return {'text': 'You cannot {} yourself! Wait for a friend :)'.format(
            'give points to' if give else 'take points from'
        )}
    for user in users:
        if '@' not in user:
            return {'text': 'You must use slack usernames: @<username>\n{} not valid'.format(user)}

    for user in users:
        gainz_storage.setdefault(user, 0)
        if give:
            gainz_storage[user] += number
        else:
            gainz_storage[user] -= number

    formatted_user_string = ''
    for user in users:
        formatted_user_string = '{} <{}>'.format(formatted_user_string, user)

    return {
        'text': '<{}> gave {} {} to{}'.format(
            acting_user,
            number,
            'point' if number == 1 else 'points',
            formatted_user_string,
        ),
        "response_type": "in_channel",
    }


load_storage_from_redis()

if __name__ == "__main__":
    app.run(port=5000)
