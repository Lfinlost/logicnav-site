#!/usr/bin/env python3
"""Генератор страниц сайта ООО «ЛоджикНав».

Запуск из корня репозитория:  python3 tools/build.py
Результат записывается в папку site/. Тексты и метаданные находятся в этом файле.

Настройка берётся из переменной окружения (в GitHub Actions её задаёт workflow):
  SITE_URL           публичный адрес сайта, например https://user.github.io/repo
                     или https://ваш-домен.ru (если есть путь — ссылки подстроятся сами)

Контактная форма работает через mailto: подготовленное письмо открывается
в почтовом приложении посетителя. На сервер сайта ничего не отправляется.
"""
import os
import re
from html import escape
from urllib.parse import urlparse, quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "site")

# ---- Настройки ----------------------------------------------------------
SITE_URL = os.environ.get("SITE_URL", "https://example.ru").rstrip("/")
BASE = urlparse(SITE_URL).path.rstrip("/")   # "" для домена, "/repo" для проектной страницы GitHub Pages
EMAIL = "logicnav@verhost.ru"
LEGAL_NAME = "ООО «Логическая навигация»"
FULL_LEGAL_NAME = "Общество с ограниченной ответственностью «Логическая навигация»"
SHORT_NAME = "ООО «ЛоджикНав»"
OGRN = "1267700240477"
INN = "7736378193"
KPP = "773601001"
OKVED = "26.51.2"
OKVED_DESCRIPTION = "Производство радиолокационной, радионавигационной аппаратуры и радиоаппаратуры дистанционного управления"
YEAR = "2026"

NAV = [
    ("/", "Главная", "home"),
    ("/products/", "Продукция", "products"),
    ("/projects/", "Разработки", "projects"),
    ("/about/", "О компании", "about"),
    ("/contacts/", "Контакты", "contacts"),
]

IMG = "/assets/img/"
PHOTOS = {
    "main": ("ln1ya_assembly_01_main", "Сборка полётного контроллера LN1YA с платой управления питанием и инерциальной системой, основной ракурс"),
    "front": ("ln1ya_assembly_02_front", "Сборка полётного контроллера LN1YA с платой управления питанием и инерциальной системой, вид спереди"),
    "side": ("ln1ya_assembly_03_side", "Сборка полётного контроллера LN1YA с платой управления питанием и инерциальной системой, вид сбоку"),
}

# ---- Значки (простые линейные, 24×24) -----------------------------------
ICONS = {
    "chip": '<rect x="7" y="7" width="10" height="10" rx="1.5"/><path d="M9 3v4M15 3v4M9 17v4M15 17v4M3 9h4M3 15h4M17 9h4M17 15h4"/>',
    "compass": '<circle cx="12" cy="12" r="9"/><path d="m16 8-2 6-6 2 2-6z"/>',
    "activity": '<path d="M3 12h4l3-7 4 14 3-7h4"/>',
    "plane": '<path d="M22 2 11 13M22 2l-7 20-4-9-9-4z"/>',
    "layers": '<path d="m12 2 10 5-10 5L2 7zM2 17l10 5 10-5M2 12l10 5 10-5"/>',
    "grid": '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/>',
    "route": '<circle cx="6" cy="19" r="3"/><circle cx="18" cy="5" r="3"/><path d="M9 19h8.5a3.5 3.5 0 0 0 0-7h-11a3.5 3.5 0 0 1 0-7H15"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    "eye": '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>',
    "package": '<path d="M16.5 9.4 7.5 4.2M21 16V8a2 2 0 0 0-1-1.7l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.7l7 4a2 2 0 0 0 2 0l7-4a2 2 0 0 0 1-1.7zM3.3 7l8.7 5 8.7-5M12 22V12"/>',
    "link": '<path d="M10 13a5 5 0 0 0 7.5.5l3-3a5 5 0 0 0-7-7l-1.7 1.7M14 11a5 5 0 0 0-7.5-.5l-3 3a5 5 0 0 0 7 7l1.7-1.7"/>',
    "bulb": '<path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7c.6.5 1 1.3 1 2.3h6c0-1 .4-1.8 1-2.3A7 7 0 0 0 12 2z"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
}


def icon(name):
    return '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">%s</svg>' % ICONS[name]


def badge(name):
    return '<span class="icon-badge">%s</span>' % icon(name)


def picture(key, sizes, eager=False, cls=""):
    base, alt = PHOTOS[key]
    srcset_w = ", ".join("%s%s-%d.webp %dw" % (IMG, base, w, w) for w in (480, 800, 1280))
    srcset_j = ", ".join("%s%s-%d.jpg %dw" % (IMG, base, w, w) for w in (480, 800, 1280))
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return (
        '<picture>'
        '<source type="image/webp" srcset="%s" sizes="%s">'
        '<img src="%s%s-800.jpg" srcset="%s" sizes="%s" width="1280" height="960" alt="%s" %s%s>'
        '</picture>'
    ) % (srcset_w, sizes, IMG, base, srcset_j, sizes, escape(alt), load, (' class="%s"' % cls) if cls else "")


def lb_button(key, caption, sizes, eager=False):
    """Фото, открывающееся в модальной галерее."""
    base, alt = PHOTOS[key]
    cap = escape(caption, quote=True)
    return (
        '<button type="button" data-lightbox data-full="%s%s-1280.jpg" data-alt="%s" data-caption="%s" '
        'aria-label="Открыть фото в полном размере: %s">%s</button>'
        % (IMG, base, escape(alt, quote=True), cap, cap, picture(key, sizes, eager))
    )


def contact_link(topic):
    return "/contacts/?topic=" + quote(topic)


# ---- Общие блоки страницы -----------------------------------------------
def head(title, desc, path, og_image="og-image.jpg", noindex=False):
    url = SITE_URL + path
    robots = '<meta name="robots" content="noindex, follow">\n' if noindex else ""
    return """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
{robots}<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:locale" content="ru_RU">
<meta property="og:site_name" content="ЛоджикНав">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{site}/assets/img/{og}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#071a37">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/img/favicon-32.png">
<link rel="icon" type="image/png" sizes="192x192" href="/assets/img/favicon-192.png">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=Manrope:wght@600;700;800&display=swap&subset=cyrillic">
<link rel="stylesheet" href="/assets/css/style.css">
</head>
""".format(title=escape(title), desc=escape(desc), robots=robots, url=url, site=SITE_URL, og=og_image)


