#!/usr/bin/env python3
"""Генератор страниц сайта ООО «ЛоджикНав».

Запуск из корня репозитория:  python3 tools/build.py
Результат записывается в папку site/. Тексты и метаданные находятся в этом файле.

Настройки берутся из переменных окружения (в GitHub Actions их задаёт workflow):
  SITE_URL           публичный адрес сайта, например https://user.github.io/repo
                     или https://ваш-домен.ru (если есть путь — ссылки подстроятся сами)
  Контактная форма работает через mailto: подготовленное письмо открывается
  в почтовом приложении посетителя. На сервер сайта ничего не отправляется.
"""
import os
import re
from html import escape
from urllib.parse import urlparse

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
REGISTERED = "17.07.2026"
DIRECTOR = "Мятин Алексей Александрович"
LEGAL_ADDRESS = "119296, г. Москва, муниципальный округ Гагаринский, Ломоносовский проспект, д. 4, к. 2, помещ. 1А/П"
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


def page_hero(crumbs, h1, lead, tag=None, extra=""):
    bc = []
    for i, (href, label) in enumerate(crumbs):
        if i == len(crumbs) - 1:
            bc.append('<li><span aria-current="page">%s</span></li>' % label)
        else:
            bc.append('<li><a href="%s">%s</a></li>' % (href, label))
    tag_html = '<span class="tag">%s</span>\n' % tag if tag else ""
    return """<section class="page-hero on-dark">
<div class="container">
<nav aria-label="Навигационная цепочка"><ol class="breadcrumbs">{bc}</ol></nav>
{tag}<h1>{h1}</h1>
<p class="lead">{lead}</p>
{extra}</div>
</section>
""".format(bc="".join(bc), tag=tag_html, h1=h1, lead=lead, extra=extra)


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


def contact_link(topic):
    from urllib.parse import quote
    return "/contacts/?topic=" + quote(topic)


pages = {}

