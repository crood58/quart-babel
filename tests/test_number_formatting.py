# -*- coding: utf-8 -*-
from __future__ import with_statement

from decimal import Decimal

import asyncio
import pytest
import pytest_asyncio.plugin
import quart

import quart_babel as babel

@pytest.mark.asyncio
async def test_basics():
    app = quart.Quart(__name__)
    babel.Babel(app)
    n = 1099

    async with app.test_request_context("/", method="GET"):
        assert babel.format_number(n) == u'1,099'
        assert babel.format_decimal(Decimal('1010.99')) == u'1,010.99'
        assert babel.format_currency(n, 'USD') == '$1,099.00'
        assert babel.format_percent(0.19) == '19%'
        assert babel.format_scientific(10000) == u'1E4'
