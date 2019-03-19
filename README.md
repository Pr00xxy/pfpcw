# PFPCW
Python full page cache warmer

## Description

This project aims to solve the problem of warming FPC enabled websites without building expensive warming solutions. Since sitemaps is indexed by SE crawlers and sitemaps contains public urls I saw it fit to base this warmer on sitemap content.
This project was written as a standalone solution without ties to any existing web framework.

Tests has been performed on 2 Wordpress sites and 2 Magento 1/2 sites.

### [!] Note from developer
This project has been tested and can act a stress tester and in turn as a DOS tool.
Im not taking any responsibility for the usage of this software. Please be a good person

## Installation

### Step 1. Prerequisites
            
   - Python 3        
   
    pip install numpy bs4
    
### Step 2. 
    
## Options

- `--sitemap`    Url to sitemap (Exclusive to `--site`)
- `--site`       Url to site (Exclusive to `--sitemap`)
                _Will scan robots.txt for any sitemaps and parse found ones_
- `--threads`     Number of concurrent threads to use (Default: 1)
- `--delay`       Delay in seconds between page parsings (Default: None)
                _Useful when you don't want to stress the server to much_
- `-v`            Run in verbose mode. Will print output to terminal

## Usage

You can either download the repo or run the latest version by using the following command

    python3 <(curl -sS https://raw.githubusercontent.com/Pr00xxy/pfpcw/master/pfpcw.py)

### How to use

    ./pfpcw ( --site <url 2 site> | --sitemap <url to sitemap.xml> ) [--threads <int>] [--delay <int>] [-v]s