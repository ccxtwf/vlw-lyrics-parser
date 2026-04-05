# Vocaloid Lyrics Wiki Lyrics Parser

This is a Python package used to parse individual lyrics from the [Vocaloid Lyrics Wiki](https://vocaloidlyrics.miraheze.org).

## Disclosure
### Copyright disclosure

Original lyrics uploaded to the Vocaloid Lyrics Wiki are copyrighted by their respective rights holders. Organizations involved in music copyright include, but are not limited to, [ASCAP](https://www.ascap.com/help/music-business-101/money-copyright), [BMI](https://www.bmi.com/faq/category/copyright), [JASRAC](https://www.jasrac.or.jp/en/creators/), NexTone, and the [Music Copyright Society of China](https://www.mcsc.com.cn/en/situation.html). Users are responsible for ensuring that their use of lyrics and translations does not infringe on these rights.

The authors of this repository are not responsible for any legal consequences resulting from misuse of lyrics or translations.

All other content hosted on the Vocaloid Lyrics Wiki is licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.en) unless otherwise stated.

### Policy on high-volume API usage and scraping

Vocaloid Lyrics Wiki and the platform it is hosted on, Miraheze, are *volunteer-run* projects. High-volume API usage and scraping should be avoided unless absolutely necessary.

When making network requests to the Vocaloid Lyrics Wiki, make sure to follow proper etiquette:
 - Add a custom User Agent to your requests. The User Agent should contain contact details, e.g. a username or an email. [See this page for more information.](https://meta.miraheze.org/wiki/Tech:User_Agents)
 - You should not make requests at a rate higher than one every 3 seconds.

Failure to follow these rules may result in rate-limiting or blocking by the technology team.

## Setup

1) Clone this repository.
```sh
git clone --recurse-submodules --shallow-submodules https://github.com/ccxtwf/vlw-lyrics-parser.git
```
2) Install the required Python packages using `python -m pip install`.
3) Create a `.env` file on the same directory as `.env.EXAMPLE` if needed.

### Setting up a MediaWiki mirror
By default, this package hits the MediaWiki Action API to convert wikitext to a raw HTML string that it may use to process information more readily. Because hitting the Action API to the live Vocaloid Lyrics Wiki is not ideal, you should prepare a MediaWiki mirror instance on your local device/network to use this package. 

Once a local MediaWiki instance is set up, you can add the following configuration on your `.env`:

```sh
WIKITEXT2HTML_PARSER_API_ENTRYPOINT="http://localhost:8080/api.php"
```

An alternative to setting up a local MediaWiki instance is to use [wikitextprocessor](https://github.com/ccxtwf/wikitextprocessor) (facilitated by the `--wtp` flag in the CLI) to parse the wikitext. However, this feature is still very experimental and is in general less feature-complete than using the Action API to parse wikitext.

### Setting up a custom user agent
Some methods in this package make calls to the live Vocaloid Lyrics wiki. For proper etiquette, it is recommended to setup a custom user agent in your `.env` file, like so:

```sh
# When making HTTP requests to the live wiki, this user agent will be used
CUSTOM_USER_AGENT="<a short description> <contact information>"
```

Your custom user agent should include some contact information (e.g. username on Miraheze, email, or telephone number) to identify you.

## Usage

You can start using the provided command line interface (CLI). To start interacting with the CLI, run the following command:
```sh
python parse.py -h
```

### Parsing lyrics from a live wiki page

The following snippet shows how you may use this package to parse lyrics from the Vocaloid Lyrics Wiki:

```sh
# Prints to console
python parse.py api -t "ハローワールド (Hello World)"

# Save as JSON 
python parse.py api -t "ハローワールド (Hello World)" -o "/path/to/file.json"
```

This method makes calls to the live Vocaloid Lyrics Wiki, so make sure not to make excessive requests via this method.

### Parsing a piece of text into lyrics

The following snippet parses raw wikitext (sourced from the <code>?action=raw</code> output of a wiki page) into a set of lyrics, which may be printed onto the console output or saved as a JSON file.

```sh
# read a string
python parse.py str "<WIKITEXT>"

# read from file page.txt
python parse.py str "$(cat page.txt)"
```

By default this method parses the lyrics by hitting the MediaWiki Action API that you've setup on the [previous section](#setup). You can also use the experimental flag `--wtp` to use [wikitextprocessor](https://github.com/ccxtwf/wikitextprocessor) instead, but bear in mind that wikitextprocessor is less feature-complete.

```sh
python parse.py str "<WIKITEXT>" --wtp
```

### Parsing a MediaWiki export dump into lyrics

The following snippet parses a MediaWiki XML dump into a set of lyrics that are saved onto a SQLITE database or a batch of JSON files.

```sh
# Saves the results onto lyrics.db (SQLITE3 format) in the given directory
python parse.py xml -i /path/to/xml -dir /path/to/output

# Saves the results onto lyrics-1.json, lyrics-2.json, and so on in the given directory
python parse.py xml -i /path/to/xml -dir /path/to/output --output-format json

# Saves the results onto lyrics-1.json, lyrics-2.json, and so on in the given directory
# Saves 100 items per JSON file
python parse.py xml -i /path/to/xml -dir /path/to/output --output-format json -n 100
```

By default this method parses the lyrics by hitting the MediaWiki Action API that you've setup on the [previous section](#setup). You can also use the experimental flag `--wtp` to use [wikitextprocessor](https://github.com/ccxtwf/wikitextprocessor) instead, but bear in mind that wikitextprocessor is less feature-complete.

```sh
python parse.py xml -i /path/to/xml -dir /path/to/output --wtp
```