#!/usr/bin/env python3
"""Webhook runner for the Kunio Korean patch repository.

실행 흐름:
1) webhook 조건 검증 (repo, ref)
2) 5분 대기
3) git pull
4) git status / HEAD 출력
5) 목표1 텍스트 탐지
6) 목표2 폰트/CHR 매핑
7) 목표3 IPS 패치 생성
8) 변경분 있으면 commit/push
9) 최종 1줄 리포트 출력
"""

from __future__ import annotations

import argparse
import os
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
TARGET_REPO = "kakduki/kunio-period-drama-korean-patch"
TARGET_REF = "refs/heads/main"
DEFAULT_DELAY = 300


@dataclass
class StepResult:
    name: str
    command: str
    return_code: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.return_code == 0


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(cmd: str, cwd: Path = REPO_ROOT, timeout: Optional[int] = None) -> StepResult:
    completed = subprocess.run(
        cmd,
        shell=True,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout,
    )
    return StepResult(
        name=cmd,
        command=cmd,
        return_code=completed.returncode,
        stdout=(completed.stdout or "").strip(),
        stderr=(completed.stderr or "").strip(),
    )


def run_pipeline_step(step_name: str, commands: List[str], fail_fast: bool = False,
                      timeout: int = 1200) -> Tuple[bool, List[StepResult], bool]:
    """
    Returns: (any_success, step_results, stop_requested)
    stop_requested becomes True when command output contains 루프 종료/DONE.
    """
    results: List[StepResult] = []
    any_success = False
    stop_requested = False

    for cmd in commands:
        print(f"[+]{_ts()} [step:{step_name}] start -> {cmd}")
        res = run_cmd(cmd, timeout=timeout)
        results.append(res)
        status = "OK" if res.ok else "FAIL"
        print(f"[+]{_ts()} [step:{step_name}] {status} code={res.return_code}")

        if res.stdout:
            print(f"[{step_name} stdout]\n{res.stdout}")
        if res.stderr:
            print(f"[{step_name} stderr]\n{res.stderr}", file=sys.stderr)

        if "루프 종료" in res.stdout or "DONE" in res.stdout:
            stop_requested = True

        if res.ok:
            any_success = True
            continue

        # fail-fast keeps going only when required.
        if fail_fast:
            break

    return any_success, results, stop_requested


def get_git_head() -> str:
    res = run_cmd("git rev-parse HEAD")
    if not res.ok:
        return "미확인"
    return res.stdout.strip()


def git_status_short() -> str:
    res = run_cmd("git status --short")
    return res.stdout.strip()


def has_changes() -> bool:
    return bool(git_status_short())


def maybe_push() -> StepResult:
    return run_cmd("git push origin main", timeout=1800)