# ============================ Главная ===============================
home = head(
    "ЛоджикНав – разработка электроники и навигационных решений",
    "ООО «Логическая навигация». Электронные устройства управления, полётные контроллеры и системы мониторинга.",
    "/",
)
home += header(("home", True))
home += """<main id="main">

<section class="hero on-dark">
<div class="container">
<div class="hero-copy">
<h1>Разработка электроники для управления и навигации</h1>
<p class="lead">ЛоджикНав – российская инженерная компания. Мы разрабатываем электронные устройства, полётные контроллеры и системы мониторинга для решения специализированных задач.</p>
<p class="tagline">Собственные разработки. Инженерный подход. Российская компонентная база.</p>
<div class="btn-row">
<a class="btn" href="/products/">Продукция</a>
<a class="btn btn--ghost" href="/contacts/">Связаться с нами</a>
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
<div class="section-head"><h2 id="directions">Направления работы</h2></div>
<div class="cards cards--3">
<article class="card card--direction">
<h3>Полётные контроллеры</h3>
<p>Электронные устройства управления для беспилотных платформ. Разработка, адаптация и интеграция решений.</p>
</article>
<article class="card card--direction">
<h3>Навигационная электроника</h3>
<p>Инженерные решения для работы с навигационными данными и взаимодействия электронных модулей.</p>
</article>
<article class="card card--direction">
<h3>Системы мониторинга</h3>
<p>Аппаратно-программные комплексы для регистрации и анализа событий на распределённых объектах.</p>
</article>
</div>
</div>
</section>

<section class="section" aria-labelledby="products">
<div class="container">
<div class="section-head"><h2 id="products">Продукция и разработки</h2></div>
<div class="cards cards--3">
<article class="card card--product">
<div class="card-media">{card_pic}</div>
<div class="card-inner">
<div class="card-body">
<h3>LN1YA</h3>
<p>LN1YA – полётный контроллер на российской элементной базе.</p>
</div>
<a class="btn btn--outline" href="/products/ln1ya/">Подробнее</a>
</div>
</article>
<article class="card">
<div class="card-meta"><span class="tag tag--light">В разработке</span></div>
<div class="card-body">
<h3>LN14YA</h3>
<p>LN14YA – полётный контроллер нового поколения.</p>
</div>
<a class="btn btn--outline" href="/products/ln14ya/">О проекте</a>
</article>
<article class="card">
<div class="card-meta"></div>
<div class="card-body">
<h3>«Тетива-М»</h3>
<p>«Тетива-М» – распределённая акустическая система на основе оптоволокна.</p>
</div>
<a class="btn btn--outline" href="/projects/tetiva-m/">О разработке</a>
</article>
</div>
</div>
</section>

<section class="section on-dark" aria-labelledby="process">
<div class="container">
<h2 id="process">От идеи до инженерного решения</h2>
<p>Работа над изделием включает анализ требований, разработку концепции, создание опытных образцов, испытания и доработку конструкции. Решения формируются с учётом задач и условий применения.</p>
<ol class="process">
<li>Анализ требований</li>
<li>Разработка концепции</li>
<li>Создание опытных образцов</li>
<li>Испытания</li>
<li>Доработка конструкции</li>
</ol>
</div>
</section>

<section class="section section--tint" aria-labelledby="cooperation">
<div class="container">
<div class="cta-block">
<div class="cta-text">
<h2 id="cooperation">Сотрудничество</h2>
<p>Рассматриваем запросы на поставку электронных изделий, их интеграцию и проработку новых технических решений. Для обсуждения проекта направьте описание задачи через форму обратной связи.</p>
</div>
<a class="btn" href="/contacts/">Отправить запрос</a>
</div>
</div>
</section>

</main>
""".format(
    hero_pic=picture("main", "(max-width: 900px) 92vw, 560px", eager=True),
    card_pic=picture("main", "(max-width: 960px) 92vw, 380px"),
)
org_ld = """<script type="application/ld+json">
{"@context":"https://schema.org","@type":"Organization","name":"ООО «Логическая навигация»","legalName":"Общество с ограниченной ответственностью «Логическая навигация»","alternateName":"ООО «ЛоджикНав»","identifier":"1267700240477","taxID":"7736378193","url":"%s/","logo":"%s/assets/img/logo_primary.png","email":"%s","address":{"@type":"PostalAddress","postalCode":"119296","addressLocality":"Москва","streetAddress":"Ломоносовский проспект, д. 4, к. 2, помещ. 1А/П","addressCountry":"RU"}}
</script>
""" % (SITE_URL, SITE_URL, EMAIL)
home += org_ld + footer() + scripts()
write("/", home)

# ============================ Продукция =============================
p = head(
    "Полётные контроллеры – ООО «ЛоджикНав»",
    "Изделие LN1YA и перспективная разработка LN14YA. Информация о продукции и запрос для сотрудничества.",
    "/products/",
)
p += header(("products", True))
p += "<main id=\"main\">\n" + page_hero(
    [("/", "Главная"), ("/products/", "Продукция")],
    "Полётные контроллеры",
    "ООО «ЛоджикНав» разрабатывает электронные устройства управления для беспилотных платформ. В разделе представлены изделие LN1YA и перспективная разработка LN14YA.",
)
p += """<section class="section" aria-labelledby="items">
<div class="container">
<h2 id="items" class="visually-hidden">Изделия</h2>
<div class="cards cards--2">
<article class="card card--product">
<div class="card-media">{pic}</div>
<div class="card-inner">
<div class="card-body">
<h3>LN1YA</h3>
<p>Полётный контроллер на российской элементной базе. Возможны различные варианты комплектации.</p>
</div>
<a class="btn btn--outline" href="/products/ln1ya/">Подробнее</a>
</div>
</article>
<article class="card">
<div class="card-meta"><span class="tag tag--light">В разработке</span></div>
<div class="card-body">
<h3>LN14YA</h3>
<p>Перспективный полётный контроллер с расширенными возможностями интеграции.</p>
</div>
<a class="btn btn--outline" href="/products/ln14ya/">Подробнее</a>
</article>
</div>
</div>
</section>
</main>
""".format(pic=picture("main", "(max-width: 760px) 92vw, 580px", eager=True))
p += footer() + scripts()
write("/products/", p)

