import urllib
import urllib2
import zipfile
import os, glob

lang = 'eng'

def searchSeries(name):
	parsedName = urllib.quote_plus(name)
	url = 'https://www.opensubtitles.org/es/search2/sublanguageid-'+lang+'/moviename-'+parsedName
	response = urllib2.urlopen(url)
	source = response.read()
	_FROM = '<td style="width:80%"'
	_TO = '<br/>'
	_OK = '//static.opensubtitles.org/gfx/icons/tv-series.gif'

	RESULTS = {}

	for entry in source.split(_FROM):
		entry = entry.split(_TO)[0]
		if _OK in entry:
			entryName = entry.split('">')[2].split('</a>')[0].replace('\n', ' ')
			entryID = entry.split('idmovie-')[1].split('"')[0]
			RESULTS[entryName] = entryID
	return RESULTS

def searchSeasons(id):
	url = 'https://www.opensubtitles.org/es/ssearch/sublanguageid-'+lang+'/idmovie-'+id
	response = urllib2.urlopen(url)
	source = response.read()
	_FROM = '<td><span id="season-'
	_TO = '"'

	RESULTS = []

	for season in source.split(_FROM):
		season = season.split(_TO)[0]
		if len(season) > 5:	# Skip [0]
			continue
		if int(season) < 1:	# Sometimes there is a -1 season (wtf?)
			continue
		RESULTS.append(season)
	return RESULTS

def searchEpisodes(id, season):
	url = 'https://www.opensubtitles.org/es/ssearch/sublanguageid-'+lang+'/idmovie-'+id
	response = urllib2.urlopen(url)
	source = response.read()
	source = source.split('<span id="season-' + season + '">')[1].split('</abbr></td></tr><tr><td>')[0]
	_FROM = '<span itemprop="episodeNumber">'
	_TO = '</span></a></td>'

	RESULTS = {}

	for episode in source.split(_FROM):
		episode = episode.split(_TO)[0]
		if not '<span itemprop="name">' in episode:	# Skip [0]
			continue
		episodeNumber = episode.split('<')[0]
		episodeName = episode.split('<span itemprop="name">')[1]
		episodeID = episode.split('imdbid-')[1].split('"')[0]
		RESULTS[episodeNumber] = {}
		RESULTS[episodeNumber]['name'] = episodeName
		RESULTS[episodeNumber]['ID'] = episodeID
	return RESULTS

def searchDownloads(id, DCOMMAND):
	url = 'https://www.opensubtitles.org/es/search/sublanguageid-'+lang+'/imdbid-'+id
	url += '/sort-7/asc-0'	# Order by downloads
	response = urllib2.urlopen(url)
	source = response.read()
	source = source.split('<tbody>')[1].split('</tbody>')[0]
	_FROM = '<tr onclick='
	_TO = '</tr>'

	RESULTS = {}

	for download in source.split(_FROM):
		download = download.split(_TO)[0]
		if not '<br/>' in download:	# Skip [0]
			continue
		downloadName = download.split('<br/>')[1].split('<br/>')[0].split('\n')[2]
		if '<span' in downloadName:	# If contains a span tag, remove it
			downloadName = downloadName.split('title="')[1].split('"')[0]

		if not DCOMMAND == '' and not DCOMMAND.lower() in downloadName.lower():	# If there is a download tag and it's not found
			continue	# Skip it

		downloadID = download.split('(')[1].split(',')[0]
		RESULTS[downloadID] = downloadName
	return RESULTS

def download(id):
	'''
	Hi, developer!
	To download the compressed file i'm using the directory:
	http://dl.opensubtitles.org/en/download/vrf-108d030f/sub/
	However, 'vrf-108d030f' seems like a really variable value,
	I have ran some tests, and it seems like it won't change.
	Nevertheless, if it does change sometime, get the value from
	http://osdownloader.org/es/osdownloader.subtitles-download/subtitles/ID
	Starts with 'You will get'. Have a nice day!
	'''
	url = 'http://dl.opensubtitles.org/en/download/vrf-108d030f/sub/'+id
	urllib.urlretrieve(url, 'sub.zip')
	zip = zipfile.ZipFile('sub.zip', 'r')
	zip.extractall('.')
	zip.close()
	os.remove('sub.zip')
	os.remove(glob.glob('*.nfo')[0])

def main():
	print "OPEN SUBTITLES DOWNLOADER"
	print "-------------------------"
	print ""
	global lang
	lang = raw_input('LANG [eng]:> ')
	print "\n"

	name = raw_input(':> ')

	SERIES_RESULTS = searchSeries(name)
	print "\n\n"
	print "Result search of "+name+":"
	SERIES_RESULTS_IDXs = {}
	for idx, result in enumerate(SERIES_RESULTS):
		SERIES_RESULTS_IDXs[idx] = result
		print '['+str(idx)+'] '+result
	print ""
	SERIES = raw_input('>: ')

	SEASONS_RESULTS = searchSeasons(SERIES_RESULTS[SERIES_RESULTS_IDXs[int(SERIES)]])
	print "\n\n"
	print "Choose a season:"
	for result in SEASONS_RESULTS:	# This isn't sorted
		print result
	print ""
	SEASON = raw_input('>: ')

	EPISODES_RESULTS = searchEpisodes(SERIES_RESULTS[SERIES_RESULTS_IDXs[int(SERIES)]], SEASON)
	print "\n\n"
	print "Choose an episode:"
	for result in EPISODES_RESULTS:
		print result+': '+EPISODES_RESULTS[result]['name']
	print ""
	EPISODE = raw_input('>: ')

	print "\n\n"
	print "DOWNLOAD TAG ( e.g.: xvid )"
	print ("(Leave in blank if not used)")
	DCOMMAND = raw_input('>: ')

	DOWNLOADS_RESULTS = searchDownloads(EPISODES_RESULTS[EPISODE]['ID'], DCOMMAND)
	print "\n\n"
	print "Choose a download:"
	DOWNLOADS_RESULTS_IDXs = {}
	for idx, result in enumerate(DOWNLOADS_RESULTS):
		DOWNLOADS_RESULTS_IDXs[idx] = result
		print '['+str(idx)+'] '+DOWNLOADS_RESULTS[result]
	print ""
	DOWNLOAD = raw_input('>: ')

	print "\n"
	download(DOWNLOADS_RESULTS_IDXs[int(DOWNLOAD)])
	print "Subtitle downloaded!"

if __name__ == '__main__':
	main()