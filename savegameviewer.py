from src.constants import PATH_SAVES
import glob, os, shelve

if __name__ == "__main__":
    saves = glob.glob(os.path.join(PATH_SAVES, "*"))
        
    print("Available save games:")
    for i in range(len(saves)):
        dirs = saves[i].split("\\")
        saves[i] = os.path.join(saves[i], dirs[-1])
        print("[%d] %s" % (i, dirs[-1]))
    done = False
    while not done:
        try:
            index = int(input("Which save game should be opened? > "))
            if index >= len(saves) or index < 0:
                print("The integer is out of bounds.")
            else:
                done = True
        except ValueError:
            print("Enter an integer.")
    
    print("===============")
    print(saves[index])
    sg = shelve.open(saves[index])
    c = 1
    for k in sg.dict.keys():
        k = str(k, sg.keyencoding)
        try:
            val = sg.get(k, '<Object reference>')
        except Exception as e:
            val = e
        print("  (%d)  '%s'" % (c, k))
        if type(val) is tuple:
            print("        val=%s" % (val,))
        elif type(val) is list:
            print("        val=")
            for item in val:
                if type(item) is tuple:
                    print("            %s" % (item,))
                else:
                    print("            %s" % item)
        else:
            print("        val=%s" % val)
        c += 1