from utils import load_s3_data, save_s3_data
from settings import GAINZ_FILE_NAME


def clear():
    save_s3_data(GAINZ_FILE_NAME, {})

    return {
        'text': 'Scoreboard Reset',
        "response_type": "in_channel",
    }


def list_leaderboard():
    gainz_storage = load_s3_data(GAINZ_FILE_NAME)
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
    gainz_storage = load_s3_data(GAINZ_FILE_NAME)
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

    save_s3_data(GAINZ_FILE_NAME, gainz_storage)

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


def run_gainzbot(acting_user, command, text, tokenized):
    if 'give' in tokenized:
        return manage_points(acting_user, tokenized)
    elif 'take' in tokenized:
        return manage_points(acting_user, tokenized, give=False)
    elif 'list' in tokenized:
        return list_leaderboard()
    elif 'clear' in tokenized:
        return clear()
