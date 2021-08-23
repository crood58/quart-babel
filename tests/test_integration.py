# -*- coding: utf-8 -*-
from __future__ import with_statement
import py

import asyncio
import pytest
import pytest_asyncio.plugin

import quart
from babel.support import NullTranslations

import quart_babel as babel
from quart_babel import get_translations, gettext, lazy_gettext

@pytest.mark.asyncio 
async def test_no_request_context():
    b = babel.Babel()
    app = quart.Quart(__name__)
    b.init_app(app)

    async with app.app_context():
        assert isinstance(get_translations(), NullTranslations)

@pytest.mark.asyncio 
async def test_multiple_directories():
    """
    Ensure we can load translations from multiple directories.

    This also ensures that directories without any translation files
    are not taken into account.
    """
    b = babel.Babel()
    app = quart.Quart(__name__)

    app.config.update({
        'BABEL_TRANSLATION_DIRECTORIES': ';'.join((
            'translations',
            'renamed_translations'
        )),
        'BABEL_DEFAULT_LOCALE': 'de_DE'
    })

    b.init_app(app)

    async with app.test_request_context("/", method="GET"):
        translations = b.list_translations()

        assert(len(translations) == 2)
        assert(str(translations[0]) == 'de')
        assert(str(translations[1]) == 'de')

        assert gettext(
            u'Hello %(name)s!',
            name='Peter'
        ) == 'Hallo Peter!'

@pytest.mark.asyncio 
async def test_multiple_directories_different_domain():
    """
    Ensure we can load translations from multiple directories with a
    custom domain.
    """
    b = babel.Babel()
    app = quart.Quart(__name__)

    app.config.update({
        'BABEL_TRANSLATION_DIRECTORIES': ';'.join((
            'translations_different_domain',
            'renamed_translations'
        )),
        'BABEL_DEFAULT_LOCALE': 'de_DE',
        'BABEL_DOMAIN': 'myapp'
    })

    b.init_app(app)

    async with app.test_request_context("/", method="GET"):
        translations = b.list_translations()

        assert(len(translations) == 2)
        assert(str(translations[0]) == 'de')
        assert(str(translations[1]) == 'de')

        assert gettext(
            u'Hello %(name)s!',
            name='Peter'
        ) == 'Hallo Peter!'
        assert gettext(u'Good bye') == 'Auf Wiedersehen'

@pytest.mark.asyncio 
async def test_different_domain():
    """
    Ensure we can load translations from multiple directories.
    """
    b = babel.Babel()
    app = quart.Quart(__name__)

    app.config.update({
        'BABEL_TRANSLATION_DIRECTORIES': 'translations_different_domain',
        'BABEL_DEFAULT_LOCALE': 'de_DE',
        'BABEL_DOMAIN': 'myapp'
    })

    b.init_app(app)

    async with app.test_request_context("/", method="GET"):
        translations = b.list_translations()

        assert(len(translations) == 1)
        assert(str(translations[0]) == 'de')

        assert gettext(u'Good bye') == 'Auf Wiedersehen'


def test_lazy_old_style_formatting():
    lazy_string = lazy_gettext(u'Hello %(name)s')
    assert lazy_string % {u'name': u'test'} == u'Hello test'

    lazy_string = lazy_gettext(u'test')
    assert u'Hello %s' % lazy_string == u'Hello test'