def attempt_claude_loop(context: str, max_loops: int = 1, stop_words: Tuple[str, ...] = ("루프 종료", "DONE")) -> Tuple[bool, str]:
    """Fallback helper. Returns (stopped, output)."""
    claude_exe = shutil.which("claude")
    if not claude_exe:
        return False, "claude 미설치"

    prompt = (
        "다음은 현재 웹훅 파이프라인 실패 로그입니다.\n"
        f"{context}\n"
        "요청: 가능한 범위에서 실패 원인을 바로잡고 다음 상태를 출력해. "
        "완료가 되면 마지막 줄에 '루프 종료' 또는 'DONE'만 출력해."
    )

    last_output = ""
    stopped = False
    for i in range(max_loops):
        safe_prompt = shlex.quote(prompt)
        cmd = f"claude -p {safe_prompt} --print"
        print(f"[+]{_ts()} Claude fallback start (attempt {i+1}/{max_loops})")
        res = run_cmd(cmd, timeout=120)
        print(f"[+]{_ts()} Claude fallback rc={res.return_code}")
        if res.stdout:
            print(f"[claude stdout]\n{res.stdout}")
        if res.stderr:
            print(f"[claude stderr]\n{res.stderr}", file=sys.stderr)
        last_output = res.stdout.strip()
        if any(word in last_output for word in stop_words):
            stopped = True
            break
        # if auth/other hard fail, no 의미 있는 루프
        if not res.ok:
            break
    return stopped, last_output


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Kunio webhook workflow")
    parser.add_argument("--repo-full-name", default=TARGET_REPO, help="payload.repository.full_name")
    parser.add_argument("--ref", default=TARGET_REF, help="payload.ref")
    parser.add_argument("--delay-seconds", type=int, default=DEFAULT_DELAY)
    parser.add_argument("--auto-commit", action="store_true", default=True)
    parser.add_argument("--no-commit", action="store_true", help="Disable auto commit")
    parser.add_argument("--auto-push", action="store_true", default=True)
    parser.add_argument("--no-push", action="store_true", help="Disable auto push")
    parser.add_argument("--run-claude-fallback", action="store_true", default=False)
    parser.add_argument("--max-loop", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=1200)
    args = parser.parse_args()

    # preserve explicit flags
    auto_commit = args.auto_commit and not args.no_commit
    auto_push = args.auto_push and not args.no_push

    summary: List[str] = []
    stop_requested = False

    print(f"[{_ts()}] webhook-autopipeline start")

    if args.repo_full_name != TARGET_REPO:
        msg = f"repo_mismatch ({args.repo_full_name})"
        head = get_git_head()
        print(f"클로드 웹훅 감지 -> HEAD={head} -> 실행결과={msg}")
        return 0

    if args.ref != TARGET_REF:
        msg = f"ref_mismatch ({args.ref})"
        head = get_git_head()
        print(f"클로드 웹훅 감지 -> HEAD={head} -> 실행결과={msg}")
        return 0

    if args.delay_seconds > 0:
        print(f"[{_ts()}] wait {args.delay_seconds}s")
        import time

        time.sleep(args.delay_seconds)

    # 1) git pull + 상태 출력
    git_pull_ok, pull_results, stop = run_pipeline_step(
        "pull", [
            "git remote set-url origin git@github.com:kakduki/kunio-period-drama-korean-patch.git",
            "git pull --ff-only origin main",
            "git status --short",
        ], timeout=args.timeout
    )
    stop_requested = stop_requested or stop

    if not git_pull_ok:
        summary.append("git pull 실패")

    head = get_git_head()
    status_after_pull = git_status_short()

    print("[status] git status --short")
    print(status_after_pull if status_after_pull else "(clean)")
    print(f"[status] HEAD={head}")

    # 2) 목표1 텍스트 탐지
    ok1, r1, stop = run_pipeline_step(
        "goal1_text_detect",
        [
            "python scripts/find_text.py",
            "python scripts/identify_bank1_text_blocks.py",
            "python scripts/map_translation_offsets.py",
        ],
        timeout=args.timeout,
    )
    stop_requested = stop_requested or stop
    summary.append(f"목표1={'성공' if ok1 else '실패'}")

    # 3) 목표2 폰트/CHR 매핑
    ok2, r2, stop = run_pipeline_step(
        "goal2_chr_font",
        [
            "python scripts/analyze_chr_font.py",
            "python scripts/analyze_chr.py",
            "python scripts/export_chr_bank07_tile_map.py",
            "python scripts/generate_korean_font.py",
        ],
        timeout=args.timeout,
    )
    stop_requested = stop_requested or stop
    summary.append(f"목표2={'성공' if ok2 else '실패'}")

    # 4) 목표3 IPS 패치
    ok3, r3, stop = run_pipeline_step(
        "goal3_ips_patch",
        [
            "python scripts/build_patch.py",
            "python scripts/ips_patcher.py",
        ],
        timeout=args.timeout,
    )
    stop_requested = stop_requested or stop
    summary.append(f"목표3={'성공' if ok3 else '실패'}")

    # 5) 변경분 있을 경우 커밋/푸시
    changed = has_changes()
    commit_result = None
    push_result = None

    if changed:
        print(f"[{_ts()}] change detected")
        if auto_commit:
            msg = f"chore: autopatch webhook {datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
            git_add = run_pipeline_step("commit", ["git add -A"], fail_fast=True, timeout=300)
            if not git_add[0]:
                summary.append("git add 실패")
            else:
                commit_result = run_pipeline_step("commit", [f"git commit -m {shlex.quote(msg)}"], fail_fast=True, timeout=300)[1][0]
                if commit_result and commit_result.ok:
                    summary.append("커밋 완료")
                else:
                    summary.append("커밋 실패")

                if auto_push and commit_result and commit_result.ok:
                    push_result = maybe_push()
                    if push_result.ok:
                        summary.append("푸시 완료")
                    else:
                        summary.append(f"푸시 실패: {push_result.stderr[:200]}")
        else:
            summary.append("변경사항 있음(커밋 비활성)")
    else:
        summary.append("변경사항 없음(커밋 스킵)")

    # 6) Claude 폴백(선택)
    stop_text_found = "루프 종료" in "\n".join(s.stdout for s in (r1 + r2 + r3)) or "DONE" in "\n".join(
        s.stdout for s in (r1 + r2 + r3)
    )
    if not stop_text_found and args.run_claude_fallback and args.max_loop > 1:
        context = (
            f"HEAD={head}\n"
            f"summary={', '.join(summary)}\n"
            f"goal1={ok1}, goal2={ok2}, goal3={ok3}\n"
            f"git status={status_after_pull or '(clean)'}\n"
        )
        stopped, _ = attempt_claude_loop(context=context, max_loops=args.max_loop - 1)
        if stopped:
            stop_requested = True
            summary.append("Claude fallback: 루프 종료")
        else:
            summary.append("Claude fallback: 미완료")

    if stop_requested:
        summary.append("중단 조건 충족")

    if any("실패" in s for s in summary):
        status_text = "실패"
    elif stop_requested:
        status_text = "루프 종료"
    else:
        status_text = "완료"

    final = f"클로드 웹훅 감지 -> HEAD={head} -> 실행결과={status_text} | {'; '.join(summary)}"
    print(final)

    # non-zero if all steps failed and nothing changed
    if not changed and not any("성공" in s for s in summary):
        return 1
    if push_result and not push_result.ok:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
