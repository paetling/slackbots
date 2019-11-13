from gainzbot import run_gainzbot


def handle_slack_request(data, other):
    print(data)
    acting_user = '@{}'.format(data['user_name'])
    command = data['command']
    text = data['text']
    tokenized = text.split(' ')

    if command == '/gainzbot':
        return run_gainzbot(acting_user, command, text, tokenized)

    return 'Nothing to do'
