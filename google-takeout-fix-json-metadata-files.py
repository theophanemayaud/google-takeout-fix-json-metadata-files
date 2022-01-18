# google-takeout-fix-json-metadata-files
# created by Théophane Mayaud for use when downloading large libraries
# from google photos, through / using Google Takeout (takeout.google.com)
# This is intended to work on macOS

# Use this freely, you can simply run it with the first argument being the
# directory to scan and correct

import sys
import os
import shutil
import numpy as np

# define extensions that are used
extensions = [".jpg", ".jpeg", ".png", ".gif", ".heic",
              ".mpeg", ".mov", ".mp4", ".m4v"]
fullExtensions = extensions.copy()
for ext in extensions:
    fullExtensions.append(ext.upper())
extensions=fullExtensions

# check input arguments (folder to scan)
numbArgs = len(sys.argv)
if numbArgs!=2:
    raise ValueError(\
        "To use this utility, you should use the syntax: \n" \
        "python this-utility.py [absolute or relative path to folder to be corrected]'")

# scan files
files = []
dirlist = [str(sys.argv[1])]
while len(dirlist) > 0:
    for (dirpath, dirnames, filenames) in os.walk(dirlist.pop()):
        dirlist.extend(dirnames)
        files.extend(map(lambda n: os.path.join(*n), zip([dirpath] * len(filenames), filenames)))

# First Handle wrongly named numbered files ex :
##.jpeg(1).json ->  (1).jpeg.json
##.jpg(3).json  -> (3).jpg.json
##.png(5).json -> (5).png.json
##.mp4(5).json -> (5).mp4.json
##.mov(1).json -> (1).mov.json

nbAffectedExtNumbParenth = sum( ').json' in file for file in files)
print("\nWill now corrrect wrongly placed number increment ex .jpeg(1).json should be (1).jpeg.json")
print(f"Number of affected files: {nbAffectedExtNumbParenth}")
nbUpdated = 0
for filePathNameExt in files:
    if ').json' in filePathNameExt:
        splitted = filePathNameExt.rsplit('.', 2)
        partBeforeExtensions = splitted[0]
        fileTypeExtension = splitted[1].split('(',1)[0]
        numberInParenth = int(splitted[1].split('(',1)[1].split(')',1)[0])
        correctedName = partBeforeExtensions + '(' + str(numberInParenth) + ').' + fileTypeExtension + '.json'
        
        try:
            os.rename(filePathNameExt, correctedName)
            nbUpdated+=1
        except:
            print(f'Error for file before:{filePathNameExt} after:{correctedName}')
            nbUpdated-=1
print(f"    Corrected {nbUpdated} files")

# Now deal with files with too long names which have been truncated
## It seems that the json file names (so the whole part before .json, that is
## including the media extension as well) cannot be longer than 46 characters !
## Therefore we scan for such, and check if truncated at 46 chargs we find
## the corresponding (and unique) json file !
## Re-scan the files
print("\nWill now corrrect truncated json file names (when longer than 46 chars)")
files = []
dirlist = [str(sys.argv[1])]
while len(dirlist) > 0:
    for (dirpath, dirnames, filenames) in os.walk(dirlist.pop()):
        dirlist.extend(dirnames)
        files.extend(map(lambda n: os.path.join(*n), zip([dirpath] * len(filenames), filenames)))
files = np.array(files)

updateTooLong = 0
for filePathNameExt in files:
    fileExt = '.' + filePathNameExt.rsplit('.',1)[-1]
    fileNameNoExt = filePathNameExt.rsplit('/',1)[-1].rsplit('.',1)[0]
    print(fileNameNoExt)
