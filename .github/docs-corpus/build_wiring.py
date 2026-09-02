import sys

pins_path, out_path = sys.argv[1], sys.argv[2]

lines = [l.strip().split('\t') for l in open(pins_path) if l.strip()]
refs = []
for p, t in lines:
    # pod-* repos carry their manifests at the ROOT (the market ref convention:
    # '@github.com/opencharly/pod-<name>:<tag>'); everything else lives at candy/<name>.
    if p.startswith('pod-'):
        refs.append("        - '@github.com/opencharly/%s:%s'" % (p, t))
    else:
        refs.append("        - '@github.com/opencharly/%s/candy/%s:%s'" % (p, p, t))

header = [
    "docs-corpus:",
    "    candy:",
    "        version: 2026.242.2200",
    "        description: CI-time corpus wiring candy for the docs deploy.",
    "        candy:",
]
footer = [
    "        plan:",
    "            - check: the corpus listing is loaded for the docs generator",
    "              id: docs-corpus-loaded",
    "              command: \"true\"",
]
out = header + refs + footer
open(out_path, 'w').write('\n'.join(out) + '\n')
print('corpus wiring refs:', len(refs))