def header(active):
    items = []
    for href, label, key in NAV:
        if key == active[0]:
            cur = ' aria-current="page"' if active[1] else ' aria-current="true"'
        else:
            cur = ""
        items.append('<li><a href="%s"%s>%s</a></li>' % (href, cur, label))
    return """<body>
<a class="skip-link" href="#main">Перейти к содержимому</a>
<header class="site-header">
<div class="container">
<a class="brand" href="/" aria-label="ЛоджикНав — на главную"><img src="/assets/img/logo_primary.png" width="{w}" height="56" alt="ЛоджикНав"></a>
<button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav"><span class="bars" aria-hidden="true"><i></i></span><span class="nav-toggle-label">Меню</span></button>
<nav class="site-nav" id="site-nav" aria-label="Основное меню">
<ul class="nav-list">
{items}
</ul>
</nav>
<a class="btn btn--sm header-cta" href="/contacts/#request">Отправить запрос</a>
</div>
</header>
""".format(items="\n".join(items), w=round(1216 / 717 * 56))


def footer():
    nav = "\n".join('<li><a href="%s">%s</a></li>' % (h, l) for h, l, _ in NAV)
    return """<footer class="site-footer">
<div class="container">
<div class="footer-grid">
<div class="footer-brand">
<img src="/assets/img/logo_primary_inverse.png" width="{w}" height="84" alt="ЛоджикНав" loading="lazy">
<p>{legal} – российская инженерная компания: электронные устройства, полётные контроллеры и системы мониторинга.</p>
</div>
<div>
<h2>Разделы</h2>
<ul class="footer-nav">
{nav}
</ul>
</div>
<div class="footer-contact">
<h2>Контакты</h2>
<p>{legal}</p>
<p><a href="mailto:{email}">{email}</a></p>
<p>ИНН {inn} · ОГРН {ogrn}</p>
</div>
</div>
<p class="footer-bottom">© {year} {short}</p>
</div>
</footer>
""".format(nav=nav, legal=LEGAL_NAME, short=SHORT_NAME, email=EMAIL, inn=INN, ogrn=OGRN, year=YEAR, w=round(1216 / 717 * 84))


def scripts():
    return """<script src="/assets/js/main.js" defer></script>
<script src="/assets/js/metrika.js" defer></script>
</body>
</html>
"""


def breadcrumbs(crumbs):
    bc = []
    for i, (href, label) in enumerate(crumbs):
        if i == len(crumbs) - 1:
            bc.append('<li><span aria-current="page">%s</span></li>' % label)
        else:
            bc.append('<li><a href="%s">%s</a></li>' % (href, label))
    return '<nav aria-label="Навигационная цепочка"><ol class="breadcrumbs">%s</ol></nav>' % "".join(bc)


def page_hero(crumbs, h1, lead, side="", buttons=""):
    """Первый экран внутренней страницы. side — правая колонка (фото, логотип, информационная карточка)."""
    btn = '<div class="btn-row">%s</div>\n' % buttons if buttons else ""
    text = '<h1>%s</h1>\n<p class="lead">%s</p>\n%s' % (h1, lead, btn)
    if side:
        inner = '<div class="hero-split">\n<div class="hero-text">\n%s</div>\n<div class="hero-side">\n%s\n</div>\n</div>\n' % (text, side)
    else:
        inner = text
    return '<section class="page-hero on-dark">\n<div class="container">\n%s\n%s</div>\n</section>\n' % (breadcrumbs(crumbs), inner)


def section_head(h2, lead=None, hid=None):
    i = ' id="%s"' % hid if hid else ""
    p = "<p>%s</p>" % lead if lead else ""
    return '<div class="section-head"><h2%s>%s</h2>%s</div>' % (i, h2, p)


def check_list(items):
    return '<ul class="check-list">%s</ul>' % "".join("<li>%s</li>" % t for t in items)


def chips(items):
    return '<ul class="chips">%s</ul>' % "".join("<li>%s</li>" % t for t in items)


def steps(items, light=False):
    li = "".join("<li><h3>%s</h3><p>%s</p></li>" % (t, d) for t, d in items)
    return '<ol class="steps%s">%s</ol>' % (" steps--light" if light else "", li)


def tiles(items, cls=""):
    out = "".join(
        '<article class="tile">%s<h3>%s</h3><p>%s</p></article>' % (badge(ic), t, d) for ic, t, d in items
    )
    return '<div class="tiles%s">%s</div>' % ((" " + cls) if cls else "", out)


def principles():
    items = [
        ("Собственные разработки", "Электронные устройства и системы ЛоджикНав – собственные разработки компании."),
        ("Российская компонентная база", "При создании изделий ориентируемся на российскую компонентную базу."),
        ("Инженерный подход", "Последовательно рассматриваем задачу заказчика, прорабатываем требования, создаём опытные решения и проверяем их."),
        ("Индивидуальная работа с запросами", "Подробные сведения об изделиях и разработках обсуждаются со специалистами применительно к вашему проекту."),
    ]
    return '<div class="principles">%s</div>' % "".join("<div><h3>%s</h3><p>%s</p></div>" % it for it in items)


def cta_band(title="Обсудим вашу задачу?", text="Опишите задачу в форме обратной связи: специалисты ЛоджикНав изучат запрос и свяжутся с вами.", topic=None, label="Отправить запрос"):
    href = contact_link(topic) + "#request" if topic else "/contacts/#request"
    return """<section class="section on-dark cta-band" aria-labelledby="cta-title">
<div class="container cta-block">
<div class="cta-text">
<h2 id="cta-title">%s</h2>
<p>%s</p>
</div>
<a class="btn" href="%s">%s</a>
</div>
</section>
""" % (title, text, href, label)


def info_card(title, items):
    return '<aside class="info-card" aria-label="%s"><h2>%s</h2>%s</aside>' % (title, title, check_list(items))


def neutral_media(code, sub=""):
    """Нейтральная типографская плашка вместо изображения оборудования."""
    s = '<span class="neutral-sub">%s</span>' % sub if sub else ""
    return '<div class="card-media card-media--neutral" aria-hidden="true"><span class="neutral-code">%s</span>%s</div>' % (code, s)


def prefix(html):
    """Добавляет BASE ко всем ссылкам вида /... (для сайта в подпапке)."""
    if not BASE:
        return html
    html = re.sub(r'(href|src|action|data-full)="/(?!/)', lambda m: '%s="%s/' % (m.group(1), BASE), html)
    html = re.sub(r'(?<=["\s,])/assets/', BASE + "/assets/", html)  # значения srcset
    return html


def write(path, content):
    full = os.path.join(OUT, path.strip("/"), "index.html") if path != "404" else os.path.join(OUT, "404.html")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(prefix(content))


