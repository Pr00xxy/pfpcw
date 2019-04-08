# PFPCW
Python Full Page Cache Warmer

## Description

Python cache warming tool used for warming full page cache solutions  
by visting pages in sitemap.xml 

Has built-in support for concurrent threads, randomizing sort order, url parse delay, and more.

Tests has been performed on Wordpress, Magento 1 and 2.

## Installation

### Step 1. Prerequisites
            
   - python3        
    
### Step 2. Download file from repo

* Check the [latest release](https://github.com/Pr00xxy/pfpcw/releases/latest) and download
    
## Parameters and flags

- `--sitemap`   Url to sitemap (Exclusive to `--site`)
- `--site`      Url to site (Exclusive to `--sitemap`)
                _Will try to locate robots.txt for any sitemaps and parse found ones_
- `--delay`     Delay in seconds between url warming (Default: 0)
- `--limit`		Limit of urls to scan. (Default: None)
- `--threads`   Number of concurrent threads to use (Default: 1)
- `-r`			Randomize order of url warming. (Default: False)	
- `-v`          Run in verbose mode. Will print output to terminal
- `-s`			Run in silent mode. Redirects all output to /dev/null

## Usage

    ./pfpcw ( --site <site url> | --sitemap <url to sitemap.xml> ) [--threads <int>] [--delay <int>] [--limit <int>] [-v] [-s] [-r]
    
or you can call the script like this directly from the repository (Stability not guaranteed). 

    python3 <(curl -sS https://raw.githubusercontent.com/Pr00xxy/pfpcw/master/pfpcw.py)
    
### [!] Note from developer
This software can act a stress tester and as a *denial of service* tool.  
Im not taking any responsibility for the usage of this software.
 