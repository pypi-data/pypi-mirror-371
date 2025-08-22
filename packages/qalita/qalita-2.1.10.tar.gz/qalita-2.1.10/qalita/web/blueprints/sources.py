"""
# QALITA (c) COPYRIGHT 2025 - ALL RIGHTS RESERVED -
"""

from typing import Any, Dict

from flask import Blueprint, current_app, redirect, render_template, request, url_for, jsonify
from qalita.commands.source import validate_source_object


bp = Blueprint("sources", __name__)


@bp.get("/")
def list_sources():
    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    cfg.load_source_config()
    sources = cfg.config.get("sources", [])
    return render_template("sources/list.html", sources=sources)


@bp.get("/add")
def add_source_view():
    return render_template("sources/edit.html", title="Add source", source=None)


@bp.post("/add")
def add_source_post():
    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    cfg.load_source_config()

    name = request.form.get("name", "").strip()
    s_type = request.form.get("type", "").strip()

    # Build config from form according to type
    config_section = {}
    if s_type == "file":
        p = request.form.get("file_path", "").strip()
        if p: config_section["path"] = p
    elif s_type == "folder":
        p = request.form.get("folder_path", "").strip()
        if p: config_section["path"] = p
    elif s_type == "sqlite":
        fpath = request.form.get("sqlite_file_path", "").strip()
        if fpath:
            config_section["type"] = "sqlite"
            config_section["file_path"] = fpath
    elif s_type in ["mysql", "postgresql", "oracle", "mssql"]:
        config_section.update({
            "type": s_type,
            "host": request.form.get("db_host", "").strip(),
            "port": request.form.get("db_port", "").strip(),
            "username": request.form.get("db_username", "").strip(),
            "password": request.form.get("db_password", "").strip(),
            "database": request.form.get("db_database", "").strip(),
            "table_or_query": request.form.get("db_table_or_query", "*").strip() or "*",
        })
    elif s_type == "mongodb":
        config_section.update({
            "host": request.form.get("mongo_host", "").strip(),
            "port": request.form.get("mongo_port", "").strip(),
            "username": request.form.get("mongo_username", "").strip(),
            "password": request.form.get("mongo_password", "").strip(),
            "database": request.form.get("mongo_database", "").strip(),
        })
    elif s_type == "s3":
        config_section.update({
            "bucket": request.form.get("s3_bucket", "").strip(),
            "prefix": request.form.get("s3_prefix", "").strip(),
            "access_key": request.form.get("s3_access_key", "").strip(),
            "secret_key": request.form.get("s3_secret_key", "").strip(),
            "region": request.form.get("s3_region", "").strip(),
        })
    elif s_type == "gcs":
        config_section.update({
            "bucket": request.form.get("gcs_bucket", "").strip(),
            "prefix": request.form.get("gcs_prefix", "").strip(),
            "credentials_json": request.form.get("gcs_credentials", "").strip(),
        })
    elif s_type == "azure_blob":
        config_section.update({
            "container": request.form.get("az_container", "").strip(),
            "prefix": request.form.get("az_prefix", "").strip(),
            "connection_string": request.form.get("az_connection", "").strip(),
        })
    elif s_type == "hdfs":
        config_section.update({
            "namenode_host": request.form.get("hdfs_namenode", "").strip(),
            "port": request.form.get("hdfs_port", "").strip(),
            "user": request.form.get("hdfs_user", "").strip(),
            "path": request.form.get("hdfs_path", "").strip(),
        })
    elif s_type == "sftp":
        config_section.update({
            "host": request.form.get("sftp_host", "").strip(),
            "port": request.form.get("sftp_port", "").strip(),
            "username": request.form.get("sftp_username", "").strip(),
            "password": request.form.get("sftp_password", "").strip(),
            "path": request.form.get("sftp_path", "").strip(),
        })
    elif s_type in ["http", "https"]:
        auth_type = request.form.get("http_auth_type", "none")
        config_section["url"] = request.form.get("http_url", "").strip()
        config_section["auth_type"] = auth_type
        if auth_type == "basic":
            config_section["username"] = request.form.get("http_username", "").strip()
            config_section["password"] = request.form.get("http_password", "").strip()
        elif auth_type == "token":
            config_section["token"] = request.form.get("http_token", "").strip()

    new_source = {
        "name": name,
        "type": s_type,
        "description": request.form.get("description", "").strip(),
        "reference": request.form.get("reference") == "on",
        "sensitive": request.form.get("sensitive") == "on",
        "visibility": request.form.get("visibility", "private"),
        "config": config_section,
    }

    if not validate_source_object(cfg, new_source, skip_connection=False):
        return render_template("sources/edit.html", title="Add source", source=request.form, error="Validation failed. Check fields and connectivity.")

    cfg.config.setdefault("sources", []).append(new_source)
    cfg.save_source_config()
    return redirect(url_for("main.dashboard"))


@bp.get("/edit/<name>")
def edit_source_view(name):
    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    cfg.load_source_config()
    src = next((s for s in cfg.config.get("sources", []) if s.get("name") == name), None)
    return render_template("sources/edit.html", title="Edit source", source=src)


