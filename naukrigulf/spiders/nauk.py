import scrapy
import playwright
import scrapy_playwright
import math

def shoud_abord_request(request):
    if request.resource_type == "image":
        return True
    if request.method.lower()=='post':
        return True
    return False

class NaukSpider(scrapy.Spider):
    name = 'nauk'
    custom_settings:{'PLAYWRIGHT_ABORT_REQUEST':shoud_abord_request}

    def start_requests(self):
        yield scrapy.Request(
            url="https://www.naukrigulf.com/frontend-jobs-?sort=date",
            callback=self.parse,
            meta=dict(playwright= True,
            playwright_page_coroutines=[
            scrapy_playwright.page.PageMethod('wait_for_selector','//h2[@class="designation-title"]')
            ]
            )   
        )
        


    def parse(self, response):
        urls=response.xpath('//div/a[@target="_blank"][1]/@href').extract()
        # if  response.request.url=="https://www.naukrigulf.com/frontend-jobs-":
        #     NUMBER=response.xpath('//div[@class="headline"]/text()').extract()
        #     n=int(''.join(filter(str.isdigit,NUMBER[0])))
        #     number_of_pages=math.ceil(n/30)+1
        
        for url in urls:
            if "naukrigulf" in url:
                yield scrapy.Request(
                url=url,
                callback=self.parse_details,
                meta=dict(playwright= True,
                playwright_page_coroutines=[
                scrapy_playwright.page.PageMethod('wait_for_selector','//div[@class="candidate-profile"]')
                ]
                )
                )
        
        next=str(response.xpath('//a[@class="end disabled-false"]/@href').extract()[0])
        next_page = str("https://www.naukrigulf.com"+next)
        print("****************************")
        print(next_page)
        print("****************************")
        if next is not None:
            print("##################################")
            print(next_page)
            print("##################################")
            yield scrapy.Request(
            url=next_page,
            callback=self.parse,
            meta=dict(playwright= True,
            playwright_page_coroutines=[
            scrapy_playwright.page.PageMethod('wait_for_selector','//h2[@class="designation-title"]')
            ]
            )
            )
        # for j in range(2,number_of_pages):
        #     next_page_url="https://www.naukrigulf.com/frontend-jobs-"+str(j)+"?sort=date"
        #     yield scrapy.Request(
        #     url=next_page_url,
        #     callback=self.parse,
        #     meta=dict(playwright= True,
        #     playwright_page_coroutines=[
        #     scrapy_playwright.page.PageMethod('wait_for_selector','//h2[@class="designation-title"]')
        #     ]
        #     )
        #     )
    def parse_details(self,response):
        yield{
            'job title':response.xpath('//h1[@class="info-position"]/text()').extract(),
            'company':response.xpath('//p[@class="info-org"]/text()').extract(),
            'posted date':response.xpath('//p[@class="jd-timeVal"]/text()').extract(),
            'location':response.xpath('/html/body/div[1]/div[2]/main/div[1]/section[1]/div[3]/div[1]/div[1]/div[2]/p[2]/a[1]/text()').extract(),
            'vacancy':response.xpath('/html/body/div[1]/div[2]/main/div[1]/section[1]/div[3]/div[1]/div[2]/div[3]/p[2]/text()').extract(),
            'link':response.url,
        }