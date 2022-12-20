import os
import pickle
from ebooklib import epub


class Chapter:
    """
    Ebook章节类
    """

    def __init__(self, title: str, file: str):
        """
        初始化
        :param title: 章节标题
        :param file: 章节文件
        """
        self.title = title
        self.file = file


class Ebook:
    """
    Ebook类
    """

    def __init__(self, book_name: str, cover='', author='', intro='', lang='zh', out_dir='./', data_dir="./") -> None:
        """
        初始化
        :param book_name: 书名
        :param cover: 封面
        :param author: 作者
        :param intro: 简介
        :param lang: 语言
        :param out_dir: 输出目录 默认当前目录
        :param data_dir: 数据文件目录 默认当前
        """
        self.book_name = book_name
        self.cover = cover
        self.author = author
        self.intro = intro
        self.lang = lang
        self.out_dir = out_dir
        self.data_dir = data_dir
        self._chapters = []

    def add_chapter(self, chapter: Chapter):
        """
        添加章节
        :param chapter: 章节实例
        :return:
        """
        self._chapters.append(chapter)

    @staticmethod
    def make_book_from_cache(data_dir, out_dir: str = './'):
        """
        从电子书缓存目录生成图书
        :param data_dir: 数据目录
        :param out_dir: 输出目录
        :return:
        """
        book_f = f'{data_dir}/book'
        if not os.path.isfile(book_f):
            raise FileNotFoundError(f'电子书缓存文件{book_f}不存在')
        with open(book_f, 'r+b') as fp:
            ebook = pickle.load(fp)

        print(ebook.book_name, ebook.author)
        ebook.save(out_dir)

    def save(self, out_dir: str = None):
        """
        生成电子书
        :param out_dir: 输出目录
        :return:
        """
        if out_dir is not None:
            self.out_dir = out_dir

        if not os.path.exists(self.out_dir):
            os.mkdir(out_dir)

        print('开始生成电子书')
        print('生成目录：' + self.out_dir)
        book = epub.EpubBook()
        book.set_identifier('abc')
        book.set_title(self.book_name)
        book.set_language(self.lang)
        book.add_author(self.author)

        # 添加封面
        with open(self.cover, 'rb') as fp:
            cover_content = fp.read()
        book.set_cover(file_name='cover.jpg', content=cover_content)

        # 添加简介页
        c_intro = epub.EpubHtml(title='简介', file_name='intro.xhtml')
        c_intro.content = f'<h1>简介</h1><p>{self.intro}</p>'
        book.add_item(c_intro)

        # 添加章节
        c_idx = 0
        chapters = [c_intro]
        for c in self._chapters:
            with open(c.file, 'r', encoding='utf-8') as fp:
                c_idx += 1
                chapter = epub.EpubHtml(title=c.title, file_name=f'c{c_idx}.xhtml')
                chapter.set_content(fp.read())

            book.add_item(chapter)
            chapters.append(chapter)

        # 添加章节内的图片
        if os.path.exists(os.path.join(self.data_dir, 'images/')):
            for img_f in os.scandir(os.path.join(self.data_dir, 'images/')):
                with open(img_f.path, 'rb') as fp:
                    img_item = epub.EpubItem(file_name=f'images/{img_f.name}', media_type='image/jpeg')
                    img_item.set_content(fp.read())

                book.add_item(img_item)

        # 添加导航
        book.toc = tuple(chapters)
        book.spine = ['nav'] + chapters

        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        epub.write_epub(f'{self.out_dir}/{self.book_name}.epub', book=book)
        print('电子书生成完成')