#    if fileExt=='.json':
#        # check if corresponding .json file exists
#        jsonFile = filePathNameExt + '.json'
#        correspJsons = (jsonFile==files)
#        if True not in correspJsons:
#            noExtFileName = filePathNameExt.rsplit('.',1)[0]
#            if noExtFileName.endswith("-modifié"):
#                noModifiedFileName = noExtFileName.rsplit('-',1)[0]
#                jsonToCopyLowExt = noModifiedFileName+fileExt.lower()+'.json'
#                jsonToCopyUpExt = noModifiedFileName+fileExt.upper()+'.json'
#                if jsonToCopyLowExt in files:
#                    jsonDest = noModifiedFileName+"-modifié"+fileExt+'.json'
#                    shutil.copy(jsonToCopyLowExt, jsonDest)
#                    updatedModified+=1
#                elif jsonToCopyUpExt in files:
#                    jsonDest = noModifiedFileName+"-modifié"+fileExt+'.json'
#                    shutil.copy(jsonToCopyUpExt, jsonDest)
#                    updatedModified+=1
##                    print(f"Fixed -modifié for {filePathNameExt}")
                
print(f"    Fixed {updateTooLong} file(s) for such error")


# Some files end with -modifié before type extension, which is a duplicate of the original so without json file. Just duplicate the json of the original without -modifié
print(f"\nSome files end with '-modifié' before type extension, which is a duplicate of the original so without json file. Just duplicate the json of the original without -modifié:")

## Re-scan the files
files = []
dirlist = [str(sys.argv[1])]
while len(dirlist) > 0:
    for (dirpath, dirnames, filenames) in os.walk(dirlist.pop()):
        dirlist.extend(dirnames)
        files.extend(map(lambda n: os.path.join(*n), zip([dirpath] * len(filenames), filenames)))
files = np.array(files)

updatedModified = 0

for filePathNameExt in files:
    fileExt = '.' + filePathNameExt.rsplit('.',1)[-1]
    if any(fileExt==ext for ext in extensions):
        # check if corresponding .json file exists
        jsonFile = filePathNameExt + '.json'
        correspJsons = (jsonFile==files)
        if True not in correspJsons:
            noExtFileName = filePathNameExt.rsplit('.',1)[0]
            if noExtFileName.endswith("-modifié"):
                noModifiedFileName = noExtFileName.rsplit('-',1)[0]
                jsonToCopyLowExt = noModifiedFileName+fileExt.lower()+'.json'
                jsonToCopyUpExt = noModifiedFileName+fileExt.upper()+'.json'
                if jsonToCopyLowExt in files:
                    jsonDest = noModifiedFileName+"-modifié"+fileExt+'.json'
                    shutil.copy(jsonToCopyLowExt, jsonDest)
                    updatedModified+=1
                elif jsonToCopyUpExt in files:
                    jsonDest = noModifiedFileName+"-modifié"+fileExt+'.json'
                    shutil.copy(jsonToCopyUpExt, jsonDest)
                    updatedModified+=1
#                    print(f"Fixed -modifié for {filePathNameExt}")
                
print(f"    Fixed {updatedModified} file(s) for such error")


# Now check the remaining files that don't have a json corresponding metadata file
print(f"\nWill now check remaining files that still don't match to a json metadata file\nWill check for following media files only: {fullExtensions}")
## Re-scan the files
files = []
dirlist = [str(sys.argv[1])]
while len(dirlist) > 0:
    for (dirpath, dirnames, filenames) in os.walk(dirlist.pop()):
        dirlist.extend(dirnames)
        files.extend(map(lambda n: os.path.join(*n), zip([dirpath] * len(filenames), filenames)))
files = np.array(files)

noMatch=0
noMatchFiles = []
for filePathNameExt in files:
    fileExt = '.' + filePathNameExt.rsplit('.',1)[-1]
    if any(fileExt==ext for ext in extensions):
        # check if corresponding .json file exists
        jsonFile = filePathNameExt + '.json'
        correspJsons = (jsonFile==files)
#        print(correspJsons)
#        print(jsonFile==files)
        if True not in correspJsons:
            noMatch+=1
            noMatchFiles.append(filePathNameExt)
            print(f"Can't find corresponding .json for file={filePathNameExt}")
#        print(filePathNameExt)

print(f"\n    Couldn't find such a match for {noMatch} element(s).")
#    if ').json' in filePathNameExt:
