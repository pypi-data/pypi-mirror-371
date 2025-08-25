"""
Project-specific macros for MkDocs (mkdocs-macros-plugin).
Used in Markdown like:
  - Build time: {{ build_time() }}
  - Version: {{ config.extra.version | default("dev") }}
"""
import os
from datetime import datetime, UTC

def define_env(env):
    # Read version from env (set in Makefile/CI); fall back to "dev"
    version = os.environ.get("WSPR_AI_LITE_VERSION", "dev")

    # Ensure config.extra exists, then set version for templates:
    env.conf.setdefault("extra", {})
    env.conf["extra"]["version"] = version

    # Simple build timestamp macro
    env.macro(lambda: datetime.now(UTC).isoformat(timespec="seconds"), name="build_time")

def on_post_build(plugin):
    """
    Called after the site is built. `plugin` is the MacrosPlugin instance.
    """
    try:
        cfg = plugin.config                       # MkDocs Config object (dict-like)
        extra = cfg.get("extra", {}) if hasattr(cfg, "get") else cfg["extra"]
        version = extra.get("version", "dev")
        # Do whatever you wanted here; for now, just log:
        print(f"[macros] post_build: version={version}")
    except Exception as e:
        # Never fail the build because of a post-build log
        print(f"[macros] post_build: skipped ({e})")