def board_figure(caption):
    """Изображение платы LN1YA (3D-изображение из презентации), открывается в галерее."""
    alt = "Изображение платы полётного контроллера LN1YA, вид сверху"
    sizes = "(max-width: 860px) 92vw, 460px"
    pic = (
        '<picture><source type="image/webp" srcset="%sln1ya_board-480.webp 480w, %sln1ya_board-750.webp 750w" sizes="%s">'
        '<img src="%sln1ya_board-750.jpg" srcset="%sln1ya_board-480.jpg 480w, %sln1ya_board-750.jpg 750w" sizes="%s" '
        'width="750" height="755" alt="%s" loading="lazy" decoding="async"></picture>'
    ) % (IMG, IMG, sizes, IMG, IMG, IMG, sizes, alt)
    btn = (
        '<button type="button" data-lightbox data-full="%sln1ya_board-750.jpg" data-alt="%s" data-caption="%s" '
        'aria-label="Открыть изображение в полном размере: %s">%s</button>'
    ) % (IMG, alt, caption, caption, pic)
    return '<figure class="photo board-photo">%s<figcaption>%s</figcaption></figure>' % (btn, caption)


def variant_cards(items):
    out = "".join(
        '<article class="card variant-card"><h3>%s</h3><p class="designation">Обозначение: %s</p><p>%s</p></article>' % it
        for it in items
    )
    return '<div class="cards cards--3">%s</div>' % out


# =========================================================================
# Главная
# =========================================================================
home = head(
    "ЛоджикНав – разработка электроники и навигационных решений",
    "ООО «Логическая навигация». Электронные устройства управления, полётные контроллеры и системы мониторинга.",
    "/",
)
home += header(("home", True))
home += ("""<main id="main">

<section class="hero on-dark">
<div class="container">
<div class="hero-copy">
<h1>Разработка электроники для управления и навигации</h1>
<p class="lead">ЛоджикНав – российская инженерная компания. Мы разрабатываем электронные устройства, полётные контроллеры и системы мониторинга для решения специализированных задач.</p>
<p class="tagline">Собственные разработки. Инженерный подход. Российская компонентная база.</p>
<div class="btn-row">
<a class="btn" href="/products/">Продукция</a>
<a class="btn btn--ghost" href="/contacts/#request">Связаться с нами</a>
</div>
</div>
<div class="hero-figure">
<figure class="plate">
{hero_pic}
<figcaption>Сборка LN1YA с платой управления питанием и инерциальной системой</figcaption>
</figure>
</div>
</div>
</section>

<section class="section section--tint" aria-labelledby="directions">
<div class="container">
""" + section_head("Направления работы", "Три связанных направления: от управляющей электроники до систем наблюдения за протяжёнными объектами.", "directions") + """
<div class="cards cards--3">
<article class="card card--direction">
""" + badge("chip") + """
<h3>Полётные контроллеры</h3>
<p>Электронные устройства управления для беспилотных платформ. Разработка, адаптация и интеграция решений.</p>
""" + check_list(["Электронные модули управления", "Адаптация под задачи платформы", "Интеграция в состав систем"]) + """
<a class="card-link" href="/products/">Раздел «Продукция»</a>
</article>
<article class="card card--direction">
""" + badge("compass") + """
<h3>Навигационная электроника</h3>
<p>Инженерные решения для работы с навигационными данными и взаимодействия электронных модулей.</p>
""" + check_list(["Работа с навигационными данными", "Взаимодействие электронных модулей", "Развитие навигационных решений"]) + """
<a class="card-link" href="/products/ln14ya/">Контроллер LN14YA</a>
</article>
<article class="card card--direction">
""" + badge("activity") + """
<h3>Системы мониторинга</h3>
<p>Аппаратно-программные комплексы для регистрации и анализа событий на распределённых объектах.</p>
""" + check_list(["Регистрация и анализ событий", "Протяжённые и распределённые объекты", "Аппаратная и программная части"]) + """
<a class="card-link" href="/projects/">Раздел «Разработки»</a>
</article>
</div>
</div>
</section>

<section class="section" aria-labelledby="products">
<div class="container">
""" + section_head("Продукция и разработки", "Изделия и технологические проекты ЛоджикНав. Подробные сведения предоставляем по запросу.", "products") + """

<article class="feature">
<div class="feature-media">
<div class="feature-photos">
{feat_a}
{feat_b}
</div>
<p class="feature-hint">Нажмите на фотографию, чтобы увеличить</p>
</div>
<div class="feature-body">
<h3>LN1YA</h3>
<p class="feature-sub">LN1YA – полётный контроллер на российской элементной базе.</p>
<p>Сверхлёгкий электронный модуль управления для интеграции в беспилотные платформы и применения в составе специализированных комплексов. Работает с привычным программным обеспечением Betaflight и iNav. Для разных задач предусмотрены варианты комплектации.</p>
""" + chips(["Полётный контроллер", "С платой управления питанием", "С инерциальной системой"]) + """
<div class="btn-row">
<a class="btn" href="/products/ln1ya/">Подробнее</a>
<a class="btn btn--outline" href="{ln1ya_cta}">Запросить информацию</a>
</div>
</div>
</article>

<div class="cards cards--2 cards--gap-top">
<article class="card card--product">
""" + neutral_media("LN14YA") + """
<div class="card-inner">
<div class="card-body">
<h3>LN14YA</h3>
<p>LN14YA – полётный контроллер нового поколения для скоростных реактивных БПЛА. Российский процессор и резервированный состав датчиков.</p>
</div>
<a class="btn btn--outline" href="/products/ln14ya/">О проекте</a>
</div>
</article>
<article class="card card--product">
""" + neutral_media("«Тетива-М»") + """
<div class="card-inner">
<div class="card-body">
<h3>«Тетива-М»</h3>
<p>«Тетива-М» – распределённая акустическая система на основе оптоволокна. Круглосуточное наблюдение за протяжёнными объектами: земля, вода, воздух.</p>
</div>
<a class="btn btn--outline" href="/projects/tetiva-m/">О разработке</a>
</div>
</article>
</div>
</div>
</section>

<section class="section section--tint" aria-labelledby="areas">
<div class="container">
""" + section_head("Где применяются наши решения", "Конкретная конфигурация всегда определяется задачей и условиями применения.", "areas") + tiles([
    ("plane", "Беспилотные платформы", "Электронные устройства управления для FPV-решений самолётного и роторного типа и других беспилотных платформ."),
    ("layers", "Специализированные комплексы", "Применение полётных контроллеров в составе комплексов по согласованным требованиям."),
    ("grid", "Навигационные данные", "Решения для работы с навигационными данными и взаимодействия электронных модулей."),
    ("route", "Протяжённая инфраструктура", "Непрерывное наблюдение за событиями вдоль протяжённых участков и объектов."),
    ("shield", "Охрана периметров", "Мониторинг периметров и выявление акустических воздействий."),
    ("eye", "Трубопроводы и водоёмы", "Мониторинг трубопроводов и водных объектов, регистрация и анализ событий."),
]) + """
</div>
</section>

<section class="section on-dark" aria-labelledby="process">
<div class="container">
""" + section_head("От идеи до инженерного решения", "Работа над изделием включает анализ требований, разработку концепции, создание опытных образцов, испытания и доработку конструкции. Решения формируются с учётом задач и условий применения.", "process") + steps([
    ("Анализ требований", "Разбираем задачу, условия применения и ограничения, фиксируем требования к изделию."),
    ("Разработка концепции", "Определяем инженерный подход и состав решения под зафиксированные требования."),
    ("Опытные образцы", "Создаём опытные образцы, на которых проверяются принятые решения."),
    ("Испытания", "Проверяем изделие на соответствие требованиям задачи."),
    ("Доработка конструкции", "Учитываем результаты проверок и дорабатываем конструкцию."),
]) + """
</div>
</section>

<section class="section" aria-labelledby="principles">
<div class="container">
""" + section_head("Принципы работы", None, "principles") + principles() + """
</div>
</section>

<section class="section section--tint" aria-labelledby="cooperation">
<div class="container">
""" + section_head("Сотрудничество", "Рассматриваем запросы на поставку электронных изделий, их интеграцию и проработку новых технических решений. Для обсуждения проекта направьте описание задачи через форму обратной связи.", "cooperation") + """
<div class="cards cards--3">
<article class="card">
""" + badge("package") + """
<h3>Поставка электронных изделий</h3>
<p>Рассматриваем запросы на поставку изделий. Состав и условия уточняются по запросу.</p>
</article>
<article class="card">
""" + badge("link") + """
<h3>Интеграция</h3>
<p>Обсуждаем встраивание электронных модулей в платформы и комплексы заказчика.</p>
</article>
<article class="card">
""" + badge("bulb") + """
<h3>Новые технические решения</h3>
<p>Прорабатываем решения под задачу, которой нет в готовом каталоге.</p>
</article>
</div>

<div class="request-flow">
<h3>Как направить запрос</h3>
""" + steps([
    ("Опишите задачу", "Заполните форму на странице «Контакты»: кратко опишите, что нужно сделать."),
    ("Проверьте письмо", "Откроется почтовое приложение с готовым письмом. Проверьте его и отправьте сами."),
    ("Получите ответ", "Специалисты свяжутся с вами по указанным контактам."),
], light=True) + """
<a class="btn" href="/contacts/#request">Отправить запрос</a>
</div>
</div>
</section>

</main>
""").format(
    hero_pic=picture("main", "(max-width: 900px) 92vw, 560px", eager=True),
    feat_a=lb_button("front", "LN1YA, вид спереди", "(max-width: 900px) 46vw, 270px"),
    feat_b=lb_button("side", "LN1YA, вид сбоку", "(max-width: 900px) 46vw, 270px"),
    ln1ya_cta=contact_link("Запрос информации о LN1YA") + "#request",
)
org_ld = """<script type="application/ld+json">
{"@context":"https://schema.org","@type":"Organization","name":"ООО «Логическая навигация»","legalName":"Общество с ограниченной ответственностью «Логическая навигация»","alternateName":"ООО «ЛоджикНав»","identifier":"1267700240477","taxID":"7736378193","url":"%s/","logo":"%s/assets/img/logo_primary.png","email":"%s"}
</script>
""" % (SITE_URL, SITE_URL, EMAIL)
home += org_ld + footer() + scripts()
write("/", home)

