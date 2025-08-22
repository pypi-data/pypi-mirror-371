from ..utils import p, line, parse, load, save

def main():
    data = parse()
    config = load()
    key = data.raw[1]
    value = data.raw[2]
    if key in config['variables'] and not data.overwrite:
        p(f"Key {key} already exists please use --overwrite to overwrite the current value.", "fatal")
    config['variables'][key] = value
    save(config)
    p("Value set.")
