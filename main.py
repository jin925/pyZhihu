import os.path
import uuid
import utils
from playwright.sync_api import Page
from ebook import Chapter
from spider import Parser, Spider
from pyquery import PyQuery as pq


class ZhihuParser(Parser):

    def fetch_book_name(self, page: Page) -> str:
        return page.locator(".HeaderInfo-title-h6ouo").inner_text()

    def fetch_author(self, page: Page) -> str:
        return page.locator(".HeaderInfo-subTitle-oXPCU").inner_text()

    def fetch_cover(self, page: Page) -> str:
        img_url = page.locator(".HeaderInfo-cover-c5QFS .Image-module-image-uorig").get_attribute('src')
        img_f = utils.download_image(url=img_url, output=self.out_dir)
        return img_f

    def fetch_intro(self, page: Page) -> str:
        # 点击展开
        page.locator(".IntroSummary-expandButton-iZSs9").click()
        return page.locator(".IntroSummary-richText-emmXR").inner_text()

    def fetch_chapter_list(self, page: Page) -> list[Chapter]:
        page.locator('.ChapterItem-title-g1yzW').first.click()
        chapters = [self.fetch_chapter(page)]
        while self.fetch_next_chapter(page):
            chapters.append(self.fetch_chapter(page))

        return chapters

    def fetch_chapter(self, page: Page) -> Chapter:
        page.wait_for_load_state('domcontentloaded')
        title = page.locator('.ManuscriptTitle-root-gcmVk').inner_text()
        content = self.format_content(content=f'<h1>{title}</h1>' + page.locator('#manuscript').inner_html())
        file = f'{self.out_dir}\\{uuid.uuid1()}.html'
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'章节：【{title}】下载完成，数据文件：{file}')
        return Chapter(title=title, file=file)

    def fetch_next_chapter(self, page: Page) -> bool:
        if page.locator('.NextSection-tip-kkFPi').count() == 0:
            return False

        page.locator('.NextSection-tip-kkFPi').scroll_into_view_if_needed()
        page.locator('.NextSection-tip-kkFPi').click()
        return True

    def format_content(self, content: str) -> str:
        doc = pq(content)
        # 计算img的src
        for el in doc('img'):
            img_url = doc('img').attr('data-src')
            img_f = utils.download_image(url=img_url, output=os.path.join(self.out_dir, 'images'))
            doc(el).attr('src', '.' + img_f.replace(self.out_dir, '').replace('\\', '/'))
            doc(el).attr('style', 'width:100%;')
        # 移除图面加载中字样
        doc('figure span').remove()
        # 移除备案号
        doc('p').eq(-1).remove()
        return doc.html()


if __name__ == '__main__':
    # todo 解析url参数  python3 main.py -u URL -o FILE
    url = "https://www.zhihu.com/xen/market/remix/paid_column/1367971634872242176"
    parser = ZhihuParser()
    spider = Spider(url=url, parser=parser, out_path="./", with_gui=False)
    spider.process()