# =========================================================================
# Продукция
# =========================================================================
p = head(
    "Полётные контроллеры – ООО «ЛоджикНав»",
    "Полётные контроллеры LN1YA и LN14YA нового поколения. Информация о продукции и запрос для сотрудничества.",
    "/products/",
)
p += header(("products", True))
p += '<main id="main">\n' + page_hero(
    [("/", "Главная"), ("/products/", "Продукция")],
    "Полётные контроллеры",
    "ООО «ЛоджикНав» разрабатывает электронные устройства управления для беспилотных платформ. В разделе представлены изделие LN1YA и полётный контроллер нового поколения LN14YA.",
)
p += ("""<section class="section" aria-labelledby="items">
<div class="container">
""" + section_head("Изделия", None, "items") + """
<div class="cards cards--2">
<article class="card card--product">
<div class="card-media">{pic}</div>
<div class="card-inner">
<div class="card-body">
<h3>LN1YA</h3>
<p>Полётный контроллер на российской элементной базе. Возможны различные варианты комплектации.</p>
<p>Сверхлёгкий электронный модуль управления для интеграции в беспилотные платформы. Совместим с Betaflight и iNav.</p>
</div>
<a class="btn btn--outline" href="/products/ln1ya/">Подробнее</a>
</div>
</article>
<article class="card card--product">
""" + neutral_media("LN14YA") + """
<div class="card-inner">
<div class="card-body">
<h3>LN14YA</h3>
<p>Полётный контроллер нового поколения с расширенными возможностями интеграции.</p>
<p>Для скоростных реактивных БПЛА: российский процессор, резервированный состав датчиков, поддержка ArduPilot.</p>
</div>
<a class="btn btn--outline" href="/products/ln14ya/">Подробнее</a>
</div>
</article>
</div>
</div>
</section>

<section class="section section--tint" aria-labelledby="common">
<div class="container">
""" + section_head("Что объединяет изделия", "Общий подход ЛоджикНав к полётным контроллерам.", "common") + tiles([
    ("layers", "Интеграция в системы", "Контроллеры предназначены для встраивания в беспилотные платформы и специализированные комплексы."),
    ("chip", "Российская компонентная база", "Ориентируемся на российскую элементную базу при разработке изделий."),
    ("package", "Варианты комплектации", "Состав поставки подбирается под задачу. Актуальный состав и доступность уточняются по запросу."),
]) + """
</div>
</section>

<section class="section" aria-labelledby="info">
<div class="container">
""" + section_head("Подробные сведения – по запросу", None, "info") + """
<div class="spec-row">
<h3>Как мы работаем с запросами</h3>
<div>
<p>Характеристики, требования к подключению, программная совместимость и документацию мы не публикуем в открытом доступе: они обсуждаются со специалистами применительно к конкретному проекту. Опишите задачу, и мы подскажем, какое решение подойдёт.</p>
<div class="btn-row">
<a class="btn" href="/contacts/#request">Отправить запрос</a>
</div>
</div>
</div>
</div>
</section>
</main>
""").format(pic=picture("main", "(max-width: 760px) 92vw, 580px", eager=True))
p += footer() + scripts()
write("/products/", p)

