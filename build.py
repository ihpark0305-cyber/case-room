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

def render(cases_list, qa_obj=None):
    obj = dict(DATA_OBJ, cases=cases_list)
    if qa_obj is not None:
        obj = dict(obj, qa=qa_obj)
    payload = json.dumps(obj, ensure_ascii=False).replace("</script>", "<\\/script>")
    out = tpl.replace("__INTERVIEW_DATA__", payload)
    assert "__INTERVIEW_DATA__" not in out, "placeholder not replaced!"
    return out

def write(out, *names):
    for name in names:
        with open(os.path.join(HERE, name), "w", encoding="utf-8") as f:
            f.write(out)

def load_private(name, key):
    p = os.path.join(DATA, name)
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as f:
        return json.load(f).get(key, [])

# --- PUBLIC build: 공개 GitHub repo/Pages로 푸시되는 파일. *_private.json 미포함(저작권 안전). ---
pub = render(DATA_OBJ["cases"])
write(pub, "interview-prep.html", "index.html")
print("BUILT (public) interview-prep.html + index.html  (%.0f KB)" % (len(pub.encode("utf-8"))/1024))
print("  cases(public) : %d" % len(DATA_OBJ["cases"]))
print("  qa(public)    : %d" % len(DATA_OBJ["qa"]["qa"]))

# --- LOCAL build: data/*_private.json (소장 유료도서 등 개인 학습용) 을 합쳐 interview-prep-local.html 생성. ---
#     private 파일과 interview-prep-local.html 은 .gitignore 처리되어 공개 repo에 올라가지 않는다.
#     (개인 사적 이용만, 재배포 금지.)
priv_cases = load_private("cases_private.json", "cases")
priv_qa    = load_private("qa_private.json", "qa")
if priv_cases or priv_qa:
    local_cases = DATA_OBJ["cases"] + priv_cases
    local_qa    = {"qa": DATA_OBJ["qa"]["qa"] + priv_qa}
    loc = render(local_cases, qa_obj=local_qa)
    write(loc, "interview-prep-local.html")
    print("BUILT (LOCAL, gitignored) interview-prep-local.html  (%.0f KB)" % (len(loc.encode("utf-8"))/1024))
    print("  cases(local)  : %d (+%d private)" % (len(local_cases), len(priv_cases)))
    print("  qa(local)     : %d (+%d private)" % (len(local_qa["qa"]), len(priv_qa)))

print("  schedule  : %d days"  % len(DATA_OBJ["schedule"]["days"]))
print("  hospitals : %d"       % len(DATA_OBJ["hospitals"]["hospitals"]))
print("  reference : %d labs"   % len(DATA_OBJ["reference"]["labs"]))
