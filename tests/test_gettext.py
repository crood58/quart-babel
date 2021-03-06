# -*- coding: utf-8 -*-
from __future__ import with_statement

import asyncio
import pytest
import pytest_asyncio.plugin

import quart

import quart_babel as babel
from quart_babel import gettext, lazy_gettext, lazy_ngettext, ngettext

@pytest.mark.asyncio
async def test_basics():
    app = quart.Quart(__name__)
    babel.Babel(app, default_locale='de_DE')

    async with app.test_request_context("/", method="GET"):
        assert gettext(u'Hello %(name)s!', name='Peter') == 'Hallo Peter!'
        assert ngettext(u'%(num)s Apple', u'%(num)s Apples', 3) == \
            u'3 Äpfel'
        assert ngettext(u'%(num)s Apple', u'%(num)s Apples', 1) == \
            u'1 Apfel'

@pytest.mark.asyncio 
async def test_template_basics():
    app = quart.Quart(__name__)
    babel.Babel(app, default_locale='de_DE')

    t = lambda x: quart.render_template_string('{{ %s }}' % x)

    async with app.test_request_context("/", method="GET"):
        assert t("gettext('Hello %(name)s!', name='Peter')") == \
            u'Hallo Peter!'
        assert t("ngettext('%(num)s Apple', '%(num)s Apples', 3)") == \
            u'3 Äpfel'
        assert t("ngettext('%(num)s Apple', '%(num)s Apples', 1)") == \
            u'1 Apfel'
        assert quart.render_template_string('''
            {% trans %}Hello {{ name }}!{% endtrans %}
        ''', name='Peter').strip() == 'Hallo Peter!'
        assert quart.render_template_string('''
            {% trans num=3 %}{{ num }} Apple
            {%- pluralize %}{{ num }} Apples{% endtrans %}
        ''', name='Peter').strip() == u'3 Äpfel'

@pytest.mark.asyncio 
async def test_lazy_gettext():
    app = quart.Quart(__name__)
    babel.Babel(app, default_locale='de_DE')
    yes = lazy_gettext(u'Yes')
    async with app.test_request_context("/", method="GET"):
        assert str(yes) == 'Ja'
        assert yes.__html__() == 'Ja'

    app.config['BABEL_DEFAULT_LOCALE'] = 'en_US'
    async with app.test_request_context("/", method="GET"):
        assert str(yes) == 'Yes'
        assert yes.__html__() == 'Yes'

@pytest.mark.asyncio 
async def test_lazy_ngettext():
    app = quart.Quart(__name__)
    babel.Babel(app, default_locale='de_DE')
    one_apple = lazy_ngettext(u'%(num)s Apple', u'%(num)s Apples', 1)
    async with app.test_request_context("/", method="GET"):
        assert str(one_apple) == '1 Apfel'
        assert one_apple.__html__() == '1 Apfel'
    two_apples = lazy_ngettext(u'%(num)s Apple', u'%(num)s Apples', 2)
    async with app.test_request_context("/", method="GET"):
        assert str(two_apples) == u'2 Äpfel'
        assert two_apples.__html__() == u'2 Äpfel'

@pytest.mark.asyncio 
async def test_lazy_gettext_defaultdomain():
    app = quart.Quart(__name__)
    b = babel.Babel(app, default_locale='de_DE', default_domain='test')
    first = lazy_gettext('first')
    async with app.test_request_context("/", method="GET"):
        assert str(first) == 'erste'
    app.config['BABEL_DEFAULT_LOCALE'] = 'en_US'
    async with app.test_request_context("/", method="GET"):
        assert str(first) == 'first'


def test_list_translations():
    app = quart.Quart(__name__)
    b = babel.Babel(app, default_locale='de_DE')
    translations = b.list_translations()
    assert len(translations) == 1
    assert str(translations[0]) == 'de'

