from .utils import  parse, p, line
from . import actions

def main():
    result = parse()
    if len(result.raw) < 1:
        p('Wrong usage.', "fatal")
    action = result.raw[0]
    match action:
        case 'new':
            actions.new.main()
        case 'run':
            actions.run.main()
        case 'env':
            actions.env.main()
        case 'var':
            actions.variables.main()
        case "help":
            actions.helper.main()
        case _:
            p("Unknown action use help.", "fatal")