# ============================ LN1YA =================================
cap1 = "Фото 1. Сборка LN1YA с платой управления питанием и инерциальной системой. Основной кадр."
cap2 = "Фото 2. Спереди"
cap3 = "Фото 3. Сбоку"


def lb_button(key, caption, sizes, eager=False):
    base, alt = PHOTOS[key]
    return (
        '<button type="button" data-lightbox data-full="%s%s-1280.jpg" data-alt="%s" data-caption="%s" aria-label="Открыть фото в полном размере: %s">%s</button>'
        % (IMG, base, escape(alt, quote=True), escape(caption, quote=True), escape(caption, quote=True), picture(key, sizes, eager))
    )


l1 = head(
    "LN1YA – полётный контроллер – ЛоджикНав",
    "Полётный контроллер LN1YA на российской элементной базе. Варианты комплектации и запрос информации.",
    "/products/ln1ya/",
    og_image="og-image.jpg",
)
l1 += header(("products", False))
l1 += "<main id=\"main\">\n" + page_hero(
    [("/", "Главная"), ("/products/", "Продукция"), ("/products/ln1ya/", "LN1YA")],
    "LN1YA – полётный контроллер",
    "LN1YA – электронный модуль управления на российской элементной базе. Контроллер предназначен для интеграции в беспилотные платформы и применения в составе специализированных комплексов.",
)
l1 += """<section class="section">
<div class="container">

<div class="spec-row">
<h2>Варианты комплектации</h2>
<div>
<ul class="variants">
<li>Полётный контроллер</li>
<li>Контроллер с платой управления питанием</li>
<li>Исполнение с дополнительной инерциальной системой</li>
</ul>
<p>В зависимости от задачи предусмотрены варианты поставки полётного контроллера, контроллера с платой управления питанием, а также исполнения с дополнительной инерциальной системой. Актуальный состав и доступность комплектаций уточняются по запросу.</p>
</div>
</div>

<div class="spec-row">
<h2>Фотографии изделия</h2>
<div>
<p>На фотографиях представлена сборка полётного контроллера, платы управления питанием и инерциальной системы. Три снимка показывают одну сборку с разных ракурсов.</p>
<figure class="photo photo-main">
{b1}
<figcaption>{c1}</figcaption>
</figure>
<div class="gallery-grid">
<figure class="photo">
{b2}
<figcaption>{c2}</figcaption>
</figure>
<figure class="photo">
{b3}
<figcaption>{c3}</figcaption>
</figure>
</div>
</div>
</div>

<div class="spec-row">
<h2>Интеграция и техническая информация</h2>
<div>
<p>Возможности применения контроллера, требования к подключению, программная совместимость и комплект документации обсуждаются со специалистами компании применительно к конкретному проекту.</p>
<a class="btn" href="{cta}">Запросить информацию о LN1YA</a>
</div>
</div>

</div>
</section>
</main>
""".format(
    b1=lb_button("main", cap1, "(max-width: 900px) 92vw, 830px", True),
    b2=lb_button("front", cap2, "(max-width: 640px) 92vw, 405px"),
    b3=lb_button("side", cap3, "(max-width: 640px) 92vw, 405px"),
    c1=cap1, c2=cap2, c3=cap3,
    cta=contact_link("Запрос информации о LN1YA"),
)
l1 += footer() + scripts()
write("/products/ln1ya/", l1)

# ============================ LN14YA ================================
l14 = head(
    "LN14YA – полётный контроллер в разработке – ЛоджикНав",
    "Перспективная разработка полётного контроллера LN14YA. Назначение и статус проекта.",
    "/products/ln14ya/",
)
l14 += header(("products", False))
l14 += "<main id=\"main\">\n" + page_hero(
    [("/", "Главная"), ("/products/", "Продукция"), ("/products/ln14ya/", "LN14YA")],
    "LN14YA – перспективный полётный контроллер",
    "LN14YA – разрабатываемое электронное устройство управления для беспилотных платформ. Проект предусматривает развитие вычислительных и навигационных функций, а также возможностей интеграции в состав различных систем.",
    tag="В разработке",
)
l14 += """<section class="section">
<div class="container">
<div class="spec-row">
<h2>Статус разработки</h2>
<div>
<p>Изделие находится на стадии разработки. Окончательный состав функций и условия применения будут определены по результатам дальнейшей инженерной проработки.</p>
</div>
</div>
<div class="spec-row">
<h2>Сотрудничество</h2>
<div>
<p>Для получения актуальной информации о проекте и возможности применения LN14YA направьте запрос специалистам компании.</p>
<a class="btn" href="{cta}">Запросить информацию о LN14YA</a>
</div>
</div>
</div>
</section>
</main>
""".format(cta=contact_link("Запрос информации о LN14YA"))
l14 += footer() + scripts()
write("/products/ln14ya/", l14)