@pytest.mark.asyncio
async def test_no_formatting():
    """
    Ensure we don't format strings unless a variable is passed.
    """
    app = quart.Quart(__name__)
    babel.Babel(app)

    async with app.test_request_context("/", method="GET"):
        assert gettext(u'Test %s') == u'Test %s'
        assert gettext(u'Test %(name)s', name=u'test') == u'Test test'
        assert gettext(u'Test %s') % 'test' == u'Test test'

@pytest.mark.asyncio 
async def test_domain():
    app = quart.Quart(__name__)
    b = babel.Babel(app, default_locale='de_DE')
    domain = babel.Domain(domain='test')

    async with app.test_request_context("/", method="GET"):
        assert domain.gettext('first') == 'erste'
        assert babel.gettext('first') == 'first'

@pytest.mark.asyncio 
async def test_as_default():
    app = quart.Quart(__name__)
    b = babel.Babel(app, default_locale='de_DE')
    domain = babel.Domain(domain='test')

    async with app.test_request_context("/", method="GET"):
        assert babel.gettext('first') == 'first'
        domain.as_default()
        assert babel.gettext('first') == 'erste'

@pytest.mark.asyncio 
async def test_default_domain():
    app = quart.Quart(__name__)
    b = babel.Babel(app, default_locale='de_DE', default_domain='test')

    async with app.test_request_context("/", method="GET"):
        assert babel.gettext('first') == 'erste'

@pytest.mark.asyncio 
async def test_multiple_apps():
    app1 = quart.Quart(__name__)
    b1 = babel.Babel(app1, default_locale='de_DE')

    app2 = quart.Quart(__name__)
    b2 = babel.Babel(app2, default_locale='de_DE')

    async with app1.test_request_context("/", method="GET") as ctx:
        assert babel.gettext('Yes') == 'Ja'

        assert ('de_DE', 'messages') in b1.domain_instance.get_translations_cache(ctx)

    async with app2.test_request_context("/", method="GET") as ctx:
        assert 'de_DE', 'messages' not in b2.domain_instance.get_translations_cache(ctx)

@pytest.mark.asyncio
async def test_cache(mocker):
    load_mock = mocker.patch(
        "babel.support.Translations.load", side_effect=babel.support.Translations.load
    )

    app = quart.Quart(__name__)
    b = babel.Babel(app, default_locale="de_DE")

    @b.localeselector
    def select_locale():
        return the_locale

    # first request, should load en_US
    the_locale = "en_US"
    async with app.test_request_context("/", method="GET") as ctx:
        assert b.domain_instance.get_translations_cache(ctx) == {}
        assert babel.gettext("Yes") == "Yes"
    assert load_mock.call_count == 1

    # second request, should use en_US from cache
    async with app.test_request_context("/", method="GET") as ctx:
        assert set(b.domain_instance.get_translations_cache(ctx)) == {
            ("en_US", "messages")
        }
        assert babel.gettext("Yes") == "Yes"
    assert load_mock.call_count == 1

    # third request, should load de_DE from cache
    the_locale = "de_DE"
    async with app.test_request_context("/", method="GET") as ctx:
        assert set(b.domain_instance.get_translations_cache(ctx)) == {
            ("en_US", "messages")
        }
        assert babel.gettext("Yes") == "Ja"
    assert load_mock.call_count == 2

    # now everything is cached, so no more loads should happen!
    the_locale = "en_US"
    async with app.test_request_context("/", method="GET") as ctx:
        assert set(b.domain_instance.get_translations_cache(ctx)) == {
            ("en_US", "messages"),
            ("de_DE", "messages"),
        }
        assert babel.gettext("Yes") == "Yes"
    assert load_mock.call_count == 2

    the_locale = "de_DE"
    async with app.test_request_context("/", method="GET") as ctx:
        assert set(b.domain_instance.get_translations_cache(ctx)) == {
            ("en_US", "messages"),
            ("de_DE", "messages"),
        }
        assert babel.gettext("Yes") == "Ja"
    assert load_mock.call_count == 2
