from types import SimpleNamespace as ns
from typing import List


def parse(message: str):
    details = False
    if message.endswith('?'):
        details = True
        message = message[:-1]

    components = is_this_for_me(message)

    if not components:
        return None

    if components == ['apua']:
        return ns(action='apua')

    modifier = 0

    try:
        modifier = int(components[-1])
        components = components[:-1]
    except IndexError:
        return
    except ValueError:
        pass

    try:
      if components[-1] in ('+', '-'):
          if components[-1] == '-':
              modifier = -modifier
          components = components[:-1]
    except IndexError:
      return

    move = ' '.join(components)

    if not move:
      return

    return ns(
      action='move',
      move=move,
      modifier=modifier,
      details=details,
    )


def is_this_for_me(message: str) -> List[str]:
    message = message.lower()
    components = message.split()

    if not components or components[0] != 'a':
        return []
    elif len(components) == 1:
        return ['apua']
    else:
        return components[1:]
