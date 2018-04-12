#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#######################################################################
#
# VidCutter - media cutter & joiner
#
# copyright © 2018 Pete Alexandrou
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#######################################################################

import logging
import os
import platform
import sys
import time
from datetime import datetime

from PyQt5.Qt import PYQT_VERSION_STR, QT_VERSION_STR
from PyQt5.QtCore import QObject, QSize, QUrl, Qt
from PyQt5.QtGui import QCloseEvent, QPixmap
from PyQt5.QtWidgets import (qApp, QDialog, QDialogButtonBox, QHBoxLayout, QLabel, QSizePolicy, QStyleFactory,
                             QTabWidget, QTextBrowser, QVBoxLayout, QWidget)

import vidcutter


class About(QDialog):
    def __init__(self, ffmpeg_service: QObject, mpv_service: QObject, parent: QWidget, f=Qt.WindowCloseButtonHint):
        super(About, self).__init__(parent, f)
        self.parent = parent
        self.logger = logging.getLogger(__name__)
        self.ffmpeg_service = ffmpeg_service
        self.mpv_service = mpv_service
        self.theme = self.parent.theme
        self.setObjectName('aboutwidget')
        self.setContentsMargins(0, 0, 0, 0)
        self.setWindowModality(Qt.ApplicationModal)
        pencolor1 = '#9A45A2' if self.theme == 'dark' else '#642C68'
        pencolor2 = '#FFF' if self.theme == 'dark' else '#000'
        appversion = qApp.applicationVersion()
        apparch = platform.architecture()[0]
        builddate = About.builddate()
        pythonlabel, qtlabel = QLabel(self), QLabel(self)
        pythonlabel.setPixmap(QPixmap(':/images/{}/python.png'.format(self.theme)))
        qtlabel.setPixmap(QPixmap(':/images/qt.png'))
        rowspan = 1
        builddate_content = ''
        if builddate is not None:
            rowspan = 2
            builddate_content = '''
            <tr valign="top">
                <td style="vertical-align:middle;text-align:right;font-size:10pt;font-weight:500;color:{pencolor1};">
                    build date:
                </td>
                <td>&nbsp;</td>
                <td style="font-size:10pt;font-weight:400;">{builddate}</td>
            </tr>'''.format(**locals())
        headercontent = '''
        <div style="font-family:'Futura-Light';font-size:40px;font-weight:400;color:{pencolor1};margin:0;padding:0;">
            <span style="font-size:58px;">V</span>ID<span style="font-size:58px;">C</span>UTTER
        </div>
        <table border="0" cellpadding="0" cellspacing="0" style="margin:10px 0 0 10px;">
            <tr valign="top">
                <td rowspan="{rowspan}" width="30"></td>
                <td style="vertical-align:middle;text-align:right;font-size:10pt;font-weight:500;color:{pencolor1};">
                    version:
                </td>
                <td>&nbsp;</td>
                <td>
                    <span style="font-size:18px;font-weight:400;">{appversion}</span>
                    &nbsp;<span style="font-size:10pt;margin-left:5px;">({apparch})</span>
                </td>
            </tr>
            {builddate_content}
        </table>'''.format(**locals())
        creditslayout = QVBoxLayout()
        creditslayout.setContentsMargins(0, 0, 0, 0)
        creditslayout.setSpacing(10)
        creditslayout.addStretch(1)
        creditslayout.addWidget(pythonlabel)
        creditslayout.addWidget(qtlabel)
        headerlayout = QHBoxLayout()
        headerlayout.setContentsMargins(0, 5, 0, 5)
        headerlayout.addWidget(QLabel('<img src="{}" />'.format(self.parent.getAppIcon(encoded=True)), self))
        headerlayout.addSpacing(15)
        headerlayout.addWidget(QLabel(headercontent, self))
        headerlayout.addStretch(1)
        headerlayout.addLayout(creditslayout)
        self.tab_about = AboutTab(self)
        self.tab_credits = CreditsTab(self)
        self.tab_license = LicenseTab(self)
        tabs = QTabWidget()
        tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        tabs.addTab(self.tab_about, 'About')
        tabs.addTab(self.tab_credits, 'Credits')
        tabs.addTab(self.tab_license, 'License')
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.close)
        layout = QVBoxLayout()
        layout.addLayout(headerlayout)
        layout.addWidget(tabs, 1)
        layout.addWidget(buttons)
        self.setLayout(layout)
        self.setWindowTitle('About %s' % qApp.applicationName())
        self.setWindowIcon(self.parent.windowIcon())
        self.setMinimumSize(self.get_size(self.parent.parentWidget().scale))

    @staticmethod
    def builddate():
        if getattr(sys, 'frozen', False) and not getattr(sys, '_MEIPASS', False):
            datefile = os.path.realpath(sys.argv[0])
        else:
            import vidcutter.libs.mpv
            datefile = sys.modules['vidcutter.libs.mpv'].__file__
        builddate = datetime.fromtimestamp(os.path.getmtime(datefile)).strftime('%d %b %Y')
        return None if int(builddate.split(' ')[2]) == time.gmtime(0)[0] else builddate.upper()

    @staticmethod
    def get_size(mode: str = 'NORMAL') -> QSize:
        modes = {
            'LOW': QSize(450, 300),
            'NORMAL': QSize(500, 505),
            'HIGH': QSize(1080, 920)
        }
        return modes[mode]

    def closeEvent(self, event: QCloseEvent) -> None:
        self.tab_about.deleteLater()
        self.tab_credits.deleteLater()
        self.tab_license.deleteLater()
        self.deleteLater()
        event.accept()


