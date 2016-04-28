# coding=utf-8

###
# Copyright (c) 2016, Amaury Carrade
# CeCILL-B license
#
###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Tea')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x

from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse


class Tea(callbacks.Plugin):
    """Retrieves infos about tea from MariageFreres"""
    threaded = True

    @wrap([rest('text')])
    def tea(self, irc, msg, args, tea_name):
        """<tea ID or name>

        Retrieves infos about tea from Mariage Frères"""
        infos = self._get_infos(tea_name)

        if not infos:
            irc.error('Je n\'ai pas réussi à trouver ce thé, désolé.')
            return

        irc.reply(str(ircutils.bold(infos['name']) + ' - ' + infos['description']), prefixNick=False)
        irc.reply(str(ircutils.bold('Conseils de préparation : ' + infos['tips'])), prefixNick=False)

    @wrap([rest('text')])
    def teadesc(self, irc, msg, args, tea_name):
        """<tea ID or name>

        Retrieves infos about tea from Mariage Frères"""
        infos = self._get_infos(tea_name)

        if not infos:
            irc.error('Je n\'ai pas réussi à trouver ce thé, désolé.')
            return

        irc.reply(str(ircutils.bold(infos['name']) + ' - ' + infos['description']), prefixNick=False)
        irc.reply(str(ircutils.bold('Conseils de préparation : ' + infos['tips'])), prefixNick=False)
        irc.reply(str(ircutils.italic(infos['long_description'])), prefixNick=False)

    thé = tea
    thédesc = teadesc

    def _get_infos(self, tea):
        try:
            return self._load_tea_from_id(int(tea))
        except ValueError:
            return self._load_tea_from_name(tea)

    def _load_tea_from_id(self, tea_id):
        if tea_id is None:
            return None

        tea_profile_page = None

        for url in self.registryValue('mariagefreres.result_urls'):
            r = self._load_mariage_url(url.format('pomf-slug', tea_id))
            if not r:
                continue

            tea_profile_page = r.content
            break

        if not tea_profile_page:
            return None

        return self._retrieve_tea_data_from_document(tea_profile_page)

    def _load_tea_from_name(self, tea_name):
        s = requests.Session()
        s.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.0'})

        homepage = self.registryValue('mariagefreres.homepage')

        # Loads the homepage before to act like a visitor and load cookies
        s.get(homepage)

        r = s.post(homepage, data={
            'WD_BUTTON_CLICK_': 'M3',
            'WD_ACTION_': '',
            'M9': tea_name,
            'M22': '',
            'M65': '-1',
            'M65_DEB': '1',
            '_M65_OCC': '0',
            'M73': '-1',
            'M73_DEB': '1',
            '_M73_OCC': '0'
        })

        if r.status_code >= 300 or r.url.lower() == self.registryValue('mariagefreres.no_results_url').lower():
            return None

        soup = BeautifulSoup(r.text, 'html.parser')

        first_result_link = soup.find(class_='ancragecenter').find('a')

        print(first_result_link)
        print(first_result_link.get('href'))

        root = urlparse(homepage).hostname
        tea_url = 'http://' + root + '/FR/' + first_result_link.get('href')

        r = self._load_mariage_url(tea_url)
        if not r:
            return None

        return self._retrieve_tea_data_from_document(r.text)

    @staticmethod
    def _retrieve_tea_data_from_document(html_document):
        soup = BeautifulSoup(html_document, 'html.parser')

        tea_name = str(soup.h1.text).replace('®', '')
        tea_description = str(soup.h2.text).replace('\r\n', ' ').replace('  ', ' ')

        tea_long_description = str(soup.find(id='fiche_desc').text).replace('\r', '')

        tips_tag = soup.find(id='fiche_conseil_prepa')
        tips = tips_tag.contents[2] if len(tips_tag.contents) > 2 else tips_tag.text

        return {
            'name': tea_name,
            'description': tea_description,
            'long_description': tea_long_description,
            'tips': tips
        }

    @staticmethod
    def _load_mariage_url(url):
        r = requests.get(url)
        if r.status_code >= 300 or 'accueil.html' in r.url:  # Handles 404-as-redirect-to-home behavior
            return None

        return r


Class = Tea


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
