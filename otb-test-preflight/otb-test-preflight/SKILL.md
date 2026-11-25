---
name: otb-test-preflight
description: Check an OpenTenBase installation and test-runner environment before starting a cluster. Use when OPENTENBASE_HOME, PATH, missing tools, or a stale postgres build may cause test failures.
---

# OpenTenBase test preflight

Run from the Skill directory with Python 3.8 or newer:

```sh
python3 scripts/preflight.py
```

When the user provides the installation and source build paths:

```sh
python3 scripts/preflight.py --home /opt/opentenbase --source-postgres /path/to/OpenTenBase/src/backend/postgres
```

Read the JSON `checks` and `summary`. Report failures before warnings. For a PATH mismatch, suggest correcting PATH to select the intended installation. For a binary mismatch, explain that different file hashes warrant checking the build/install process; they do not prove functional incompatibility. If source comparison is skipped, explicitly say it was not checked.

The tool does not execute database binaries, start or stop clusters, modify files, connect to databases, or verify runtime readiness. Do not change environment variables, reinstall software, or start services without the user's explicit authorization. Do not present a passing report as proof that the cluster is healthy.
