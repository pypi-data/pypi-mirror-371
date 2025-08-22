"""
# QALITA (c) COPYRIGHT 2025 - ALL RIGHTS RESERVED -
"""

import os
import re
from datetime import datetime
from flask import Blueprint, current_app, render_template, redirect, url_for


bp = Blueprint("main", __name__)


@bp.route("/")
def dashboard():
    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    agent_conf = None
    try:
        raw = cfg.load_agent_config()
        # Map nested raw config to flat fields expected by the template
        if isinstance(raw, dict) and raw:
            def pick(obj, *path):
                cur = obj
                for key in path:
                    if not isinstance(cur, dict) or key not in cur:
                        return ""
                    cur = cur[key]
                return cur

            agent_conf = {
                "name": pick(raw, "context", "remote", "name") or raw.get("name", ""),
                "mode": raw.get("mode", ""),
                "url": pick(raw, "context", "local", "url") or raw.get("url", ""),
                "agent_id": pick(raw, "context", "remote", "id") or raw.get("agent_id", ""),
            }
        else:
            agent_conf = None
    except Exception:
        agent_conf = None
    cfg.load_source_config()
    sources = list(reversed(cfg.config.get("sources", [])))
    # Build agent run list from agent_run_temp
    agent_runs = []
    try:
        run_root = cfg.get_agent_run_path()
        if os.path.isdir(run_root):
            pattern = re.compile(r"^\d{14}_[a-z0-9]{5}$")
            for entry in sorted(os.listdir(run_root), reverse=True):
                if pattern.match(entry) and os.path.isdir(os.path.join(run_root, entry)):
                    ts = entry.split("_")[0]
                    try:
                        when = datetime.strptime(ts, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
                    except Exception:
                        when = ts
                    agent_runs.append({
                        "name": entry,
                        "path": os.path.join(run_root, entry),
                        "timestamp": ts,
                        "when": when,
                    })
    except Exception:
        agent_runs = []
    return render_template("dashboard.html", agent_conf=agent_conf, sources=sources, agent_runs=agent_runs)


@bp.post("/validate")
def validate_sources():
    from qalita.commands.source import validate_source as _validate

    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    # Run validation
    try:
        _validate.__wrapped__(cfg)  # type: ignore[attr-defined]
    except Exception:
        _validate(cfg)  # type: ignore[misc]
    # Build feedback from results
    try:
        cfg.load_source_config()
        sources = cfg.config.get("sources", []) or []
        total = len(sources)
        valid_count = sum(1 for s in sources if (s.get("validate") or "").lower() == "valid")
        invalid_count = sum(1 for s in sources if (s.get("validate") or "").lower() == "invalid")
        msg = f"Validated {total} source(s): {valid_count} valid, {invalid_count} invalid"
        level = "info" if invalid_count == 0 else "error"
    except Exception:
        msg = "Validation completed."
        level = "info"
    # Render dashboard with feedback
    return dashboard_with_feedback(msg, level)


@bp.post("/push")
def push_sources():
    from flask import request
    from qalita.commands.source import push_programmatic

    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    # For web, we do not want interactive confirms, so public approvals are off by default
    ok, message = push_programmatic(cfg, skip_validate=False, approve_public=False)
    level = "info" if ok else "error"
    return dashboard_with_feedback(message, level)


@bp.post("/pack/push")
def push_pack_from_ui():
    from flask import request
    from qalita.commands.pack import push_from_directory

    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    pack_dir = request.form.get("pack_dir", "").strip()
    feedback = None
    feedback_level = "info"
    if pack_dir:
        ok, message = push_from_directory(cfg, pack_dir)
        feedback = message or ("Pack pushed successfully." if ok else "Pack push failed.")
        feedback_level = "info" if ok else "error"
    else:
        feedback = "Please select a pack folder."
        feedback_level = "error"
    # Refresh dashboard with feedback
    return dashboard_with_feedback(feedback, feedback_level)


def dashboard_with_feedback(feedback_msg=None, feedback_level: str = "info"):
    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    agent_conf = None
    try:
        raw = cfg.load_agent_config()
        if isinstance(raw, dict) and raw:
            def pick(obj, *path):
                cur = obj
                for key in path:
                    if not isinstance(cur, dict) or key not in cur:
                        return ""
                    cur = cur[key]
                return cur
            agent_conf = {
                "name": pick(raw, "context", "remote", "name") or raw.get("name", ""),
                "mode": raw.get("mode", ""),
                "url": pick(raw, "context", "local", "url") or raw.get("url", ""),
                "agent_id": pick(raw, "context", "remote", "id") or raw.get("agent_id", ""),
            }
        else:
            agent_conf = None
    except Exception:
        agent_conf = None
    cfg.load_source_config()
    sources = list(reversed(cfg.config.get("sources", [])))
    # Build agent runs
    agent_runs = []
    try:
        run_root = cfg.get_agent_run_path()
        if os.path.isdir(run_root):
            pattern = re.compile(r"^\d{14}_[a-z0-9]{5}$")
            for entry in sorted(os.listdir(run_root), reverse=True):
                if pattern.match(entry) and os.path.isdir(os.path.join(run_root, entry)):
                    ts = entry.split("_")[0]
                    try:
                        when = datetime.strptime(ts, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
                    except Exception:
                        when = ts
                    agent_runs.append({
                        "name": entry,
                        "path": os.path.join(run_root, entry),
                        "timestamp": ts,
                        "when": when,
                    })
    except Exception:
        agent_runs = []
    return render_template(
        "dashboard.html",
        agent_conf=agent_conf,
        sources=sources,
        agent_runs=agent_runs,
        feedback=feedback_msg,
        feedback_level=feedback_level,
    )


