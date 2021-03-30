import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import SouthstateItem
from itemloaders.processors import TakeFirst
import json
pattern = r'(\xa0)?'

class SouthstateSpider(scrapy.Spider):
	name = 'southstate'
	page = 1
	start_urls = [f'https://www.southstatebank.com/api/articlesearch/Index?Sort=newest&PageSize=9&PageNum={page}&RelatedTags=Customer%20Spotlight%7CNews%20Release%7CSouthState%20Spotlight&FilterCategoryList%5B%5D=SouthStateStories&SelectedFilterList%5B0%5D%5BFilterCategoryName%5D=SouthStateStories&SelectedFilterList%5B0%5D%5BFilterTagName%5D=']

	def parse(self, response):
		data = json.loads(response.text)
		for index in range(len(data['Results'])):
			link = data['Results'][index]['Url']
			title = data['Results'][index]['Heading']
			date =data['Results'][index]['DateForDisplay']
			yield response.follow(link, self.parse_post, cb_kwargs=dict(date=date, title=title))

		next_page = f'https://www.southstatebank.com/api/articlesearch/Index?Sort=newest&PageSize=9&PageNum={self.page}&RelatedTags=Customer%20Spotlight%7CNews%20Release%7CSouthState%20Spotlight&FilterCategoryList%5B%5D=SouthStateStories&SelectedFilterList%5B0%5D%5BFilterCategoryName%5D=SouthStateStories&SelectedFilterList%5B0%5D%5BFilterTagName%5D='
		if self.page <= data['TotalPages']:
			self.page += 1
			yield response.follow(next_page, self.parse)

	def parse_post(self, response, date, title):
		content = response.xpath('//div[@class="body-content"][1]//text() |(//div[@class="body-content"])[2]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=SouthstateItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
