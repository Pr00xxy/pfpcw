#!/usr/bin/env python3
from __future__ import print_function
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup
import urllib.request
import threading
import requests
import argparse
import numpy
import time
import gzip
import sys
import ssl
import re
import io

parser = argparse.ArgumentParser(description='description')
required = parser.add_argument_group('required arguments')
optional = parser.add_argument_group('optional arguments')

required.add_argument('--sitemap',  dest='sitemap',  action='store',      default=None)
optional.add_argument('--site',     dest='site',     action='store',      default=None)
optional.add_argument('--delay',    dest='delay',    action='store',      default=0)
optional.add_argument('--threads',  dest='threads',  action='store',      default=1)
optional.add_argument('-v',         dest='verbose',  action='store_true', default=False)
args = parser.parse_args()


class CacheWarmer:
    MAX_TEST_URL = 10
    NO_URLS = 0
    SITE_URLS = []
    PROGRESS = 0
    thread_kill = False
    total_download_time = 0

    def __init__(
            self,
            sitemap_url='',
            delay=0,
            threads=None,
            verbose=False,
            site=None
    ):
        self.sitemap_url = sitemap_url
        self.delay = delay
        self.threads = threads
        self.verbose = verbose
        self.site = site

    def run(self):
        """
        Main function
        :return: bool
        """
        sitemap_content = ''

        if self.sitemap_url:
            print('Downloading sitemap')
            sitemap_content = self.download_link(self.sitemap_url)

        if self.site:
            print('Running in detect mode. Locating sitemaps')
            sitemap_array = self.locate_sitemaps()
            sitemap_content = self.assemble_multiple_sitemap(sitemap_array)

        print('Parsing sitemap')

        url_array = self.parse_sitemap(sitemap_content)
        self.NO_URLS = len(url_array)
        self.SITE_URLS = url_array

        print('Link count: {0}'.format(self.NO_URLS))
        print('Threads: {0} \n'.format(self.threads))
        print('Spawning {0} threads ... \n'.format(self.threads))
        time.sleep(1)

        try:
            thread_pool = self._create_thread_pool(numpy.array_split(numpy.array(self.SITE_URLS), self.threads))

            for thread in thread_pool:
                thread.start()

            while self.PROGRESS < self.NO_URLS:
                time.sleep(1)
                if self.PROGRESS == self.NO_URLS:
                    break

            time.sleep(2)  # Sleep for margin
            print('Warmed {0} links'.format(self.NO_URLS))
            sys.exit(0)

        except (KeyboardInterrupt, SystemExit):
            self.thread_kill = True
            sys.exit(1)

    def assemble_multiple_sitemap(self, sitemaps_array):
        """
        Combines sitemaps_array into a single string

        :param sitemaps_array:
        :return: string
        """
        sitemap_content = ''
        buffer = ''
        failed_sitemaps = []
        for idx, sitemap_url in enumerate(sitemaps_array):

            result = self.download_link(sitemap_url)

            if len(result) < 1:
                buffer += '!'
                failed_sitemaps.append(sitemap_url)
            else:
                buffer += '.'

            print('\r' + buffer, end=' ')

            sitemap_content += result

        return sitemap_content

    def locate_sitemaps(self):
        """
        Returns all sitemap objects in robots.txt

        :return: array
        """
        robots_txt = self.download_link(self.site + '/' + 'robots.txt')

        if robots_txt is False:
            return []

        sitemap_array = re.findall(r'(?:http|https):(?://)(?:[A-z0-9].{0,50})(?:|.xml.gz|.xml)', robots_txt)

        if sitemap_array is None:
            return []

        return sitemap_array

    def download_link(self, link):
        """
        Returns content of weblink.
        Returns uncompressed version of link if compressed

        :param link: web link
        :return: string: content of link
        """
        if self._validate_link(link):
            context = ssl._create_unverified_context()
            try:
                # TODO: Add header
                if '.xml.gz' in link:
                    r = requests.get(link)
                    return gzip.GzipFile(fileobj=io.StringIO(r.content)).read()

                response = urllib.request.urlopen(link, context=context).read()

                if type(response) is bytes:
                    return response.decode('utf-8')

                return response
            except HTTPError as e:
                # if self.verbose:
                #     print('Error code: {0} {1}'.format(e.code, link))
                return ''
            except URLError as e:
                # if self.verbose:
                #     print('Url error: {0}'.format(e))
                return ''
            except Exception as e:
                print(repr(e))
                return ''

    @staticmethod
    def _validate_link(link):
        """
        Check if string is a valid http/ftp/s/ link

        :param link:
        :return: bool:
        """
        regex = re.compile(
            r'^(?:http|ftp)s?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if re.match(regex, link):
            return True
        return False

    def parse_sitemap(self, sitemap_xml):
        """
        return array of <loc> links
        :param sitemap_xml:
        :return:
        """
        soup = BeautifulSoup(sitemap_xml, features='lxml')
        raw_url_array = []

        if soup.find('urlset'):
            raw_url_array = soup.find_all('loc')

        clean_url_array = []
        for url in raw_url_array:
            if self._validate_link(url.text):
                clean_url_array.append(url.text)

        return clean_url_array

    def _create_thread_pool(self, splits):
        """
        Create workers for warming

        :param splits:
        :return:
        """
        threads = []
        for i in range(self.threads):
            t = threading.Thread(target=self._warm, args=(i, numpy.array(splits[i]),))
            threads.append(t)
        return threads

    def _warm(self, worker_id, links):
        """
        Download all links in :param link array.

        :param worker_id:
        :param links:
        :return: bool:
        """
        download_time = 0
        processed = 0

        for link in links:
            try:
                self.PROGRESS += 1
                processed += 1

                if self.thread_kill is True:
                    sys.exit(1)

                if self.delay > 0:
                    time.sleep(float(self.delay))

                download_time_start = time.time()
                if self.download_link(link):
                    download_time += time.time() - download_time_start

                if self.verbose:
                    print('({0}/{1}) ({2}) {3}'.format(self.PROGRESS, self.NO_URLS, worker_id, link))

            except Exception:
                if self.verbose:
                    print('Failed warming link: {0}'.format(link))

        self.total_download_time += download_time
        print('Thread {0} Completed. Processed {1}/{2}'.format(worker_id, processed, len(links)))
        return True


cache_warmer = CacheWarmer(
    sitemap_url=args.sitemap,
    delay=int(args.delay),
    threads=int(args.threads),
    verbose=args.verbose,
    site=args.site
)
cache_warmer.run()
