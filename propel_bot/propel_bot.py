import json

import boto3
import botocore

from settings import S3_BUCKET_NAME, GAINZ_FILE_NAME

s3_file_object = None


def get_s3_file_object():
    global s3_file_object
    if s3_file_object is None:

        s3 = boto3.resource(
            "s3",
            config=botocore.config.Config(connect_timeout=5, read_timeout=1)
        )
        s3_file_object = s3.Object(S3_BUCKET_NAME, GAINZ_FILE_NAME)
    return s3_file_object


def load_gainz_external_data():
    s3_file_object = get_s3_file_object()
    gainz_resp = s3_file_object.get()
    return json.loads(gainz_resp["Body"].read())


def save_gainz_external_data(data):
    s3_file_object = get_s3_file_object()
    s3_file_object.put(Body=json.dumps(data))


def clear():
    save_gainz_external_data({})

    return {
        'text': 'Scoreboard Reset',
        "response_type": "in_channel",
    }


def list_leaderboard():
    gainz_storage = load_gainz_external_data()
    tuples = [(person, points) for person, points in gainz_storage.items() if points > 0]
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
    gainz_storage = load_gainz_external_data()
    number = int(tokenized_values[1])
    users = tokenized_values[3:]
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

    save_gainz_external_data(gainz_storage)

    formatted_user_string = ''
    for user in users:
        formatted_user_string = '{} <{}>'.format(formatted_user_string, user)

    return {
        'text': '<{}> {} {} {} to{}'.format(
            acting_user,
            'gave' if give else 'took',
            number,
            'point' if number == 1 else 'points',
            formatted_user_string,
        ),
        "response_type": "in_channel",
    }


def handle_slack_request(data, other):
    print(data)
    acting_user = '@{}'.format(data['user_name'])
    command = data['command']
    text = data['text']
    tokenized = text.split(' ')

    if command == '/gainzbot' and 'give' in tokenized:
        return manage_points(acting_user, tokenized)
    elif command == '/gainzbot' and 'take' in tokenized:
        return manage_points(acting_user, tokenized, give=False)
    elif command == '/gainzbot' and 'list' in tokenized:
        return list_leaderboard()
    elif command == '/gainzbot' and 'clear' in tokenized:
        return clear()

    return 'Nothing to do'
