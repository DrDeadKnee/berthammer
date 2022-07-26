def choose(question, choices):
    user_prompt = question + " (q to quit)"

    for idx, option in enumerate(choices):
        user_prompt += f"\n{idx + 1}\t{option}"
    user_prompt += "\n> "
    response = input(user_prompt)
    _check_q(response)

    try:
        choice = choices[int(response) - 1]
        return choice

    except (ValueError, IndexError):
        print(f"{response} is not an option.")
        return choose(question, choices)


def keepon(prompt=None):
    if prompt is None:
        prompt = "any key to continue..."

    prompt += "(q to quit)\n> "
    response = input(prompt)
    _check_q(response)

    return None


def _check_q(response):
    if response.lower() in ["q", "quit"]:
        exit()
