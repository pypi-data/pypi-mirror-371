import json
import subprocess

from ..utils import p, line, parse
import os
import json

BASIC = {
    "projex": "1.0.1",
    "dependencies": [],
    "env":{},
    "ssh": [],
    "runners": {},
    "variables": {}
}


def main():
    data = parse()
    filename = data.parsed.get("output", "projex.json")
    venv = data.parsed.get("venv", ".venv")
    main_file = data.parsed.get("main-file", "main.py")
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as fp:
                json.load(fp)
        except json.JSONDecodeError:
            p(
                f"{filename} exists, But it has wrong structure (JSONDecodeError)",
                "fatal",
            )
        except PermissionError:
            p("{filename} exists, But I do not have permission to read it.", "fatal")
        except Exception as err:
            p(f"Unexpected error: {err}", "fatal")
        else:
            if not data.overwrite:
                p(
                    f"{filename} Already exists. Use --overwrite to overwrite the current config file.",
                    "fatal",
                )

    p("Creating new projex...")
    BASIC['variables']["venv"] = venv
    BASIC["variables"]["mainFile"] = main_file
    BASIC['runners']['base'] = dict(
            cmd='{venv}/bin/python {mainFile}',
            env="g",
            linked="m",
            sandbox=False
    )
    subprocess.run(['python', '-m', 'venv', '.venv'])
    try:
        with open(filename, "+w", encoding="utf-8") as fp:
            json.dump(BASIC, fp, indent=2)
    except PermissionError:
        p("Cannot make new project: Permission denied.", "fatal")
    except Exception as err:
        p(f"Cannot make new project: Unexpected error ({err})", "fatal")
    p("Created projex.")