# =========================================================================
# LN1YA
# =========================================================================
cap1 = "Фото 1. Сборка LN1YA с платой управления питанием и инерциальной системой. Основной кадр."
cap2 = "Фото 2. Спереди"
cap3 = "Фото 3. Сбоку"
cap4 = "Плата LN1YA. Изображение"

l1 = head(
    "LN1YA – полётный контроллер – ЛоджикНав",
    "Сверхлёгкий полётный контроллер LN1YA на российской элементной базе. Совместимость с Betaflight и iNav, варианты комплектации и запрос информации.",
    "/products/ln1ya/",
)
l1 += header(("products", False))
l1 += '<main id="main">\n' + page_hero(
    [("/", "Главная"), ("/products/", "Продукция"), ("/products/ln1ya/", "LN1YA")],
    "LN1YA – полётный контроллер",
    "LN1YA – электронный модуль управления на российской элементной базе. Контроллер предназначен для интеграции в беспилотные платформы и применения в составе специализированных комплексов.",
    side='<div class="hero-figure"><figure class="plate">%s<figcaption>Сборка LN1YA с платой управления питанием и инерциальной системой</figcaption></figure></div>' % picture("main", "(max-width: 900px) 92vw, 520px", eager=True),
    buttons='<a class="btn" href="%s">Запросить информацию о LN1YA</a><a class="btn btn--ghost" href="/products/">Вся продукция</a>' % (contact_link("Запрос информации о LN1YA") + "#request"),
)
l1 += (
    '<section class="section" aria-labelledby="one-board">\n<div class="container">\n<div class="split">\n<div>\n'
    '<h2 id="one-board">Всё необходимое на одной плате</h2>\n'
    '<p>LN1YA – сверхлёгкий полётный контроллер на российской элементной базе. Основные датчики расположены на борту платы, поэтому внешние модули для их работы не требуются.</p>\n'
    + check_list([
        "Формат All-in-One: компактная плата с основными датчиками на борту",
        "Двухъядерный российский процессор",
        "Слот microSD для журналов полёта (Blackbox)",
        "Совместимость с Betaflight и iNav",
    ])
    + '\n</div>\n' + board_figure(cap4) + '\n</div>\n</div>\n</section>\n\n'

    '<section class="section section--tint" aria-labelledby="composition">\n<div class="container">\n'
    + section_head("Состав сборки на фотографиях", "Сборка включает полётный контроллер, плату управления питанием и инерциальную систему.", "composition")
    + '\n<div class="cards cards--3">\n'
    '<article class="card">' + badge("chip") + '<h3>Полётный контроллер</h3><p>Основной электронный модуль управления для беспилотных платформ.</p></article>\n'
    '<article class="card">' + badge("layers") + '<h3>Плата управления питанием</h3><p>Дополнительный модуль, который входит в сборку на фотографиях и в соответствующую комплектацию.</p></article>\n'
    '<article class="card">' + badge("compass") + '<h3>Инерциальная система</h3><p>Дополнительная система для исполнений, в которых она предусмотрена.</p></article>\n'
    '</div>\n</div>\n</section>\n\n'

    '<section class="section" aria-labelledby="variants">\n<div class="container">\n'
    + section_head("Варианты комплектации", "В зависимости от задачи предусмотрены варианты поставки полётного контроллера, контроллера с платой управления питанием, а также исполнения с дополнительной инерциальной системой.", "variants")
    + '\n' + variant_cards([
        ("Полётный контроллер", "ТМПГ.466229.001", "Для замены зарубежного контроллера в существующих FPV-решениях."),
        ("Контроллер с платой управления питанием", "ТМПГ.466229.001-01", "Для создания лёгких FPV-аппаратов."),
        ("Исполнение с инерциальной системой", "ТМПГ.466229.001-02", "Для решения задач навигации в сложных условиях, например над морем."),
    ])
    + '\n<p class="section-note">Актуальный состав и доступность комплектаций уточняются по запросу.</p>\n</div>\n</section>\n\n'

    '<section class="section section--tint" aria-labelledby="photos">\n<div class="container">\n'
    + section_head("Фотографии изделия", "На фотографиях представлена сборка полётного контроллера, платы управления питанием и инерциальной системы. Три снимка показывают одну сборку с разных ракурсов. Нажмите на снимок, чтобы открыть его в полном размере.", "photos")
    + '\n<div class="gallery-grid gallery-grid--3">\n'
    '<figure class="photo">' + lb_button("main", cap1, "(max-width: 760px) 92vw, 380px") + '<figcaption>' + cap1 + '</figcaption></figure>\n'
    '<figure class="photo">' + lb_button("front", cap2, "(max-width: 760px) 92vw, 380px") + '<figcaption>' + cap2 + '</figcaption></figure>\n'
    '<figure class="photo">' + lb_button("side", cap3, "(max-width: 760px) 92vw, 380px") + '<figcaption>' + cap3 + '</figcaption></figure>\n'
    '</div>\n</div>\n</section>\n\n'

    '<section class="section" aria-labelledby="software">\n<div class="container">\n<div class="split split--text">\n<div>\n'
    '<h2 id="software">Привычное программное обеспечение</h2>\n'
    '<p>LN1YA работает с конфигураторами Betaflight и iNav: инженер настраивает контроллер в знакомой среде и записывает журналы полёта на microSD.</p>\n'
    '</div>\n<div>\n<p class="list-title">В конфигураторе доступны:</p>\n'
    + check_list([
        "прошивка и обновление",
        "настройка портов",
        "выбор типа аппарата (квадрокоптер, самолёт), датчиков и режимов",
        "PID-тюнинг",
        "настройка OSD",
        "клиент командной строки (CLI)",
    ])
    + '\n</div>\n</div>\n</div>\n</section>\n\n'

    '<section class="section section--tint" aria-labelledby="flow">\n<div class="container">\n'
    + section_head("От задачи до применения", "Как LN1YA встраивается в проект заказчика.", "flow")
    + steps([
        ("Техническое задание", "Определяются требования к аппарату: назначение, масса, состав датчиков."),
        ("Выбор контроллера", "Подбирается комплектация LN1YA под требования задачи."),
        ("Настройка", "Работа в привычном Betaflight или iNav, журналы полёта пишутся на microSD."),
        ("Применение", "Российская элементная база снижает зависимость от импортной электроники в критичном узле."),
    ], light=True)
    + '\n</div>\n</section>\n\n'

    '<section class="section" aria-labelledby="integration">\n<div class="container">\n<div class="spec-row">\n'
    '<h2 id="integration">Интеграция и техническая информация</h2>\n<div>\n'
    '<p>Возможности применения контроллера, требования к подключению, программная совместимость и комплект документации обсуждаются со специалистами компании применительно к конкретному проекту.</p>\n'
    '<p>В запросе можно уточнить:</p>\n'
    + check_list(["возможности применения в вашей платформе", "требования к подключению", "программную совместимость", "комплект документации", "актуальный состав и доступность комплектаций"])
    + '\n<div class="btn-row">\n<a class="btn" href="' + contact_link("Запрос информации о LN1YA") + '#request">Запросить информацию о LN1YA</a>\n</div>\n'
    '</div>\n</div>\n</div>\n</section>\n</main>\n'
)
l1 += footer() + scripts()
write("/products/ln1ya/", l1)

