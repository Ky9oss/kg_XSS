filename = "../xss_dictionary.txt" 

with open(filename, 'r') as f:
    lines = f.readlines()

with open(filename, 'w') as f:
    for line in lines:
        line = line.rstrip()
        if line.endswith('"'):
            line = line[:-1]
        if line.endswith(','):
            line = line[:-1]
        f.write(line + '\n')
