import gzip, json, correctionlib

FILE = "jsonpog-integration/POG/EGM/2023_Summer23BPix/electronID.json.gz"
CORR = "Electron-ID-SF"

# Runtime API (for inputs + evaluation)
cs = correctionlib.CorrectionSet.from_file(FILE)
c = cs[CORR]

print("Inputs (in order):")
for i, inp in enumerate(c.inputs):
    # inp.type is e.g. "string" or "real"
    print(f"  {i}: {inp.name} ({inp.type})")

# ------- OPTIONAL: show valid categorical keys + numeric bin edges -------

with gzip.open(FILE, "rt") as f:
    raw = json.load(f)

def content_map(cat_node):
    cont = cat_node["content"]
    if isinstance(cont, dict):
        return cont
    if isinstance(cont, list):
        return {e["key"]: e["value"] for e in cont}
    raise TypeError("Unknown content type")

# pick the correction in the raw schema
corr = next(cc for cc in raw["corrections"] if cc["name"] == CORR)

# years / eras
years_map = content_map(corr["data"])
years = list(years_map.keys())
print("years:", ", ".join(years))

# ValType under first year
YEAR = years[0]
val_map = content_map(years_map[YEAR])
valtypes = list(val_map.keys())
print(f"ValType[{YEAR}]:", ", ".join(valtypes))

# WorkingPoint under (YEAR, ValType)
VAL = valtypes[0]
wp_map = content_map(val_map[VAL])
wps = list(wp_map.keys())
print(f"WorkingPoint[{YEAR}/{VAL}]:", ", ".join(wps))

# bin edges for numeric axes (eta/pt)
def collect_binnings(node, out):
    if isinstance(node, dict) and node.get("nodetype") == "binning":
        out[node["input"]] = node["edges"]
    cont = node.get("content")
    if isinstance(cont, list):
        for e in cont:
            collect_binnings(e["value"], out)
    elif isinstance(cont, dict):
        collect_binnings(cont, out)

edges = {}
collect_binnings(corr["data"], edges)
for var, ed in edges.items():
    print(f"{var} edges:", ed)

