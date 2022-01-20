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
              ".mpeg", ".mov", ".mp4", ".m4v", ".mpg"]
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
for (dirpath, dirnames, filenames) in os.walk(str(sys.argv[1])):
    for filename in filenames:
        filePathName = os.path.join(os.path.abspath(dirpath), filename)
        files.append(filePathName)
files = np.array(files)
print(f"\nFound {len(files)} files")

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
        if splitted[1]=='json': # sometimes .json doesn't have other extension...
            continue
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
print("\nWill now corrrect truncated json file names (when longer than 46 chars):")
files = []
for (dirpath, dirnames, filenames) in os.walk(str(sys.argv[1])):
    for filename in filenames:
        filePathName = os.path.join(os.path.abspath(dirpath), filename)
        files.append(filePathName)
files = np.array(files)

updateTooLong = 0
for filePathNameExt in files:
    fileExt = '.' + filePathNameExt.rsplit('.',1)[-1]
    fileNameNoExt = filePathNameExt.rsplit('/',1)[-1].rsplit('.',1)[0]
    filePathNameNoJson = filePathNameExt.rsplit('.',1)[0]

    if fileExt=='.json' and len(fileNameNoExt)==46:
        # if media already exists, it means there is no error
        if sum(filePathNameNoJson==file for file in files)==0:
            possibleIds = np.array(list(fileNameNoExt in file for file in files), dtype='bool')
            possibleFiles = files[possibleIds]
            possibleFiles = possibleFiles[np.array(list('.json' not in file for file in possibleFiles), dtype='bool')]
            if possibleFiles.size==1:
                os.rename(filePathNameExt, possibleFiles[0] + '.json')
    #            print(possibleFiles)
                updateTooLong+=1

print(f"    Fixed {updateTooLong} file(s) for such error")


# Some files end with -modifié before type extension, which is a duplicate of the original so without json file. Just duplicate the json of the original without -modifié
print(f"\nSome files end with '-modifié' before type extension, which is a duplicate of the original so without json file. Just duplicate the json of the original without -modifié:")

## Re-scan the files
files = []
for (dirpath, dirnames, filenames) in os.walk(str(sys.argv[1])):
    for filename in filenames:
        filePathName = os.path.join(os.path.abspath(dirpath), filename)
        files.append(filePathName)
files = set(files)

updatedModified = 0

for filePathNameExt in files:
    fileExt = '.' + filePathNameExt.rsplit('.',1)[-1]
    if not "-modifié" in filePathNameExt: # pre-skip this file to save a lot of time
        continue
    if any(fileExt==ext for ext in extensions):
        # check if corresponding .json file exists
        jsonFile = filePathNameExt + '.json'
        if jsonFile not in files:
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
for (dirpath, dirnames, filenames) in os.walk(str(sys.argv[1])):
    for filename in filenames:
        filePathName = os.path.join(os.path.abspath(dirpath), filename)
        files.append(filePathName)
files = np.array(files)

noMatch=0
lowCaseFiles = np.char.lower(files) # here we don't really care if it's exact and perfect per case, only that each has a json
onlyJsons = set([file for file in lowCaseFiles if file.endswith(".json")]) # save time for each run no need to check agains all !
for filePathNameExt in lowCaseFiles:
    fileExt = '.' + filePathNameExt.rsplit('.',1)[-1]
    if any(fileExt==ext for ext in extensions):
        # check if corresponding .json file exists
        jsonFile = filePathNameExt + '.json'
#        correspJsons = (np.char.lower(jsonFile)==onlyJsons)
        if jsonFile not in onlyJsons:
            noMatch+=1
            print(f"No .json for: {filePathNameExt}")

print(f"\n    Couldn't find .json for {noMatch} element(s).")
#    if ').json' in filePathNameExt:
