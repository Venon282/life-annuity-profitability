from PyQt6.QtCore import QUrl, QObject, pyqtSignal, pyqtProperty
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest

def GetView(markdown, html_url='./template.html', parent=None):
    with open(html_url, encoding='utf8') as file:
        html = file.read()

    with open('generated.html', 'w', encoding='utf8') as file:
        generated = html.replace('markdown_content_placeholder', markdown)
        file.write(generated)

    view = QWebEngineView(parent=parent)
    # page = Page(view)
    # view.setPage(page)
    view.load(QUrl('file:///generated.html'))
    print('return view')
    return view

class Page(QWebEnginePage):
    def acceptNavigationRequest(self, new_url, navigation_type, is_main_frame):
        if navigation_type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            QDesktopServices.openUrl(new_url)
            return False
        else:
            return super().acceptNavigationRequest(new_url, navigation_type, is_main_frame)
