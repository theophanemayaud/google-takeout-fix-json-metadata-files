# google-takeout-fix-json-metadata-files
When you use google takeout to download your Google Photos library, the .json files can get messy. This python script performs a first scan through the downloaded files, and fixes as many as possible. 


## Small sub script to merge all archives into one

> takeout-merge-folders.py

Use this freely, you have to extract all your google takeout archives in the same folder, and within each extracted folder you should have a `Google Photos` subfolder. This script will merget all these sub `Google Photos` folder into one `Google Photos Takeout Merged` folder in the destination of your choice. You can run it with :

- first argument: source directory where all archives were extracted. It should contain folders multiple folders with inside a Google Photos folder

- second argument: destination directory, where a
           `Google Photos Takeout Merged` folder will be put, and all original files moved to it if no error.


## Some example problems that are adressed by the script :

### Wrongly named numbered files ex :
>.jpeg(1).json ->  (1).jpeg.json
>
>.jpg(3).json  -> (3).jpg.json
>
>.png(5).json -> (5).png.json
>
>.mp4(5).json -> (5).mp4.json
>
>.mov(1).json -> (1).mov.json


### Files with too long names which have been truncated:

It seems that the json file names (so the whole part before .json, that is including the media extension as well) cannot be longer than 46 characters ! Therefore we scan for such, and check if truncated at 46 chargs we find the corresponding (and unique) json file ! 


### Some files end with -modifié

This '-modifié' is placed before type extension, which is a duplicate of the original so without json file. Just duplicate the json of the original without -modifié

NB maybe if your google account is in English, change it to -modified ... ?

## Errors not yet adressed by the script

### Live photos

Live photos are treated by takeout as an image file, a video file, and a json metadata file for the photo only. Notice there is not one json file for each of both image and video files, so all the videos are missing json files !

## Recommendations for using exiftool to then merge .json and media files

### Merge for all files

For all other files, set creation, modification, and metadata date other to the one contained in google's json. Attention, Google gives UTC times plus timezone, but there it puts in UTC only without a timezone, so the zone info is lost (unless GPS coordinates are taken into account...?):

`
exiftool -r -d %s -TagsFromFile %d%F.json '-filemodifydate<$PhotoTakenTimeTimestamp' "-filecreatedate<$PhotoTakenTimeTimestamp" "-GPSAltitude<GeoDataAltitude" "-GPSLatitude<GeoDataLatitude" "-GPSLatitudeRef<GeoDataLatitude" "-GPSLongitude<GeoDataLongitude" "-GPSLongitudeRef<GeoDataLongitude" -overwrite_original_in_place ./
`

### Specific videos quicktime tag

For videos only add the specific tag (quicktime) that apple photo reads for creation time and GPS coordinates (but they can be in the same folder as photos because it only deals with the .mp4 .avi and .mkv extensions), Apple photos then recognizes the position:

`
exiftool -r -d %s -TagsFromFile "%d%F.json" -ext mp4 -ext avi -ext mkv -ext mov -ext mpg -ext m4v -ext webm -ext mpeg -ext wmv '-filemodifydate<$PhotoTakenTimeTimestamp' '-filecreatedate<$PhotoTakenTimeTimestamp' '-QuickTime:CreateDate<PhotoTakenTimeTimestamp' '-QuickTime:GPSCoordinates#<$geoDatalatitude $geoDatalongitude $geoDataaltitude' '-Keys:GPSCoordinates#<$geoDatalatitude $geoDatalongitude $geoDataaltitude' -overwrite_original_in_place ./
`