# ============================ Разработки ============================
pr = head(
    "Технологические разработки – ООО «ЛоджикНав»",
    "Инженерные проекты ООО «ЛоджикНав» в области электроники, навигации и систем мониторинга. Распределённая акустическая система «Тетива-М».",
    "/projects/",
)
pr += header(("projects", True))
pr += "<main id=\"main\">\n" + page_hero(
    [("/", "Главная"), ("/projects/", "Разработки")],
    "Технологические разработки",
    "ЛоджикНав развивает инженерные проекты в области электроники, навигации и систем мониторинга. В разделе представлены направления, находящиеся в разработке, и сведения об их назначении.",
)
pr += """<section class="section">
<div class="container">
<h2 class="visually-hidden">Разработки</h2>
<div class="cards cards--3">
<article class="card">
<div class="card-body">
<h3>«Тетива-М»</h3>
<p>«Тетива-М» – распределённая акустическая система на основе оптоволокна.</p>
</div>
<a class="btn btn--outline" href="/projects/tetiva-m/">Подробнее</a>
</article>
</div>
</div>
</section>
</main>
"""
pr += footer() + scripts()
write("/projects/", pr)

# ============================ Тетива-М ==============================
t = head(
    "Тетива-М – распределённая акустическая система – ЛоджикНав",
    "Разрабатываемая оптоволоконная система распределённого акустического мониторинга.",
    "/projects/tetiva-m/",
)
t += header(("projects", False))
t += "<main id=\"main\">\n" + page_hero(
    [("/", "Главная"), ("/projects/", "Разработки"), ("/projects/tetiva-m/", "«Тетива-М»")],
    "«Тетива-М» – распределённая акустическая система",
    "«Тетива-М» – разрабатываемая система распределённого акустического мониторинга на основе оптоволоконной технологии. Решение ориентировано на наблюдение за событиями вдоль протяжённых объектов и инфраструктуры.",
)
t += """<section class="section">
<div class="container">
<div class="spec-row">
<h2>Назначение</h2>
<div>
<p>Система предназначена для организации непрерывного мониторинга и выявления акустических воздействий на протяжённых участках. Возможность применения рассматривается с учётом требований конкретного объекта.</p>
</div>
</div>
<div class="spec-row">
<h2>Области применения</h2>
<div>
<p>Мониторинг протяжённой инфраструктуры, охрана периметров и наблюдение за состоянием объектов. Конфигурация системы и условия внедрения определяются для каждого проекта отдельно.</p>
</div>
</div>
<div class="spec-row">
<h2>Дополнительная информация</h2>
<div>
<p>Для обсуждения применения системы «Тетива-М» и получения подробных материалов свяжитесь с представителями ООО «ЛоджикНав».</p>
<a class="btn" href="{cta}">Запросить информацию о «Тетиве-М»</a>
</div>
</div>
</div>
</section>
</main>
""".format(cta=contact_link("Запрос информации о «Тетиве-М»"))
t += footer() + scripts()
write("/projects/tetiva-m/", t)

