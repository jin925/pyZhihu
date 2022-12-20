import abc
import pickle
import tempfile
import utils
from multiprocessing import Process
from ebook import Ebook, Chapter
from playwright.sync_api import sync_playwright, Page, TimeoutError


class Parser:
    __metaclass__ = abc.ABCMeta

    def __init__(self) -> None:
        self.out_dir = tempfile.mkdtemp()
        print('Spider临时工作目录：' + self.out_dir)
        super().__init__()

    def parse(self, page: Page) -> Ebook:
        book_name = self.fetch_book_name(page)
        author = self.fetch_author(page)
        cover = self.fetch_cover(page)
        intro = self.fetch_intro(page)
        ebook = Ebook(book_name=book_name, cover=cover, author=author, intro=intro, data_dir=self.out_dir)
        chapters = self.fetch_chapter_list(page)
        for c in chapters:
            ebook.add_chapter(c)
        # 生成电子书临时文件
        with open(self.out_dir + '/book', 'w+b') as f:
            pickle.dump(ebook, f)

        return ebook

    @abc.abstractmethod
    def fetch_book_name(self, page: Page) -> str:
        pass

    @abc.abstractmethod
    def fetch_author(self, page: Page) -> str:
        pass

    @abc.abstractmethod
    def fetch_cover(self, page: Page) -> str:
        pass

    @abc.abstractmethod
    def fetch_intro(self, page: Page) -> str:
        pass

    @abc.abstractmethod
    def fetch_chapter_list(self, page: Page) -> list[Chapter]:
        pass

    @abc.abstractmethod
    def fetch_chapter(self, page: Page) -> Chapter:
        pass

    @abc.abstractmethod
    def fetch_next_chapter(self, page: Page) -> list[Chapter]:
        pass

    @abc.abstractmethod
    def format_content(self, content: str) -> str:
        pass


class Spider:
    def __init__(self, url: str, parser: Parser, out_path: str = "./", with_gui=False) -> None:
        if not isinstance(parser, Parser):
            raise TypeError('参数parser不是Parser的实例')
        self.url = url
        self.parser = parser
        self.out_path = out_path
        self.with_gui = with_gui

    def process(self) -> None:
        """
        爬取执行
        :return:
        """
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=not self.with_gui)
            context = browser.new_context()
            page = context.new_page()
            page.set_default_timeout(10e3)
            try:
                page.goto('https://www.zhihu.com/signin')
            except TimeoutError:
                print('无法访问知乎页面，请检查本机是否能正常访问网络')
                exit()
            qr_rect = page.eval_on_selector('.Qrcode-qrcode', 'el => el.getBoundingClientRect()')
            img_f = f'{self.parser.out_dir}/qr.png'
            page.screenshot(path=img_f, clip=qr_rect)
            print('请在30秒内使用知乎App或者微信扫码弹出二维码，登录知乎')

            try:
                with page.expect_navigation(timeout=30e3):
                    p = Process(target=utils.show_img, args=(img_f,), daemon=True)
                    p.start()
            except TimeoutError:
                print('您似乎长时间没有扫码，退出执行')
                print(p.pid)
                p.terminate()
                exit()

            print(p.pid)
            p.terminate()
            print('开始抓取电子书：' + self.url)
            page.goto(self.url)
            ebook = self.parser.parse(page)
            ebook.save()
            context.close()
            browser.close()
