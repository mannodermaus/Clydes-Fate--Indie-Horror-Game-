import os
import fnmatch

def Walk(root='.', recurse=True, pattern='*'):
    for path, subdirs, files in os.walk(root):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                yield os.path.join(path, name)
        if not recurse:
            break

def count(root='', format="*", recurse=True):
    files = {}
    format = [f.lower() for f in format]
    for fspec in Walk(root, recurse, '*.py'):
        line_count = 0
        found_some = False
        file = []
        
        for line in open(fspec).readlines():
            line_count += 1
            line = line.strip()
            line_checked = line.lower()
            if line_checked:
                if not line_checked.startswith("#"):
                    for f in format:
                        if f in line_checked:
                            file.append((line_count, line))
                            found_some = True
                            break
        if found_some:
            key = fspec.split("\\")[-1].split(".")[0]
            files[key] = file

    return files

if __name__ == "__main__":
    format = str(eval(input("What do you want to look for? > "))).split()
    dict = count(os.getcwd(), format, True)
    cnt = 0
    for f in dict.keys():
        print("========================================")
        print("%s.py" % f)
        for l in dict[f]:
            print("\t%d : %s" % (l[0], l[1]))
            cnt += 1
    print("\nFound matches: %d" % cnt)