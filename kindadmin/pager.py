class Pagination:
    def __init__(self,items,getargs=None,url='',pageItemLs=1,maxPageNum=11):
        '''

        :param items:  数据库查询的数据
        :param currenPageNum: 当前页码          ---  curren_page_num
        :param pageItemLs:    一页显示多少条数据---  page_item_list
        :param maxPageNum:    页面最多显示多少页码---max_page_num
        :param url:         在哪个页面进行分页   --- url
        :param getargs:         保留url带有get参数   --- url
        '''
        self.url = url
        self.items = items
        self.page_items_max = items.count()
        self.page_item_list = pageItemLs
        self.curren_page_num = None
        #如果最多显示页码大于总页数，那就把总页数赋值给最多显示页码
        self.max_page_num = maxPageNum if self.total_page_num > maxPageNum else self.total_page_num
        '''
        如果传入的当前页码不是整数，当前页码就直接赋值为1，
        如果传入的当前页码小于等于0 ，当前页码就直接赋值为1，
        如果传入的当前页码大于数据能分出来的最大页码数，就把当前页码赋值为最大页码数
        否则就把传入的当前页码赋值给当前页码
        '''
        self.get_args(getargs)
        try:
            v = int(self.curren_page_num)
            if v <= 0 :
                self.curren_page_num = 1
            elif v > self.total_page_num:
                self.curren_page_num = self.total_page_num
            else:
                self.curren_page_num = v
        except Exception as e:
            self.curren_page_num = 1



    def get_args(self,getargs):
        result = ''
        for k,v in getargs.items():
            if k != 'p':
                if v:
                    result += '&%s=%s' % (k,v)
            else:
                self.curren_page_num = v

        self.url_args =  result

    def get_item(self):
        '''
        根据分页生成数据返回
        :return:
        '''
        return self.items[self.start:self.end]


    @property
    def total_page_num(self):
        '''
        计算总页数
        :return:
        '''
        total,b = divmod(self.page_items_max,self.page_item_list)
        total = total + 1 if b != 0 else total
        return  total

    @property
    def start(self):
        '''计算数据切片的起始切片位置'''
        return ( self.curren_page_num -1 ) * self.page_item_list

    @property
    def end(self):
        '''计算数据切片的结束切片位置'''
        return  self.curren_page_num * self.page_item_list


    def pagenum_range(self):
        '''
        动态生成页码
        :return:
        '''
        #以显示页码数量的一半为临界点
        page = self.max_page_num // 2
        if self.curren_page_num <= page:
            #如果当前页码小于临界点，页码的显示就是 1 - 最大能分出的页码数
            return range(1,self.max_page_num+1)

            #如果(当前页 + page) 要大于 总页码数量， 页码数就显示  （总页数 - 一页最多显示页码数 +1） - （总页数 + 1）
        if (self.curren_page_num + page) > self.total_page_num :
            return range(self.total_page_num - self.max_page_num + 1 ,self.total_page_num +1 )

         # 页码数就显示  （当前页码数 - page） - （当前页 + page + 1）
        return  range(self.curren_page_num - page,self.curren_page_num + page + 1)

    def item_list(self,type='http'):
        '''
        返回HTML代码
        :return:
        '''
        if self.page_items_max:
            item = ['<nav aria-label="..." ><ul class="pagination">',]
            if type == 'http':
                item.append( '<li><a href="%s?p=1%s">首页</a></li>' % (self.url,self.url_args))
                if self.curren_page_num == 1:
                    item.append('<li class="disabled"><a>上一页</a></li>')
                else:
                    item.append('<li><a href="%s?p=%s%s">上一页</a></li>' % (self.url, self.curren_page_num - 1,self.url_args))
                for i in self.pagenum_range():
                    if i == self.curren_page_num:
                        item.append('<li class="active"><a href="%s?p=%s%s">%s</a></li>' % (self.url, i,self.url_args, i))
                    else:
                        item.append('<li><a href="%s?p=%s%s">%s</a></li>' % (self.url, i,self.url_args, i))

                if self.curren_page_num == self.total_page_num:
                    item.append('<li class="disabled"><a>下一页</a></li>')
                else:
                    item.append('<li><a href="%s?p=%s%s">下一页</a></li>' % (self.url, self.curren_page_num + 1,self.url_args))

                item.append('<li><a href="%s?p=%s%s">尾页</a></li>' % (self.url, self.total_page_num,self.url_args))


            elif type == 'ajax':
                item.append('<li><a pager=1>首页</a></li>')
                if self.curren_page_num == 1:
                    item.append('<li class="disabled"><a>上一页</a></li>')
                else:
                    item.append('<li><a pager=%s>上一页</a></li>' % (self.curren_page_num - 1))
                for i in self.pagenum_range():
                    if i == self.curren_page_num:
                        item.append('<li class="active"><a pager=%s>%s</a></li>' % ( i, i))
                    else:
                        item.append('<li><a pager=%s>%s</a></li>' % ( i, i))

                if self.curren_page_num == self.total_page_num:
                    item.append('<li class="disabled"><a>下一页</a></li>')
                else:
                    item.append('<li><a pager=%s>下一页</a></li>' % (self.curren_page_num + 1))

                item.append('<li><a pager=%s>尾页</a></li>' % (self.total_page_num))
            item.append(' </ul></nav>')
            return ''.join(item)
        else:
            return ''