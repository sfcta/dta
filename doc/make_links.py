#
# this is hacky but I couldn't find an easy way to do it
#

import re, shutil

if __name__ == '__main__':

    infilename = r"_build\html\script_importFullSanFranciscoNetworkDataset.html"
    script_re = re.compile(r"[\\]scripts[\\](\w+).py")
    
    
    outfile = open("output.html", "w")
    for line in open(infilename, "r"):

        (line, count) = script_re.subn('\scripts\<a href="script_\g<1>.html">\g<1>.py</a>', line)
        if count>0: 
            print "make_links: subbed [%s]" % line
        
        outfile.write(line)
    outfile.close()
    
    shutil.copyfile("output.html", infilename)