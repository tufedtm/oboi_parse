import scrapy
import urllib.request


class QuotesSpider(scrapy.Spider):
    name = 'oboi_palitra'
    site = 'http://oboi-palitra.ru'
    vendor_code = ''

    def start_requests(self):
        urls = [
            'http://oboi-palitra.ru/oboi/'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        pages_count = int(response.css('a.paginator__btn_next-all::attr(href)').extract_first().split('=')[-1])

        paginator_pages = []
        for page in range(1, pages_count + 1):
            paginator_pages.append(f'{self.site}/oboi/?PAGEN_1={page}')

        for page in paginator_pages:
            print(page)
            yield response.follow(page, self.parse_catalog)

    def parse_catalog(self, response):
        res = []

        for item in response.css('ul.catalog_list li > a::attr(href)').extract():
            res.append(f'{self.site}{item}')

        for item in res:
            yield response.follow(item, self.parse_item)

    def parse_item(self, response):
        self.vendor_code = self.parse_vendor_code(response=response.css('ul.detail_head'))

        yield {
            'vendor_code': self.vendor_code,
            'brand': self.parse_brand(response=response.css('div.d_logo_wrap')),
            'rooms': self.parse_rooms(response=response.css('ul.rooms')),
            'features': self.parse_features(response=response.css('div.features')),
            'suggest': self.parse_suggest(response=response.css('div.suggest_text')),
            'other_colors': self.parse_other_colors(response=response.css('div.left')),
            'rapport': self.parse_rapport(response=response.css('div.wallpaper')),
            'interior_photo': self.parse_interior_photo(response=response.css('a.open-image')),
            'texture_photo': self.parse_texture_photo(response=response.css('ul.texture_list')),
        }


    def parse_vendor_code(self, response):
        return response.css('li strong::text').extract_first()

    def parse_brand(self, response):
        return response.css('img').xpath('@alt').extract_first()

    def parse_rooms(self, response):
        return response.css('li a::text').extract()

    def parse_features(self, response):
        res = []
        for tr in response.css('tr'):
            k, v = tr.css('td::text').extract()
            res.append({
                'k': k,
                'v': v
            })

        return res

    def parse_suggest(self, response):
        return response.css('a::text').extract()

    def parse_other_colors(self, response):
        return sorted(
            [
                '-'.join(x.upper().split('_')[1:])
                for x in
                response.xpath('p[contains(text(), "Другие оттенки")]/following-sibling::ul//a/@title').extract()
            ]
        )

    def parse_interior_photo(self, response):
        return response.xpath('@href').extract()

    def parse_texture_photo(self, response):
        return response.css('a').xpath('@href').extract()

    def parse_rapport(self, response):
        tmp = response.xpath("@style").extract_first()[22:-1].split('/')
        tmp.pop(0)
        tmp.pop(1)
        tmp.pop(1)
        tmp.pop(4)
        tmp.pop(4)

        image_link = f'{self.site}/{"/".join(tmp)}'
        file_name = f'img/{self.vendor_code}.{image_link.split(".")[-1]}'
        urllib.request.urlretrieve(image_link, file_name)

        return image_link
