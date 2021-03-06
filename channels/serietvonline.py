# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canale per serietvonline
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------
import re
import urlparse

from core import config, httptools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "serietvonline"
host        = "https://serietvonline.com"
headers     = [['Referer', host]]

# -----------------------------------------------------------------
def mainlist(item):
    logger.info("streamondemand.serietvonline mainlist")

    itemlist = [Item(channel=__channel__,
                     action="lista_serie",
                     title="[COLOR azure]Lista Novità[/COLOR]",
                     url=("%s/lista-novita/" % host),
                     thumbnail=thumbnail_novita,
                     fanart=thumbnail_lista),
                Item(channel=__channel__,
                     action="lista_serie",
                     title="[COLOR azure]Lista Cartoni Animati e Anime[/COLOR]",
                     url=("%s/lista-cartoni-animati-e-anime/" % host),
                     thumbnail=thumbnail_lista,
                     fanart=thumbnail_lista),
                Item(channel=__channel__,
                     action="lista_serie",
                     title="[COLOR azure]Lista Documentari[/COLOR]",
                     url=("%s/lista-documentari/" % host),
                     thumbnail=thumbnail_lista,
                     fanart=thumbnail_lista),
                Item(channel=__channel__,
                     action="lista_serie",
                     title="[COLOR azure]Lista Serie Tv Anni 50 60 70 80[/COLOR]",
                     url=("%s/lista-serie-tv-anni-60-70-80/" % host),
                     thumbnail=thumbnail_lista,
                     fanart=thumbnail_lista),
                Item(channel=__channel__,
                     action="lista_serie",
                     title="[COLOR azure]Lista serie Alta Definizione[/COLOR]",
                     url=("%s/lista-serie-tv-in-altadefinizione/" % host),
                     thumbnail=thumbnail_lista,
                     fanart=thumbnail_lista),
                Item(channel=__channel__,
                     action="lista_serie",
                     title="[COLOR azure]Lista Serie Tv Italiane[/COLOR]",
                     url=("%s/lista-serie-tv-italiane/" % host),
                     thumbnail=thumbnail_lista,
                     fanart=thumbnail_lista),

                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     action="search",
                     extra='serie',
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]
    return itemlist
# =================================================================

# -----------------------------------------------------------------
def search(item, texto):
    logger.info("streamondemand.serietvonline search " + texto)

    itemlist = []

    url = host + "/?s= " + texto

    data = httptools.downloadpage(url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<a href="([^"]+)"><span[^>]+><[^>]+><\/a>[^h]+h2>(.*?)<'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True), tipo='tv'))

    # Extrae el paginador
    patronvideos = '<div class="siguiente"><a href="([^"]+)">'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title="[COLOR yellow]Torna Home[/COLOR]",
                 folder=True)),
        itemlist.append(
            Item(channel=__channel__,
                 action="serietv",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 extra=item.extra,
                 folder=True))

    return itemlist
# =================================================================

# -----------------------------------------------------------------
def lista_serie(item):
    logger.info("streamondemand.serietvonline novità")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    blocco = scrapertools.find_single_match(data, 'id="lcp_instance_0">(.*?)</ul>')
    patron='<li><a href="(.*?)".*?>(.*?)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle in matches:
        scrapedtitle=scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(Item(channel=__channel__,
                                     action="episodios",
                                     title=scrapedtitle,
                                     fulltitle=scrapedtitle,
                                     url=scrapedurl,
                                     fanart=item.fanart if item.fanart != "" else item.scrapedthumbnail,
                                     show=item.fulltitle,
                                     folder=True),tipo='tv'))

    return itemlist
# =================================================================

# -----------------------------------------------------------------
def episodios(item):
    logger.info("streamondemand.serietvonline episodios")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    blocco = scrapertools.get_match(data, '<table>(.*?)</table>')
    #logger.debug(blocco)

    patron = '<tr><td>(.*?)</td><tr>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)
    scrapertools.printMatches(matches)

    for puntata in matches:
        puntata = "<td class=\"title\">"+puntata
        #logger.debug(puntata)
        scrapedtitle=scrapertools.find_single_match(puntata, '<td class="title">(.*?)</td>')
        scrapedtitle=scrapedtitle.replace(item.title,"")
        itemlist.append(
            Item(channel=__channel__,
                 action="episodios_all",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=puntata,
                 thumbnail=item.scrapedthumbnail,
                 plot=item.scrapedplot,
                 folder=True))
    return itemlist
# =================================================================

# -----------------------------------------------------------------
def episodios_all(item):
    logger.info("streamondemand.serietvonline episodios")
    itemlist = []

    patron = "<a href='(.*?)'[^>]+>[^>]+>(.*?)<\/a>"
    matches = re.compile(patron, re.DOTALL).findall(item.url)

    for scrapedurl,scrapedserver in matches:
        #logger.debug(scrapedurl)
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=item.scrapedtitle,
                 show=item.scrapedtitle,
                 title="[COLOR blue]" + item.title + "[/COLOR][COLOR orange]" + scrapedserver + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=item.scrapedthumbnail,
                 plot=item.scrapedplot,
                 folder=True))

    return itemlist
# =================================================================

# -----------------------------------------------------------------
def findvideos(item):
    itemlist=[]

    data = item.url
    while 'vcrypt' in item.url:
        item.url = httptools.downloadpage(item.url, only_headers=True, follow_redirects=False).headers.get("location")
        data = item.url

    logger.debug(data)

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = item.title
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist
# =================================================================


# -----------------------------------------------------------------
def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand)")
# =================================================================


thumbnail_fanart="https://superrepo.org/static/images/fanart/original/script.artwork.downloader.jpg"
ThumbnailHome = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Dynamic-blue-up.svg/580px-Dynamic-blue-up.svg.png"
thumbnail_novita="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"
thumbnail_lista="http://www.ilmioprofessionista.it/wp-content/uploads/2015/04/TVSeries3.png"
thumbnail_top="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"
thumbnail_cerca="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"
thumbnail_successivo="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png"