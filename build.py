# -*- coding: utf-8 -*-
"""
data/*.json (source of truth) + template.html (view)  ->  interview-prep.html (single self-contained file)
친구들이 파일만 열면 되도록 데이터를 inline 한다 (file:// 에서 fetch CORS 회피).
편집은 data/*.json 또는 template.html 에서 하고, `python build.py` 로 재생성.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)

bundle = {
    "cases":     load("cases.json"),
    "schedule":  load("schedule.json"),
    "hospitals": load("hospitals.json"),
    "qa":        load("qa.json"),
    "reference": load("reference.json"),
}
# flatten: window.DATA.cases is the array, etc.
DATA_OBJ = {
    "cases":     bundle["cases"]["cases"],
    "schedule":  bundle["schedule"],
    "hospitals": bundle["hospitals"],
    "qa":        bundle["qa"],
    "reference": bundle["reference"],
}

with open(os.path.join(HERE, "_template.html"), encoding="utf-8") as f:
    tpl = f.read()

payload = json.dumps(DATA_OBJ, ensure_ascii=False).replace("</script>", "<\\/script>")
out = tpl.replace("__INTERVIEW_DATA__", payload)

# interview-prep.html = 친구에게 파일로 보낼 때 / index.html = GitHub Pages가 서빙하는 파일
for name in ("interview-prep.html", "index.html"):
    with open(os.path.join(HERE, name), "w", encoding="utf-8") as f:
        f.write(out)

kb = len(out.encode("utf-8")) / 1024
print("BUILT interview-prep.html + index.html  (%.0f KB)" % kb)
print("  cases     : %d" % len(DATA_OBJ["cases"]))
print("  schedule  : %d days" % len(DATA_OBJ["schedule"]["days"]))
print("  hospitals : %d" % len(DATA_OBJ["hospitals"]["hospitals"]))
print("  qa        : %d" % len(DATA_OBJ["qa"]["qa"]))
print("  reference : %d labs" % len(DATA_OBJ["reference"]["labs"]))
assert "__INTERVIEW_DATA__" not in out, "placeholder not replaced!"
