#!/usr/bin/env python
import os, sys, signal

script_path = os.path.abspath(sys.argv[0])
script_parent, script_name = os.path.split(script_path)
sys.stderr.write('You are executing the script: %s\n' % script_name)
try:
    sys.stderr.write('The process ID (pid) is : %d\n' % os.getpid())
except:
    pass
sys.stderr.write('The directory of the script:  %s\n' % script_parent)
sys.stderr.write("The working directory:        %s\n" % os.path.abspath("."))
n_args = len(sys.argv) - 1
sys.stderr.write("%d command line arguments were supplied" % n_args)
if n_args > 0:
    r = []
    for a in sys.argv[1:]:
        if os.path.exists(a):
            if os.path.isdir(a):
                r.append(a + "    (this argument is the path to a diretory)")
            else:
                r.append(a + "    (this argument is the path to a file)")
        else:
            r.append(a + "    (this argument is not a path to an existing file or dir)")
    sys.stderr.write(":\n%s" % "\n".join(r))
sys.stderr.write("\n\n")
sys.stderr.write("""These  messages are written to standard error stream

You will be prompted for input and the line that you enter will be written
to standard output.

Any input that you enter that enter that starts with "q" or "Q" will cause 
the program to quit"
""")

exit_signal = False
signal_received = False
def p(s, st):
    global exit_signal, signal_received
    signal_received = True
    sys.stderr.write("\n%s: Signal number %d received.\n" % (script_name,s))
    fatal_sig = [signal.SIGQUIT, signal.SIGINT, signal.SIGTERM]
    fatal_signame = ["QUIT", "INTerrupt", "TERMinate"]
    try:
        i = fatal_sig.index(s)
        sys.stderr.write("%s: This is the %s signal. Exiting...\n" % (script_name, fatal_signame[i]))
        exit_signal = True
    except:
        pass
    if exit_signal:
        sys.exit(1)
for i in range(signal.NSIG):
    try:
        signal.signal(i, p)
    except:
        pass


n_lines = 0
while True:
    sys.stderr.write("waiting for input (q to quit) > ")
    try:
        signal_received = False
        line = sys.stdin.readline()
    except:
        if not signal_received:
            sys.stderr.write("Illegal input received\n")
        if exit_signal:
            sys.exit(1)
    else:
        if line:
            n_lines += 1
            if line.lower().startswith("q"):
                sys.stderr.write("Line beginning with %s read -- stopping\n" % line[0])
                break
            else:
                sys.stdout.write("%d %s" % (n_lines, line))
        else:
            sys.stderr.write("End of input\n" )
            break
sys.stderr.write("Exiting after reading %d line(s) from standard input\n" % (n_lines))


