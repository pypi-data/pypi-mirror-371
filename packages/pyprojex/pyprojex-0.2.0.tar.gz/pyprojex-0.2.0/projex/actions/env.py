from ..utils import p, line, parse, load, save


def new(config, args):
    if len(args.raw) != 3:
        p("Usage 'projex env new <group name>'", "fatal")
    group_name = args.raw[2]
    if group_name in ('global', 'no-env'):
        p(f"You cannot name a environment variable group name {group_name}", "fatal")
    config['env'][group_name] = {}
    save(config)
    p("New env is added.")

def remove(config, args):
    if len(args.raw) != 3:
        p("Usage 'projex env remove <group name>'", "fatal")
    group_name = args.raw[2]
    if group_name in ('global', 'no-env'):
        p(f"You cannot remove especial environment variable group name {group_name}", "fatal")
    elif group_name not in config['env']:
        p(f"{group_name} doesn't exists.", "fatal")
    config['env'].pop(group_name)
    save(config)
    p("Env space is removed.")

def group(config, args):
    if len(args.raw) < 4:
        p("Usage 'projex env group <name> <pop|set> [values...]'", "fatal")
    name = args.raw[2]
    action = args.raw[3]
    values = args.raw[4:]
    if action not in ('pop', 'set'):
        p("Action is not allowed.", "fatal")
    elif name not in config['env']:
        p("Group doesn't exists.")
    elif action == "pop":
        for i in values:
            if i not in config['env'][name]:
                p(f"{i} is not set in the group.")
            else:
                config['env'][name].pop(i)
                p(f"Removed {i}")
    elif action == 'set':
        for i in values:
            spltd = i.split('=', 1)
            if not len(spltd)-1:
                p(f"{i} is not in correct format.")
            else:
                key, value = spltd[0], spltd[1]
                config['env'][name][key] = value
                p(f"Set {i}")
    save(config)

def main():
    config = load()
    args = parse()
    if len(args.raw) < 2:
        p("Usage 'projex env <action>'", "fatal")
    elif args.raw[1] == 'new':
        new(config, args)
    elif args.raw[1] == 'remove':
        remove(config, args)
    elif args.raw[1] == 'group':
        group(config, args)