# =========================================================================
# LN14YA
# =========================================================================
l14 = head(
    "LN14YA – полётный контроллер нового поколения – ЛоджикНав",
    "Полётный контроллер LN14YA нового поколения для скоростных реактивных БПЛА: российский процессор, резервированный состав датчиков, поддержка ArduPilot.",
    "/products/ln14ya/",
)
l14 += header(("products", False))
l14 += '<main id="main">\n' + page_hero(
    [("/", "Главная"), ("/products/", "Продукция"), ("/products/ln14ya/", "LN14YA")],
    "LN14YA – полётный контроллер нового поколения",
    "LN14YA – электронное устройство управления для беспилотных платформ, ориентированное на скоростные реактивные БПЛА. Предусматривает развитие вычислительных и навигационных функций, резервированный состав датчиков и возможности интеграции в состав различных систем.",
    side=info_card("Коротко", ["Для скоростных реактивных БПЛА", "Вычислитель на российском процессоре", "Резервированный состав датчиков", "Совместимость с ArduPilot"]),
    buttons='<a class="btn" href="%s">Запросить информацию о LN14YA</a><a class="btn btn--ghost" href="/products/">Вся продукция</a>' % (contact_link("Запрос информации о LN14YA") + "#request"),
)
l14 += (
    '<section class="section" aria-labelledby="features">\n<div class="container">\n'
    + section_head("Особенности", "Основные свойства устройства.", "features")
    + tiles([
        ("plane", "Скоростные реактивные БПЛА", "Устройство ориентировано на скоростные беспилотные аппараты реактивного типа."),
        ("chip", "Российский процессор", "Вычислитель построен на российском процессоре."),
        ("layers", "Резервированный состав датчиков", "Ключевые измерения дублируются, чтобы устройство сохраняло работоспособность."),
        ("link", "Поддержка ArduPilot", "Работа с распространённым программным обеспечением для автопилотов."),
    ], "tiles--2")
    + '\n</div>\n</section>\n\n'

    '<section class="section section--tint" aria-labelledby="redundancy">\n<div class="container">\n'
    + section_head("Резервирование", "Что дублируется в составе устройства.", "redundancy")
    + tiles([
        ("compass", "Инерциальные датчики", "Предусмотрено резервирование инерциальных датчиков от разных производителей."),
        ("route", "Данные о высоте", "Предусмотрено дублирование измерения высоты."),
        ("activity", "Контроль питания", "Предусмотрено двухканальное измерение параметров питания."),
    ])
    + '\n</div>\n</section>\n\n'

    '<section class="section" aria-labelledby="usage">\n<div class="container">\n<div class="spec-row">\n'
    '<h2 id="usage">Состав функций и применение</h2>\n<div>\n'
    '<p>LN14YA входит в линейку полётных контроллеров ЛоджикНав и предназначен для беспилотных платформ. Состав функций, интерфейсы и характеристики уточняются; актуальные сведения специалисты предоставляют по запросу применительно к задачам вашего проекта.</p>\n'
    '</div>\n</div>\n<div class="spec-row">\n<h2>Сотрудничество</h2>\n<div>\n'
    '<p>Для получения актуальной информации о проекте и возможности применения LN14YA направьте запрос специалистам компании.</p>\n'
    '<div class="btn-row">\n<a class="btn" href="' + contact_link("Запрос информации о LN14YA") + '#request">Запросить информацию о LN14YA</a>\n</div>\n'
    '</div>\n</div>\n</div>\n</section>\n</main>\n'
)
l14 += footer() + scripts()
write("/products/ln14ya/", l14)

# =========================================================================
# Разработки
# =========================================================================
pr = head(
    "Технологические разработки – ООО «ЛоджикНав»",
    "Инженерные проекты ООО «ЛоджикНав» в области электроники, навигации и систем мониторинга. Распределённая акустическая система «Тетива-М».",
    "/projects/",
)
pr += header(("projects", True))
pr += '<main id="main">\n' + page_hero(
    [("/", "Главная"), ("/projects/", "Разработки")],
    "Технологические разработки",
    "ЛоджикНав развивает инженерные проекты в области электроники, навигации и систем мониторинга. В разделе представлены наши разработки и сведения об их назначении.",
)
pr += """<section class="section" aria-labelledby="projects-list">
<div class="container">
""" + section_head("Разработки", None, "projects-list") + """
<article class="feature feature--neutral">
""" + neutral_media("«Тетива-М»", "Распределённая акустическая система") + """
<div class="feature-body">
<h3>«Тетива-М»</h3>
<p class="feature-sub">«Тетива-М» – распределённая акустическая система на основе оптоволокна.</p>
<p>Система распределённого акустического мониторинга для круглосуточного наблюдения за событиями вдоль протяжённых объектов и инфраструктуры, обнаружения и классификации объектов.</p>
""" + chips(["Охрана периметров", "Трубопроводы и инфраструктура", "Водоёмы"]) + """
<div class="btn-row">
<a class="btn" href="/projects/tetiva-m/">Подробнее</a>
</div>
</div>
</article>
</div>
</section>

<section class="section section--tint" aria-labelledby="approach">
<div class="container">
""" + section_head("Как мы подходим к разработкам", "Одна последовательность для изделий и для технологических проектов.", "approach") + steps([
    ("Анализ требований", "Фиксируем задачу и условия применения."),
    ("Концепция", "Определяем состав решения под задачу."),
    ("Опытные образцы", "Проверяем принятые решения на практике."),
    ("Испытания", "Оцениваем соответствие требованиям."),
    ("Доработка", "Учитываем результаты и дорабатываем решение."),
], light=True) + """
</div>
</section>
</main>
"""
pr += cta_band("Нужна разработка под вашу задачу?", "Опишите задачу: обсудим, какое решение можно проработать, и сформулируем следующие шаги.")
pr += footer() + scripts()
write("/projects/", pr)