class BaseTab(QTextBrowser):
    def __init__(self, parent=None):
        super(BaseTab, self).__init__(parent)
        self.setOpenExternalLinks(True)
        if parent.theme == 'dark':
            bgcolor = 'rgba(12, 15, 16, 210)'
            pencolor = '#FFF'
        else:
            bgcolor = 'rgba(255, 255, 255, 200)'    
            pencolor = '#000'
        self.setStyleSheet('''
            QTextBrowser {{
                background-color: {bgcolor};
                color: {pencolor};
            }}'''.format(**locals()))


class AboutTab(BaseTab):
    def __init__(self, parent):
        super(AboutTab, self).__init__(parent)
        self.parent = parent
        spacer = '&nbsp;&nbsp;&nbsp;'
        # noinspection PyBroadException
        try:
            mpv_version = self.parent.mpv_service.version()
        except Exception:
            self.parent.logger.exception('mpv version error', exc_info=True)
            mpv_version = '<span style="color:maroon; font-weight:bold;">MISSING</span>'
        # noinspection PyBroadException
        try:
            ffmpeg_version = self.parent.ffmpeg_service.version()
        except Exception:
            self.parent.logger.exception('ffmpeg version error', exc_info=True)
            ffmpeg_version = '<span style="color:maroon; font-weight:bold;">MISSING</span>'
        html = '''
<style>
    table { width: 100%%; font-family: "Noto Sans UI", sans-serif; background-color: transparent; }
    a { color: %s; text-decoration: none; font-weight: bold; }
</style>
<table border="0" cellpadding="8" cellspacing="4">
    <tr>
        <td>
            <table border="0" cellpadding="0" cellspacing="0">
                <tr valign="bottom">
                    <td>
                        <p style="font-size:13px;">
                            <b>libmpv:</b> %s
                            %s
                            <b>FFmpeg:</b> %s
                            <br/>
                            <b>Python:</b> %s
                            &nbsp;&nbsp;&nbsp;
                            <b>Qt:</b> %s
                            &nbsp;&nbsp;&nbsp;
                            <b>PyQt:</b> %s
                        </p>
                        <p style="font-size:13px;">
                            Copyright &copy; %s <a href="mailto:%s">%s</a>
                            <br/>
                            Website: <a href="%s" target="_blank">%s</a>
                        </p>
                        <p style="font-size:13px;">
                            Found a bug? You can <a href="%s">REPORT IT HERE</a>.
                        </p>
                    </td>
                    <td align="right">
                        <a href="https://www.jetbrains.com/pycharm"><img src=":/images/pycharm.png" /></a>
                    </td>
                </tr>
            </table>
            <p style="font-size:12px;">
                Built in Python with the help of <a href="https://www.jetbrains.com/pycharm">PyCharm Professional</a>
                using an open-source development license donated by its wickedly cool creators at
                <a href="https://www.jetbrains.com">JetBrains</a>.
            </p>
            <p style="font-size:11px; margin-top:15px;">
                This program is free software; you can redistribute it and/or
                modify it under the terms of the GNU General Public License
                version 3, or (at your option) any later version. This software uses code
                produced by the <a href="https://mpv.io">mpv</a> and
                <a href="https://www.ffmpeg.org">FFmpeg</a> projects under the
                <a href="https://www.gnu.org/licenses/old-licenses/gpl-2.0.html">GPLv2.0</a> and
                <a href="https://www.gnu.org/licenses/old-licenses/lgpl-2.1.en.html">LGPLv2.1</a>
                licenses respectively.
            </p>
        </td>
    </tr>
</table>''' % ('#EA95FF' if self.parent.theme == 'dark' else '#441D4E',
               mpv_version, spacer, ffmpeg_version, sys.version.split(' ')[0], QT_VERSION_STR,
               PYQT_VERSION_STR, datetime.now().year, vidcutter.__email__, vidcutter.__author__,
               vidcutter.__website__, vidcutter.__website__, vidcutter.__bugreport__)
        self.setHtml(html)


