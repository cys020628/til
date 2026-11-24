"""노트(.md)의 ```kotlin 블록을 추출해 블록별로 컴파일·실행하고 결과를 리포트로 저장한다.

사용: python -I verify_notes.py <작업폴더> <노트1.md> [<노트2.md> ...]
환경변수 KOTLIN_HOME: kotlinc 설치 폴더 (bin/kotlinc, lib/kotlin-stdlib.jar가 있는 곳)
결과: <작업폴더>/report.json
"""
import concurrent.futures as cf
import json
import os
import re
import subprocess
import sys
from pathlib import Path

KOTLIN_HOME = Path(os.environ["KOTLIN_HOME"])
KOTLINC = KOTLIN_HOME / "bin" / ("kotlinc.bat" if os.name == "nt" else "kotlinc")
STDLIB = KOTLIN_HOME / "lib" / "kotlin-stdlib.jar"


def extract_blocks(md_path):
    text = Path(md_path).read_text(encoding="utf-8")
    blocks = []
    for m in re.finditer(r"```kotlin\n(.*?)\n```", text, flags=re.S):
        line_no = text[: m.start()].count("\n") + 1
        blocks.append((line_no, m.group(1)))
    return blocks


def expected_outputs(code):
    """println 줄 끝의 `// 값` 주석을 기대값으로 모은다."""
    exp = []
    for line in code.splitlines():
        if "println(" in line or "print(" in line:
            m = re.search(r"//\s*(.+)$", line)
            if m:
                exp.append(m.group(1).strip())
    return exp


def run_block(job):
    idx, src_name, line_no, code, work = job
    pkg = f"b{idx:02d}"
    d = work / pkg
    d.mkdir(parents=True, exist_ok=True)
    has_pkg = re.search(r"^\s*package\s", code, flags=re.M) is not None
    has_main = re.search(r"\bfun\s+main\s*\(", code) is not None
    body = code if has_pkg else f"package {pkg}\n\n{code}"
    kt = d / "Blk.kt"
    kt.write_text(body, encoding="utf-8")
    out = d / "out"
    res = {
        "idx": idx, "src": src_name, "line": line_no, "has_main": has_main,
        "first": code.strip().splitlines()[0][:70], "expected": expected_outputs(code),
        "intended_error": ("컴파일 에러" in code) or ("Unresolved reference" in code),
    }
    p = subprocess.run([str(KOTLINC), str(kt), "-d", str(out)], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=240)
    res["compile_rc"] = p.returncode
    res["compile_log"] = "\n".join(l for l in (p.stderr + p.stdout).splitlines()
                                   if ("error:" in l or "warning:" in l))
    if p.returncode == 0 and has_main and not has_pkg:
        r = subprocess.run(["java", "-Dfile.encoding=UTF-8", "-Dstdout.encoding=UTF-8", "-Dstderr.encoding=UTF-8", "-cp", f"{out}{os.pathsep}{STDLIB}", f"{pkg}.BlkKt"], capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=60)
        res["run_rc"] = r.returncode
        res["stdout"] = r.stdout.splitlines()
        res["stderr"] = r.stderr.strip()[:300]
    return res


def main():
    work = Path(sys.argv[1])
    notes = sys.argv[2:]
    jobs, idx = [], 0
    for md in notes:
        for line_no, code in extract_blocks(md):
            idx += 1
            jobs.append((idx, Path(md).name, line_no, code, work))
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        results = list(ex.map(run_block, jobs))
    (work / "report.json").write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"blocks={len(results)}")


if __name__ == "__main__":
    main()