# =========================================================================
# Тетива-М
# =========================================================================
t = head(
    "Тетива-М – распределённая акустическая система – ЛоджикНав",
    "Распределённая акустическая система «Тетива-М» на основе оптоволокна: круглосуточное наблюдение за протяжёнными объектами, охрана периметров, мониторинг трубопроводов и водоёмов.",
    "/projects/tetiva-m/",
)
t += header(("projects", False))
t += '<main id="main">\n' + page_hero(
    [("/", "Главная"), ("/projects/", "Разработки"), ("/projects/tetiva-m/", "«Тетива-М»")],
    "«Тетива-М» – распределённая акустическая система",
    "«Тетива-М» – система распределённого акустического мониторинга на основе оптоволоконной технологии. Решение ориентировано на круглосуточное наблюдение за событиями вдоль протяжённых объектов и инфраструктуры.",
    side=info_card("Коротко", ["Круглосуточное наблюдение", "Земля, вода, воздух", "Работа в реальном времени", "Кабель не требует питания"]),
    buttons='<a class="btn" href="%s">Запросить информацию о «Тетиве-М»</a><a class="btn btn--ghost" href="/projects/">Все разработки</a>' % (contact_link("Запрос информации о «Тетиве-М»") + "#request"),
)
t += (
    '<section class="section" aria-labelledby="purpose">\n<div class="container">\n<div class="spec-row">\n'
    '<h2 id="purpose">Назначение</h2>\n<div>\n'
    '<p>Система предназначена для организации непрерывного мониторинга и выявления акустических воздействий на протяжённых участках, а также для обнаружения и классификации воздушных, наземных, надводных и подводных объектов. Возможность применения рассматривается с учётом требований конкретного объекта.</p>\n'
    '</div>\n</div>\n<div class="spec-row">\n<h2>Принцип работы</h2>\n<div>\n'
    '<p>Обычное оптоволокно используется как непрерывная линейка датчиков: вибрации и акустические воздействия регистрируются вдоль всей длины кабеля, а не в отдельных точках.</p>\n'
    '</div>\n</div>\n</div>\n</section>\n\n'

    '<section class="section section--tint" aria-labelledby="capabilities">\n<div class="container">\n'
    + section_head("Ключевые возможности", None, "capabilities")
    + tiles([
        ("grid", "Тысячи точек измерения", "На одном волокне наблюдение ведётся сразу во множестве точек."),
        ("activity", "Реальное время", "События регистрируются и анализируются в реальном времени."),
        ("package", "Пассивная инфраструктура", "Кабель вдоль наблюдаемого участка не требует питания."),
    ])
    + '\n</div>\n</section>\n\n'

    '<section class="section" aria-labelledby="areas">\n<div class="container">\n'
    + section_head("Области применения", "Мониторинг протяжённой инфраструктуры, охрана периметров и наблюдение за состоянием объектов. Конфигурация системы и условия внедрения определяются для каждого проекта отдельно.", "areas")
    + tiles([
        ("shield", "Охрана периметра", "Локализация нарушителя вдоль периметра без мёртвых зон."),
        ("plane", "Обнаружение БПЛА", "Определение направления и типа объекта по акустической сигнатуре."),
        ("route", "Мониторинг трубопроводов", "Утечки, несанкционированные врезки, земляные работы, сейсмическая активность."),
        ("eye", "Мониторинг водоёмов", "Обнаружение судов и пловцов, обновление их положения."),
    ], "tiles--2")
    + '\n</div>\n</section>\n\n'

    '<section class="section section--tint" aria-labelledby="project-flow">\n<div class="container">\n'
    + section_head("Как строится проект", "Применение системы всегда рассматривается под конкретный объект.", "project-flow")
    + steps([
        ("Описание объекта", "Вы рассказываете об объекте и задачах наблюдения."),
        ("Оценка применимости", "Специалисты рассматривают возможность применения с учётом требований объекта."),
        ("Согласование конфигурации", "Конфигурация и условия внедрения определяются для проекта отдельно."),
    ], light=True)
    + '\n</div>\n</section>\n\n'

    '<section class="section" aria-labelledby="more">\n<div class="container">\n<div class="spec-row">\n'
    '<h2 id="more">Дополнительная информация</h2>\n<div>\n'
    '<p>Для обсуждения применения системы «Тетива-М» и получения подробных материалов свяжитесь с представителями ООО «ЛоджикНав».</p>\n'
    '<div class="btn-row">\n<a class="btn" href="' + contact_link("Запрос информации о «Тетиве-М»") + '#request">Запросить информацию о «Тетиве-М»</a>\n</div>\n'
    '</div>\n</div>\n</div>\n</section>\n</main>\n'
)
t += footer() + scripts()
write("/projects/tetiva-m/", t)

# =========================================================================
# О компании
# =========================================================================
a = head(
    "О компании – ООО «Логическая навигация»",
    "Российская инженерная компания. Разработка электроники, навигационных решений и систем мониторинга.",
    "/about/",
)
a += header(("about", True))
a += '<main id="main">\n' + page_hero(
    [("/", "Главная"), ("/about/", "О компании")],
    "О компании",
    "ООО «Логическая навигация» (ООО «ЛоджикНав») – российская инженерная компания, работающая в области разработки электронной аппаратуры, систем управления, навигации и мониторинга.",
    side='<figure class="plate about-logo"><img src="/assets/img/logo_extended.png" width="1384" height="948" alt="ЛоджикНав — Логическая навигация" loading="lazy"></figure>',
)
a += ("""<section class="section" aria-labelledby="activities">
<div class="container">
""" + section_head("Направления деятельности", "Разрабатываем электронные устройства и системы для специализированных задач.", "activities") + """
<div class="cards cards--3">
<article class="card">
""" + badge("chip") + """
<h3>Полётные контроллеры</h3>
<p>Разработка полётных контроллеров и электронных модулей для беспилотных платформ.</p>
</article>
<article class="card">
""" + badge("compass") + """
<h3>Навигационные решения</h3>
<p>Создание и развитие навигационных решений и электроники для работы с навигационными данными.</p>
</article>
<article class="card">
""" + badge("activity") + """
<h3>Системы мониторинга</h3>
<p>Разработка аппаратно-программных систем мониторинга для распределённых и протяжённых объектов.</p>
</article>
</div>
</div>
</section>

<section class="section section--tint" aria-labelledby="approach">
<div class="container">
<div class="split">
<div>
<h2 id="approach">Инженерный подход</h2>
<p>В работе над проектами мы последовательно рассматриваем задачу заказчика, прорабатываем требования к изделию, создаём опытные решения и выполняем их проверку.</p>
<p>Такой порядок помогает принимать решения по существу задачи: что нужно заказчику, в каких условиях будет работать изделие и как проверить результат.</p>
""" + check_list(["Рассматриваем задачу заказчика", "Прорабатываем требования к изделию", "Создаём опытные решения", "Выполняем их проверку"]) + """
</div>
<figure class="plate about-photo">
{photo}
<figcaption>Сборка полётного контроллера LN1YA, вид сбоку</figcaption>
</figure>
</div>
</div>
</section>

<section class="section" aria-labelledby="principles">
<div class="container">
""" + section_head("Принципы работы", None, "principles") + principles() + """
</div>
</section>

<section class="section section--tint" aria-labelledby="company">
<div class="container">
<div class="spec-row">
<h2 id="company">Сведения об организации</h2>
<div>
<dl class="company-details">
<dt>Полное наименование</dt><dd>{full}</dd>
<dt>Сокращённое наименование</dt><dd>{short}</dd>
<dt>Основной вид деятельности (ОКВЭД {okved})</dt><dd>{okved_description}</dd>
</dl>
</div>
</div>
</div>
</section>
</main>
""").format(
    photo=picture("side", "(max-width: 900px) 92vw, 520px"),
    full=FULL_LEGAL_NAME, short=SHORT_NAME, okved=OKVED, okved_description=OKVED_DESCRIPTION,
)
a += cta_band("Открыты к обсуждению технических задач", "Обсудим интеграцию электронных модулей и перспективные совместные разработки.", label="Связаться с нами")
a += footer() + scripts()
write("/about/", a)

