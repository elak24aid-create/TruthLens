import requests
import time

urls = [
    'https://en.wikipedia.org/wiki/Earth',
    'https://www.reuters.com/legal/litigation/openai-says-ai-models-accessed-australian-government-systems-without-2026-09-29/',
    'https://www.usnews.com/news/world/articles/2026-09-28/thailand-expects-to-clear-bangkok-floodwater-in-two-to-three-days-government-says',
    'https://example.com/bad/url/does/not/exist/or/timeout/123'
]

for url in urls:
    print(f'Testing URL: {url}')
    try:
        res = requests.post('http://127.0.0.1:8000/api/check-url', json={'url': url}, timeout=60)
        data = res.json()
        print('STATUS:', res.status_code)
        if res.status_code == 200:
            print('VERDICT:', data.get('verdict'))
            print('EVIDENCE COUNT:', len(data.get('evidence', [])))
        else:
            print('ERROR:', data.get('detail'))
    except Exception as e:
        print('ERROR:', str(e))
    print('---')
