from ddgs import DDGS
import time

def get_answer(q):
    print(f"--- {q} ---")
    with DDGS() as ddgs:
        try:
            results = list(ddgs.text(q, max_results=3))
            for res in results:
                print(res['title'])
                print(res['body'])
                print()
        except Exception as e:
            print(e)
            
get_answer("Who is the president of the United States?")
get_answer("Who is Michael Jackson?")