# =========================================================================
# Контакты
# =========================================================================
c = head(
    "Контакты – ООО «ЛоджикНав»",
    "Контактная информация и форма обращения по вопросам продукции, разработок и сотрудничества.",
    "/contacts/",
)
c += header(("contacts", True))
c += '<main id="main">\n' + page_hero(
    [("/", "Главная"), ("/contacts/", "Контакты")],
    "Контакты",
    "По вопросам продукции, разработок и сотрудничества подготовьте письмо через форму или напишите на нашу электронную почту.",
)
c += ("""<section class="section">
<div class="container contact-grid">

<div class="contact-side">
<h2 class="visually-hidden">Реквизиты</h2>
<div class="mail-card">
""" + badge("mail") + """
<p class="mail-card-label">Электронная почта</p>
<p class="mail-card-value"><a href="mailto:{email}">{email}</a></p>
</div>
<dl class="requisites">
<dt>Полное наименование</dt>
<dd>{full}</dd>
<dt>Сокращённое наименование</dt>
<dd>{short}</dd>
<dt>ОГРН</dt>
<dd>{ogrn}</dd>
<dt>ИНН / КПП</dt>
<dd>{inn} / {kpp}</dd>
</dl>
</div>

<div class="form-card" id="request">
<h2>Направить запрос</h2>
<p class="form-hint">Заполните поля. После нажатия кнопки откроется почтовое приложение с подготовленным письмом. Письмо отправляется вами самостоятельно.</p>
<p class="form-hint form-hint--tips">В сообщении полезно указать: что нужно сделать, для какой платформы или объекта, в какие сроки нужен ответ.</p>

<form id="contact-form" action="mailto:{email}" method="post" enctype="text/plain">
<div class="form-grid">

<div class="field">
<label for="f-name">Имя<span class="req" aria-hidden="true">*</span></label>
<input type="text" id="f-name" name="name" autocomplete="name" required aria-required="true" maxlength="120">
<span class="error-msg" role="alert"></span>
</div>

<div class="field">
<label for="f-org">Организация</label>
<input type="text" id="f-org" name="organization" autocomplete="organization" maxlength="200">
<span class="error-msg" role="alert"></span>
</div>

<div class="field">
<label for="f-email">Электронная почта<span class="req" aria-hidden="true">*</span></label>
<input type="email" id="f-email" name="email" autocomplete="email" required aria-required="true" maxlength="200">
<span class="error-msg" role="alert"></span>
</div>

<div class="field">
<label for="f-phone">Телефон</label>
<input type="tel" id="f-phone" name="phone" autocomplete="tel" maxlength="40">
<span class="error-msg" role="alert"></span>
</div>

<div class="field field--full">
<label for="f-subject">Тема обращения<span class="req" aria-hidden="true">*</span></label>
<input type="text" id="f-subject" name="subject" required aria-required="true" maxlength="150">
<span class="error-msg" role="alert"></span>
</div>

<div class="field field--full">
<label for="f-message">Сообщение<span class="req" aria-hidden="true">*</span></label>
<textarea id="f-message" name="message" required aria-required="true" maxlength="5000"></textarea>
<span class="error-msg" role="alert"></span>
</div>

<div class="field field--full">
<p class="note">Документы и фотографии можно приложить к письму в почтовой программе после её открытия. Сайт не загружает файлы.</p>
</div>

<div class="field field--full">
<div class="consent">
<input type="checkbox" id="f-consent" name="consent" value="1" required aria-required="true">
<label for="f-consent">Я согласен(на) на использование указанных контактных данных для ответа на обращение.</label>
</div>
<span class="error-msg" role="alert"></span>
</div>

<div class="field field--full">
<div><button class="btn" type="submit">Открыть письмо</button></div>
</div>

</div>
<div id="form-status" class="form-status" role="status" aria-live="polite"></div>
<div id="mail-actions" class="mail-actions" hidden>
<a class="btn btn--outline btn--sm" id="mail-fallback" href="mailto:{email}">Открыть письмо вручную</a>
<button class="btn btn--outline btn--sm" type="button" id="mail-copy">Скопировать текст обращения</button>
</div>
</form>
</div>

</div>
</section>
</main>
""").format(
    email=EMAIL,
    full=FULL_LEGAL_NAME,
    short=SHORT_NAME,
    ogrn=OGRN,
    inn=INN,
    kpp=KPP,
)
c += footer() + scripts()
write("/contacts/", c)

# =========================================================================
# 404
# =========================================================================
e = head("Страница не найдена – ООО «ЛоджикНав»", "Запрошенная страница не найдена.", "/404.html", noindex=True)
e += header(("", False))
e += """<main id="main" class="error-page">
<div class="container">
<p class="code">404</p>
<h1>Страница не найдена</h1>
<p>Возможно, адрес изменился или введён с ошибкой. Перейдите на главную или выберите нужный раздел в меню.</p>
<a class="btn" href="/">На главную</a>
</div>
</main>
"""
e += footer() + scripts()
write("404", e)

# =========================================================================
# sitemap / robots
# =========================================================================
urls = ["/", "/products/", "/products/ln1ya/", "/products/ln14ya/", "/projects/", "/projects/tetiva-m/", "/about/", "/contacts/"]
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for u in urls:
    sm += "  <url><loc>%s%s</loc></url>\n" % (SITE_URL, u)
sm += "</urlset>\n"
with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as f:
    f.write(sm)
with open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8") as f:
    f.write("User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE_URL)

print("OK: сайт собран в site/ (SITE_URL=%s, форма: mailto:%s)" % (SITE_URL, EMAIL))
