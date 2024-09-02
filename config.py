import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'mto.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'whg58467458yh54w0yu3tgjtrjyt9up76rki4soeu'
