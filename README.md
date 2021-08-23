# Quart Babel

Implements i18n and l10n support for Quart.  This is based on the Python
[babel][] module as well as [pytz][] both of which are installed automatically
for you if you install this library.

The original code for this extension was taken from Flask-Babel. Flask-Babel can be found [here][flask-babel]

# Installation 

Install the extension with the following command:

    $ pip3 install quart-babel

# Usage

To use the extension simply import the class wrapper and pass the Quart app 
object back to here. Do so like this:

    from quart import Quart
    from quart_babel import Babel 

    app = Quart(__name__)
    babel = Babel(app)


# Documention

The documentation for Flask-Babel can be used for Quart-Babel and is available [here][docs].
Just remember to that you need to call quart instead of flask and quart_babel instead of flask_babel. 

[babel]: https://github.com/python-babel/babel
[pytz]: https://pypi.python.org/pypi/pytz/
[flask-babel]: https://flask-babel.tkte.ch/
[docs]: https://flask-babel.tkte.ch/
[semver]: https://semver.org/
