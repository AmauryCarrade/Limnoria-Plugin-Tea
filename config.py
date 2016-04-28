# coding=utf-8
###
# Copyright (c) 2016, Amaury Carrade
# All rights reserved.
#
#
###

import supybot.conf as conf
import supybot.registry as registry
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Tea')
except:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x


def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified themself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('Tea', True)


Tea = conf.registerPlugin('Tea')
# This is where your configuration variables (if any) should go.  For example:
# conf.registerGlobalValue(Tea, 'someConfigVariableName',
#     registry.Boolean(False, _("""Help for someConfigVariableName.""")))

conf.registerGroup(Tea, 'mariagefreres')

conf.registerGlobalValue(Tea.mariagefreres, 'homepage',
    registry.String(
            'http://www.mariagefreres.com/FR/accueil.html',
            _("""The home page of the Mariage Frères website.""")
    ))

conf.registerGlobalValue(Tea.mariagefreres, 'no_results_url',
    registry.String(
        'http://www.mariagefreres.com/FR/plus_de_thes.html',
        _("""The URL Mariage Frères redirects to if a search leads to no results.
        We have to store that because the HTTP status code is always 200.""")
    ))

conf.registerGlobalValue(Tea.mariagefreres, 'result_urls',
    registry.SpaceSeparatedListOfStrings(
        ['http://www.mariagefreres.com/FR/2-{0}-TC{1}.html', 'http://www.mariagefreres.com/FR/2-{0}-TB{1}.html', 'http://www.mariagefreres.com/FR/2-{0}-T{1}.html'],
        _("""The details pages URLs of the teas, space-separated. The URLs will be tested until one does not leads to a 404 or a redirect to the homepage.
        For each URL, {0} will be replaced with a slug-like placeholder, and {1} with the tea ID.""")
    ))


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
