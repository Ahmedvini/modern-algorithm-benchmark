from pathlib import Path
import json
e=Path("/content/mab_bounded_resume_20261011T024034091796Z_revision2/evidence/validation_commands")
for p in sorted(e.glob("*.json")):
 d=json.loads(p.read_text());print(p.name, d["exit_code"], d.get("status"), d.get("stdout", "")[-350:])
