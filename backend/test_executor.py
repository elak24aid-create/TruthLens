from app.services.online_research import check_identity, perform_online_research
import sys

print("Wiki:", check_identity("The Sun is a star."))
res = perform_online_research("The Sun is a star.")
print("Research count:", len(res))
for r in res:
    print(r.title, r.relationship, r.publisher)
