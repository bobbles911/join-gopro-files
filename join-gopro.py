#!/usr/bin/env python3
import glob, re, os, sys, subprocess

FFMPEG_FILELIST_NAME = "join-gopro-files.list.temp"
UDTACOPY_PATH = os.path.dirname(os.path.realpath(__file__)) + "/udtacopy/udtacopy"

filePaths = glob.glob("./G*.MP4")
filePaths = [filePath[2:] for filePath in filePaths] # strip "./"

# Find all gopro file parts and also just the *first* files

allPartsRegex = re.compile("^G[HXPO]\d*\.MP4$")
firstPartsRegex = re.compile("^G[HXPO]01\d*\.MP4$")

allVideoParts = set(filter(allPartsRegex.match, filePaths))
firstVideoParts = set(filter(firstPartsRegex.match, filePaths))

if len(allVideoParts) == 0:
	print("No video parts found in current directory!")
	sys.exit()

print("Found video parts", allVideoParts)
print("Start video parts", firstVideoParts)


# Return the two character code part of the video name (e.g. "GX") plus the video number as a 4 character string (e.g. "0012")
def split_video_filename(fileName):
	return (fileName[:2], re.match("^.{4}(\d{4})\.MP4$", fileName).group(1))


# Now for all first parts, organise with their subsequent parts

videoPartLists = []

print("Video part sequences found:")

for firstPart in firstVideoParts:
	videoStartCode, videoNumberStr = split_video_filename(firstPart)
	
	foundVideoParts = [firstPart]
	
	# Iterate through each subsequent video part
	
	currentPart = 2
	
	while True:
		nextPartName = videoStartCode + str(currentPart).zfill(2) + videoNumberStr + ".MP4"
		
		if os.path.isfile(nextPartName):
			foundVideoParts.append(nextPartName)
		else:
			break
		
		currentPart += 1
	
	if len(foundVideoParts) > 1:
		videoPartLists.append(foundVideoParts)
		print(foundVideoParts)


if len(videoPartLists) == 0:
	print("No sequences found, nothing to do.")
	sys.exit()

print("Now processing...")

for videoParts in videoPartLists:
	# get modification time of first part
	mtime = os.path.getmtime(videoParts[0])
	
	# Write the part names to a file list for ffmpeg
	with open(FFMPEG_FILELIST_NAME, "w") as fp:
		for partName in videoParts:
			fp.write("file '" + partName + "'\n")
	
	# Create the output file name
	videoStartCode, videoNumberStr = split_video_filename(videoParts[0])
	outputFileName = videoStartCode + videoNumberStr + "_combined.mp4"
	
	# Run ffmpeg
	print(videoParts[0], "ffmpeg concatenating")
	
	ffmpegArgs = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", FFMPEG_FILELIST_NAME, "-c", "copy", "-map", "0:0", "-map", "0:1", "-map", "0:3", outputFileName]
	
	print(ffmpegArgs)
	
	complete = subprocess.run(ffmpegArgs)
	complete.check_returncode()
	
	# Run the gopro "udtacopy" tool
	print(videoParts[0], "running udtacopy")
	
	udtacopyArgs = [UDTACOPY_PATH, videoParts[0], outputFileName]
	print(udtacopyArgs)
	
	complete = subprocess.run(udtacopyArgs)
	
	if complete.returncode != 1:
		print("udtacopy failed with unexpected return code", complete.returncode)
		sys.exit(1)
	
	# Keep the old modification time just because that's nice
	os.utime(outputFileName, (mtime, mtime))


# Clean up
os.remove(FFMPEG_FILELIST_NAME)

print("Fin.")


