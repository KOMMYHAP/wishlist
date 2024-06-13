import os
import subprocess


def collect_backups_list(root: str) -> list[str]:
    backups_list = []
    with os.scandir(root) as it:
        for entry in it:
            if entry.is_file():
                print(f'Suspicious file "{entry.name}" skipped.')
                continue
            backups_list.append(entry.path)
    return backups_list


def run_external_tool(args) -> bool:
    try:
        result = subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, check=True)
        if result.stderr:
            print(result.stderr)
            return False
    except subprocess.CalledProcessError as e:
        print(e)
        if e.stderr:
            print(e.stderr)
        return False

    return True
