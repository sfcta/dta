#
# this is hacky but I couldn't find an easy way to do it
#

import re, shutil

if __name__ == '__main__':

    # filenames -> [ (regex1, substr1), (regex2, substr2), ...]
    subsitutions = {r"_build\html\script_importFullSanFranciscoNetworkDataset.html":
                    [(re.compile(r"[\\]scripts[\\](\w+).py"), '\scripts\<a href="script_\g<1>.html">\g<1>.py</a>')],
                    r"_build\html\script_createSFNetworkFromCubeNetwork.html":
                    [(re.compile(r'(<span class="n">sanfranciscoScenario</span><span class="o">.</span><span class="n">)(\w+)(</span>)'),
                      '<a href="_generated/dta.DynameqScenario.html#dta.DynameqScenario.\g<2>">\g<1>\g<2>\g<3></a>'),
                     (re.compile(r'(<span class="n">sanfranciscoDynameqNet</span><span class="o">.</span><span class="n">)(\w+)(</span>)'),
                      '<a href="_generated/dta.Network.html#dta.Network.\g<2>">\g<1>\g<2>\g<3></a>')]}     
    
    for infilename in subsitutions.keys():
        
        outfile = open("output.html", "w")
        for line in open(infilename, "r"):

            for (regex, substr) in subsitutions[infilename]:
                oldline = line
                (line, count) = regex.subn(substr, line)
                if count>0:
                    print "make_links: %s" % infilename
                    print "  was: ", oldline
                    print "  new: ", line
        
            outfile.write(line)
        outfile.close()
    
        shutil.move("output.html", infilename)