@bp.post("/edit/<name>")
def edit_source_post(name):
    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    cfg.load_source_config()
    sources = cfg.config.get("sources", [])
    for i, src in enumerate(sources):
        if src.get("name") == name:
            new_name = request.form.get("name", src.get("name", "")).strip()
            new_type = request.form.get("type", src.get("type", "")).strip()
            new_desc = request.form.get("description", src.get("description", "")).strip()
            new_vis = request.form.get("visibility", src.get("visibility", "private"))
            new_ref = request.form.get("reference") == "on"
            new_sens = request.form.get("sensitive") == "on"
            # Build config
            config_section: Dict[str, Any] = {}
            if new_type == "file":
                p = request.form.get("file_path", "").strip()
                if p: config_section["path"] = p
            elif new_type == "folder":
                p = request.form.get("folder_path", "").strip()
                if p: config_section["path"] = p
            elif new_type == "sqlite":
                fpath = request.form.get("sqlite_file_path", "").strip()
                if fpath:
                    config_section["type"] = "sqlite"
                    config_section["file_path"] = fpath
            elif new_type in ["mysql", "postgresql", "oracle", "mssql"]:
                config_section.update({
                    "type": new_type,
                    "host": request.form.get("db_host", "").strip(),
                    "port": request.form.get("db_port", "").strip(),
                    "username": request.form.get("db_username", "").strip(),
                    "password": request.form.get("db_password", "").strip(),
                    "database": request.form.get("db_database", "").strip(),
                    "table_or_query": request.form.get("db_table_or_query", "*").strip() or "*",
                })
            elif new_type == "mongodb":
                config_section.update({
                    "host": request.form.get("mongo_host", "").strip(),
                    "port": request.form.get("mongo_port", "").strip(),
                    "username": request.form.get("mongo_username", "").strip(),
                    "password": request.form.get("mongo_password", "").strip(),
                    "database": request.form.get("mongo_database", "").strip(),
                })
            elif new_type == "s3":
                config_section.update({
                    "bucket": request.form.get("s3_bucket", "").strip(),
                    "prefix": request.form.get("s3_prefix", "").strip(),
                    "access_key": request.form.get("s3_access_key", "").strip(),
                    "secret_key": request.form.get("s3_secret_key", "").strip(),
                    "region": request.form.get("s3_region", "").strip(),
                })
            elif new_type == "gcs":
                config_section.update({
                    "bucket": request.form.get("gcs_bucket", "").strip(),
                    "prefix": request.form.get("gcs_prefix", "").strip(),
                    "credentials_json": request.form.get("gcs_credentials", "").strip(),
                })
            elif new_type == "azure_blob":
                config_section.update({
                    "container": request.form.get("az_container", "").strip(),
                    "prefix": request.form.get("az_prefix", "").strip(),
                    "connection_string": request.form.get("az_connection", "").strip(),
                })
            elif new_type == "hdfs":
                config_section.update({
                    "namenode_host": request.form.get("hdfs_namenode", "").strip(),
                    "port": request.form.get("hdfs_port", "").strip(),
                    "user": request.form.get("hdfs_user", "").strip(),
                    "path": request.form.get("hdfs_path", "").strip(),
                })
            elif new_type == "sftp":
                config_section.update({
                    "host": request.form.get("sftp_host", "").strip(),
                    "port": request.form.get("sftp_port", "").strip(),
                    "username": request.form.get("sftp_username", "").strip(),
                    "password": request.form.get("sftp_password", "").strip(),
                    "path": request.form.get("sftp_path", "").strip(),
                })
            elif new_type in ["http", "https"]:
                auth_type = request.form.get("http_auth_type", "none")
                config_section["url"] = request.form.get("http_url", "").strip()
                config_section["auth_type"] = auth_type
                if auth_type == "basic":
                    config_section["username"] = request.form.get("http_username", "").strip()
                    config_section["password"] = request.form.get("http_password", "").strip()
                elif auth_type == "token":
                    config_section["token"] = request.form.get("http_token", "").strip()

            updated = {
                "name": new_name,
                "type": new_type,
                "description": new_desc,
                "visibility": new_vis,
                "reference": new_ref,
                "sensitive": new_sens,
                "config": config_section if config_section else src.get("config", {}),
            }

            if not validate_source_object(cfg, updated, skip_connection=False, exclude_name=name):
                return render_template("sources/edit.html", title="Edit source", source=request.form, error="Validation failed. Check fields and connectivity.")

            sources[i].update(updated)
            break
    cfg.save_source_config()
    return redirect(url_for("main.dashboard"))


@bp.post("/delete/<name>")
def delete_source_post(name):
    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    cfg.load_source_config()
    cfg.config["sources"] = [s for s in cfg.config.get("sources", []) if s.get("name") != name]
    cfg.save_source_config()
    return redirect(url_for("main.dashboard"))


@bp.get("/pick-file")
def pick_file():
    try:
        import tkinter as tk  # type: ignore
        from tkinter import filedialog  # type: ignore

        root = tk.Tk()
        root.withdraw()
        try:
            root.wm_attributes("-topmost", 1)
        except Exception:
            pass
        path = filedialog.askopenfilename()
        root.update()
        root.destroy()
        return jsonify({"path": path})
    except Exception as exc:  # pragma: no cover
        return jsonify({"error": f"Picker unavailable: {exc}"}), 500


@bp.get("/pick-folder")
def pick_folder():
    try:
        import tkinter as tk  # type: ignore
        from tkinter import filedialog  # type: ignore

        root = tk.Tk()
        root.withdraw()
        try:
            root.wm_attributes("-topmost", 1)
        except Exception:
            pass
        path = filedialog.askdirectory()
        root.update()
        root.destroy()
        return jsonify({"path": path})
    except Exception as exc:  # pragma: no cover
        return jsonify({"error": f"Picker unavailable: {exc}"}), 500


