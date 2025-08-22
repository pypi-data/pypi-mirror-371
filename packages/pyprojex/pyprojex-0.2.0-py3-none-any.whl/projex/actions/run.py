import os
import subprocess
import shlex
from ..utils import p, line, parse, load, save

DT_PROCESS =  0x00000008

HELP = '''
-> Welcome to run section, here you add runners and manage them
* In projex runners are tweakable in few ways
    1. System Environment Variables:
        This makes sure you want to command run with access to whole public system env or just environment variables that you gave. 
    2. Sandboxing
        Here you can limit network, cpu, memory usage and network routes and alot more, for using this future use 'projex sandbox'
    3. Environment Group
        Here you can make Environment Groups like production and development so codes will run with custom groups.
        You can make groups permanently or auto ask between groups. Read more about projex Env group templating in projex.com/docs
'''

def main():
    data = parse()
    config = load()
    if len(data.raw) < 2:
        p("Usage: projex run <new|all|remove|[name]>", "fatal")
    action = data.raw[1]
    if action == "new":
        if len(data.raw) != 3:
            p("Usage: projex run new <name>", "fatal")
        elif data.raw[2] in config["runners"]:
            p(
                f"{data.raw[2]} runner s already exists, use projex run remove {data.raw[2]} to remove it.",
                "fatal",
            )
        elif data.raw[2] in ('new', 'all', 'remove'):
            p(
                f"You cannot name your runner {data.raw}",
                "fatal"
            )
        cmd = input(
            f"- Please enter the bash command you want to {data.raw[2]} contain [You can use variables in curly braces]: "
        )
        env = input(
            "- In this case do you want this command run in global environment or minimal [g/m]"
        )
        while env.lower() not in ("g", "m"):
            env = input(
                "-Wrong answer! In this case do you want this command run in global environment or minimal [g/m]"
            )
        if env == 'm':
            linked = input(
                "- Do you want to link this runner to custom environment group? [group_name/n]"
            )
        else:
            linked = "g"
        p(
            f"Got results, adding runner with name {data.raw[2]} with ENV -> {env}, GROUP -> {linked}"
        )

        config['runners'][data.raw[2]] = dict(
            cmd=cmd,
            env=env,
            linked=linked,
            sandbox=False
        )
        save(config)
        p(
            "Saved the new configuration."
        )

    elif action == 'remove':
        if len(data.raw) != 3:
            p("Usage: projex run remove <name>", "fatal")
        elif data.raw[2] not in config['runners']:
            p(f"There is no runner named {data.raw[2]} in config.", "fatal")
        config['runners'].pop(data.raw[2])
        save(config)
        p(f"Runner {data.raw[2]} removed successfully.")

    elif action == "all":
        for j,i in config['runners'].items():
            p(f"{j} ({i['env']}, {i['linked']}) - {i['cmd']}")

    elif action == 'start':
        name = data.raw[2]
        loaded = config['runners'][name]
        variables = config['variables']
        cmd = loaded['cmd'].format(**variables)
        if loaded['env'] == 'g':
           env = os.environ
        elif loaded['env'] == 'm' and loaded['linked'] in config['env']:
            env = config['env'][loaded['linked']]
            if "__global__" in env and env['__global__'] == True:
                p("Merging global variables with custom group, __global__ detected.")
                env.update(os.environ)
        else:
            p("No environment variable group is available for this run. Running with empty environment variables", "warning")
            env = dict()
        p(str(shlex.split(cmd)))
        if data.disown or data.bg:
            if os.name == 'nt': # Windows
                proc = subprocess.run(shlex.split(cmd),  creationflags=DT_PROCESS, close_fds=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
            else: # Unix
                proc = subprocess.Popen(shlex.split(cmd), start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
            p(f"Process ID: {proc.pid}")
        else:
            subprocess.run(shlex.split(cmd), env=env)


    
