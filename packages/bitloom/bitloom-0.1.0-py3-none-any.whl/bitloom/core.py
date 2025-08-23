def make_file(filename):
    header = "÷øbl\n"
    with open(filename, "r") as f:
        content = f.read()
    out = header + content
    out = out.replace("PRINT ", "print(")
    out = out.replace("INPUT ", "input(")
    out = out.replace("VAR ", "")
    with open(filename, "w") as f:
        f.write(out + "\n÷øbl")

def run_file(filename):
    with open(filename, "r") as f:
        exec(f.read().replace("÷øbl", ""))
