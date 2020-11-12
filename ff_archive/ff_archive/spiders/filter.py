
import json
out_dir = "C:/Users/obaid/Py Projects/ffarchive_py/ff_archive/ff_archive/spiders/"
with open(out_dir + "UserData.jsonl", "r") as dump_file:
    L = dump_file.readlines()
newer_dump = ""
for line in L:
    user = json.loads(line)
    if (user["total_favs"] < 300) and (user["total_follows"] < 300):
        continue
    if user["total_stories"] > 2 and user["total_favs"] < 600 and user["total_follows"] < 600:
        continue
    newer_dump += json.dumps(user) + "\n"
with open(out_dir + "UserDataFiltered.jsonl", "w+") as dump_file:
    dump_file.write(newer_dump)