#!/bin/bash

cd ../hapidocindexer

# Run hapidocdownloader
cd hapidocdownloader
printf '\n%s\n\n' "###Start of hapidocdownloader..."
/root/anaconda/bin/python main.py
printf '%s\n\n' "###End of hapidocdownloader..."
cd ..

# Set up hapidoccore
DIR=/hapidocindexer/hapidoccore/data
if [ -d "$DIR" ]; then
    printf '%s\n' "Removing ($DIR)"
    rm -rf "$DIR"
fi

DIR=/hapidocindexer/hapidoccore/data/dataset/source/client_files
printf '%s\n' "Creating ($DIR)"
mkdir -p "$DIR"
DIR=/hapidocindexer/hapidoccore/data/dataset/source/example_files
printf '%s\n\n' "Creating ($DIR)"
mkdir -p "$DIR"
DIR=/hapidocindexer/hapidoccore/results
printf '%s\n' "Creating ($DIR)"
mkdir -p "$DIR"

# Copy files from hapidocdownloader to hapidoccore
printf '\n%s\n' "#Copying files from hapidocdownloader to hapidoccore"
projects=($(ls -d ./hapidocdownloader/files/*/))
for project_path in "${projects[@]}"
do
	project=$(basename $project_path)
	DIR=/hapidocindexer/hapidoccore/data/dataset/source/client_files/$project/
	printf '%s\n' "Creating ($DIR)"
	mkdir -p "$DIR"
	DIR=/hapidocindexer/hapidoccore/data/dataset/source/example_files/$project/
	printf '%s\n' "Creating ($DIR)"
	mkdir -p "$DIR"
	cp -r hapidocdownloader/files/$project/*.java hapidoccore/data/dataset/source/client_files/$project/
	cp -r hapidocdownloader/files/$project/*.java hapidoccore/data/dataset/source/example_files/$project/
	cp -r hapidocdownloader/files/$project/files_urls.json hapidoccore/data/dataset/source/example_files/$project/files_urls.json
done

# Run hapidoccore
cd hapidoccore
printf '\n%s\n\n' "###Start of hapidoccore..."
/root/anaconda/bin/python main.py
printf '%s\n\n' "###End of hapidoccore..."
cd ..

# Copy files from hapidoccore to hapidocdb
projects=($(ls -d ./hapidoccore/results/*/))
for project_path in "${projects[@]}"
do
	project=$(basename $project_path)
	DIR=/hapidocindexer/hapidocdb/files/$project/
	printf '%s\n' "Creating ($DIR)"
	mkdir -p "$DIR"
	cp -r hapidoccore/results/$project/ranked_files.json hapidocdb/files/$project/ranked_files.json
	cp -r hapidoccore/data/dataset/source/example_files/$project/files_urls.json hapidocdb/files/$project/files_urls.json
	cp -r hapidoccore/results/$project/ranked/ hapidocdb/files/$project/ranked/
done

# Run hapidocdb
cd hapidocdb
/root/anaconda/bin/python main.py
cd ..
