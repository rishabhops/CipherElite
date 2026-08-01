import ast, glob, re

CMD_RE = re.compile(r'@CipherElite\.on\(events\.NewMessage\(pattern=r["\']([^"\']+)["\']')
PLUGIN_GLOB = "plugins/*.py"
BOT_GLOB = "bot_plugins/*.py"

def get_commands(path):
    cmds = []
    text = open(path).read()
    for line in text.splitlines():
        m = CMD_RE.search(line)
        if not m:
            continue
        pattern = m.group(1)
        # Strip non-capturing prefix and extract the main command word
        # pattern examples:
        #   "\\.spotify(?:\\s+|$)"
        #   "\\.ban(?: |$)(.*)"
        #   "\\.lock"
        m2 = re.search(r"\\\\\.([a-zA-Z_0-9]+)", pattern)
        if m2:
            cmds.append(m2.group(1))
        else:
            cmds.append(pattern)
    return cmds

all_cmds = {}
for path in glob.glob(PLUGIN_GLOB) + glob.glob(BOT_GLOB):
    cmds = get_commands(path)
    for c in cmds:
        all_cmds.setdefault(c, []).append(path)

conflicts = {k: v for k, v in all_cmds.items() if len(v) > 1}

print(f"Total commands: {len(all_cmds)}")
if conflicts:
    print("Conflicts:")
    for cmd, files in sorted(conflicts.items()):
        print(f"  .{cmd}: {files}")
else:
    print("No conflicts detected.")
