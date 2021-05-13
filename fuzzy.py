import re

def fuzzyfinder(input, collection, accessor=lambda x: x, sort_results=True):
    suggestions = []
    input = str(input) if not isinstance(input, str) else input
    pat = '.*?'.join(map(re.escape, input))
    pat = '(?=({0}))'.format(pat)
    regex = re.compile(pat, re.IGNORECASE)
    for item in collection:
        r = list(regex.finditer(accessor(item)))
        if r:
            best = min(r, key=lambda x: len(x.group(1)))
            suggestions.append((len(best.group(1)), best.start(), accessor(item), item))
    if suggestions:
      if sort_results:
          return next(z[-1] for z in sorted(suggestions))
      else:
          return next(z[-1] for z in sorted(suggestions, key=lambda x: x[:2]))
