== USAGE ==

  pool.py POOL_NUMBER [-h] [--version] [-s] [-u USER] [-p PASS] [-f FOLDER] [-n TEMPLATE] [-m] [-c RETRIES_ON_CORRUPT_FILE] [-t TIMEOUT]

  
== OPTIONS EXPLAINED ==

  -h, --help
	Show available options.

  --version
	Show DanbooruPoolDownloader version and exit.
  
  -s, --settings
	Change the settings, this is recommended if you are planning to use the script many times and don't want to write all the
	options when calling it.
  
  -u USER, --user=USER, -p PASSWORD, -password=PASSWORD
	Login to your danbooru account before downloading, these fields are blank by default.

  -f FOLDER, --folder=FOLDER
	Change the folder where the files will be downloaded to, the default is to download them to a subfolder in the folder pool.py is in.
	
  -n TEMPLATE --name=TEMPLATE
	Change how files are renamed after download, files are named [n]id_md5.extension by default. More in the "Filename template" section.

  --no_md5
	Disables the comparison between the downloaded file and the one stated in the danbooru post.

  -c RETRIES, --corrupt_retries=RETRIES
	Change how many times files whose md5 doesn't match with teh official one are retried before skipping.

  -t TIMEOUT --timeout=TIMEOUT
	Changes how many seconds BooruPoolDL should wait for Danbooru to reply before stopping the download.

	
== FILENAME TEMPLATES ==

This template controls how downloaded files are named, it uses key substitution with info from the post, all the keys must start with '$', (eg. $md5)
for example the using the template:
	
	${id}-$md5 (${w}x${h})px

Would result in a file named:

	266930-3f8d0428bb68678ae25ef7081530789c (392x1087)px.jpg

NOTE: When writtin something other than whitespace after a key, the key should be enclosed in curly braces (eg. ${id}_ instead of &id_), 
otherwhise Python will think that the following characters are party of they key and produce an error
	
	
== FILENAME KEYS ==

	$pos	The posiotion of the post inside the pool, useful for pools in which the post order does not follow the logical oreder of the images
	$id		The ID of the post
	$md5	The file md5
	$tags	The tags associated with the image
	$rating	The rating of the post (safe/questionable/explicit)
	$w		The width of the image in pixels
	$h		The height of the image in pixels

	
== QUESTIONS, BUG REPORTS, FEATURE REQUESTS, ETC. ==

Please write them in the appropiate section of the project's sourceforge page (https://sourceforge.net/projects/danboorupooldl/)
or mail them to U.0x202E@gmail.com (please include [question]/[bug]/[request]/[death threat] on the title)


--suomynonA !AnonzWfB9s