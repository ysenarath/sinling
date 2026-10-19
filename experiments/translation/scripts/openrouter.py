"""A minimal OpenRouter chat client with a response cache and a hard spending cap.

Every response is cached by model and prompt, so re-running an experiment costs nothing. The cost
OpenRouter reports for each call is added to data/spend.json, and no call is made once the total
reaches the cap.
"""

import hashlib
import json
import os
import threading
import time
import urllib.error
import urllib.request

from common import DATA

URL = 'https://openrouter.ai/api/v1/chat/completions'
CAP_USD = float(os.environ.get('TRANSLATION_BUDGET_USD', '5.0'))
CACHE = DATA / 'cache'
SPEND = DATA / 'spend.json'
_lock = threading.Lock()


class BudgetExceeded(RuntimeError):
    pass


def spent():
    with _lock:
        return _read_spend()


def _read_spend():
    return json.loads(SPEND.read_text())['usd'] if SPEND.exists() else 0.0


def _add_spend(usd):
    with _lock:
        total = _read_spend() + usd
        SPEND.parent.mkdir(parents=True, exist_ok=True)
        tmp = SPEND.with_suffix('.tmp')
        tmp.write_text(json.dumps({'usd': total, 'cap': CAP_USD}))
        os.replace(tmp, SPEND)  # atomic, so a reader never sees a half-written file
        return total


def chat(model, messages, *, max_tokens=2048, temperature=0.0):
    """Return (text, cost_usd, cached) for one chat completion."""
    body = {'model': model, 'messages': messages, 'max_tokens': max_tokens, 'temperature': temperature,
            'usage': {'include': True}}
    # Translation needs no hidden reasoning, which costs tokens and can use up max_tokens.
    body['reasoning'] = {'effort': 'minimal'} if model.startswith('openai/gpt-5') else {'enabled': False}
    # Only route to providers that honour every setting above (some ignore the reasoning switch).
    body['provider'] = {'require_parameters': True}
    key = hashlib.sha256(json.dumps(body, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    path = CACHE / model.replace('/', '__') / f'{key}.json'
    if path.exists():
        cached = json.loads(path.read_text(encoding='utf-8'))
        return cached['text'], cached['cost'], True

    if spent() >= CAP_USD:
        raise BudgetExceeded(f'spending cap of ${CAP_USD:.2f} reached')
    request = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={
        'Authorization': f'Bearer {os.environ["OPENROUTER_API_KEY"]}',
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://github.com/ysenarath/sinling',
        'X-Title': 'Sinling translation experiment',
    })
    for attempt in range(6):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                data = json.load(response)
            break
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < 5:
                time.sleep(2 ** attempt * 3)
                continue
            raise RuntimeError(f'{model}: HTTP {e.code}: {e.read()[:300]!r}') from e
        except (urllib.error.URLError, TimeoutError):
            if attempt < 5:
                time.sleep(2 ** attempt * 3)
                continue
            raise
    if 'choices' not in data:
        raise RuntimeError(f'{model}: unexpected response {str(data)[:300]}')
    text = (data['choices'][0]['message'].get('content') or '').strip()
    cost = float(data.get('usage', {}).get('cost', 0.0))
    _add_spend(cost)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({'text': text, 'cost': cost, 'usage': data.get('usage')}, ensure_ascii=False),
                    encoding='utf-8')
    return text, cost, False