# ============================ О компании ============================
a = head(
    "О компании – ООО «Логическая навигация»",
    "Российская инженерная компания. Разработка электроники, навигационных решений и систем мониторинга.",
    "/about/",
)
a += header(("about", True))
a += """<main id="main">
<section class="page-hero on-dark">
<div class="container">
<nav aria-label="Навигационная цепочка"><ol class="breadcrumbs"><li><a href="/">Главная</a></li><li><span aria-current="page">О компании</span></li></ol></nav>
<div class="hero-split">
<div>
<h1>О компании</h1>
<p class="lead">ООО «Логическая навигация» (ООО «ЛоджикНав») – российская инженерная компания, работающая в области разработки электронной аппаратуры, систем управления, навигации и мониторинга.</p>
</div>
<figure class="plate about-logo"><img src="/assets/img/logo_extended.png" width="1384" height="948" alt="ЛоджикНав — Логическая навигация" loading="lazy"></figure>
</div>
</div>
</section>
<section class="section">
<div class="container">
<div class="spec-row">
<h2>Направления деятельности</h2>
<div>
<ul class="plain-list">
<li>Разработка полётных контроллеров и электронных модулей</li>
<li>Создание и развитие навигационных решений</li>
<li>Разработка аппаратно-программных систем мониторинга</li>
</ul>
</div>
</div>
<div class="spec-row">
<h2>Инженерный подход</h2>
<div>
<p>В работе над проектами мы последовательно рассматриваем задачу заказчика, прорабатываем требования к изделию, создаём опытные решения и выполняем их проверку.</p>
</div>
</div>
<div class="spec-row">
<h2>Сведения об организации</h2>
<div>
<dl class="company-details">
<dt>Полное наименование</dt><dd>{full}</dd>
<dt>Сокращённое наименование</dt><dd>{short}</dd>
<dt>Дата регистрации</dt><dd>{registered}</dd>
<dt>Генеральный директор</dt><dd>{director}</dd>
<dt>Основной вид деятельности (ОКВЭД {okved})</dt><dd>{okved_description}</dd>
</dl>
</div>
</div>
<div class="spec-row">
<h2>Сотрудничество</h2>
<div>
<p>Открыты к обсуждению технических задач, интеграции электронных модулей и перспективных совместных разработок.</p>
<a class="btn" href="/contacts/">Связаться с нами</a>
</div>
</div>
</div>
</section>
</main>
""".format(full=FULL_LEGAL_NAME, short=SHORT_NAME, registered=REGISTERED, director=DIRECTOR, okved=OKVED, okved_description=OKVED_DESCRIPTION)
a += footer() + scripts()
write("/about/", a)

# ============================ Контакты ==============================
c = head(
    "Контакты – ООО «ЛоджикНав»",
    "Контактная информация и форма обращения по вопросам продукции, разработок и сотрудничества.",
    "/contacts/",
)
c += header(("contacts", True))
c += "<main id=\"main\">\n" + page_hero(
    [("/", "Главная"), ("/contacts/", "Контакты")],
    "Контакты",
    "По вопросам продукции, разработок и сотрудничества подготовьте письмо через форму или напишите на нашу электронную почту.",
)
c += """<section class="section">
<div class="container contact-grid">

<div>
<h2 class="visually-hidden">Реквизиты</h2>
<dl class="requisites">
<dt>Полное наименование</dt>
<dd>{full}</dd>
<dt>Сокращённое наименование</dt>
<dd>{short}</dd>
<dt>ОГРН</dt>
<dd>{ogrn}</dd>
<dt>ИНН / КПП</dt>
<dd>{inn} / {kpp}</dd>
<dt>Дата регистрации</dt>
<dd>{registered}</dd>
<dt>Юридический адрес</dt>
<dd>{legal_address}</dd>
<dt>Генеральный директор</dt>
<dd>{director}</dd>
<dt>Электронная почта</dt>
<dd><a href="mailto:{email}">{email}</a></dd>
</dl>
</div>

<div class="form-card">
<h2>Направить запрос</h2>
<p class="form-hint">Заполните поля. После нажатия кнопки откроется почтовое приложение с подготовленным письмом. Письмо отправляется вами самостоятельно.</p>

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
""".format(
    email=EMAIL,
    full=FULL_LEGAL_NAME,
    short=SHORT_NAME,
    ogrn=OGRN,
    inn=INN,
    kpp=KPP,
    registered=REGISTERED,
    legal_address=LEGAL_ADDRESS,
    director=DIRECTOR,
)
c += footer() + scripts()
write("/contacts/", c)

# ============================ 404 ===================================
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

# ============================ sitemap / robots ======================
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