class CreditsTab(BaseTab):
    def __init__(self, parent):
        super(CreditsTab, self).__init__(parent)
        self.parent = parent
        self.setObjectName('credits')
        self.setHtml('''
        <style>
            table { background-color: transparent; }
            a { color:%s; text-decoration:none; font-weight:bold; }
            a:hover { text-decoration:underline; }
        </style>
        <h3 style="text-align:center;">CREDITS</h3>
        <p>
            This application either uses code and tools from the following projects in part or in their entirety as
            deemed permissable by each project's open-source license.
        </p>
        <table border="0" cellpadding="10" cellspacing="0" width="400" align="center" style="margin-top:10px;">
            <tr>
                <td width="200">
                    <p>
                        <a href="https://github.com/marcan/pympv">pympv</a>
                        -
                        GPLv3+
                    </p>
                    <p>
                        <a href="http://ffmpeg.org">FFmpeg</a>
                        -
                        GPLv2+
                    </p>
                    <p>
                        <a href="https://www.riverbankcomputing.com/software/pyqt">PyQt5</a>
                        -
                        GPLv3+
                    </p>
                </td>
                <td width="200">
                    <p>
                        <a href="http://mpv.io">mpv (libmpv)</a>
                        -
                        GPLv2+
                    </p>
                    <p>
                        <a href="http://mediaarea.net/mediainfo">MediaInfo</a>
                        -
                        BSD-style
                    </p>
                    <p>
                        <a href="https://www.qt.io">Qt5</a>
                        -
                        LGPLv3
                    </p>
                </td>
            </tr>
        </table>''' % ('#EA95FF' if self.parent.theme == 'dark' else '#441D4E'))


class LicenseTab(BaseTab):
    def __init__(self, parent):
        super(LicenseTab, self).__init__(parent)
        self.setObjectName('license')
        self.setSource(QUrl('qrc:/license.html'))
        if sys.platform in {'win32', 'darwin'}:
            self.setStyle(QStyleFactory.create('Fusion'))
