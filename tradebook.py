
# coding: utf-8

# ###### Yingke Yu yy2792

# # Equity Order Matcher

# - This project is to create an equity order matcher that deals with online trading orders, the design requirements come from a reference attached.
# 
# 
# - The equity order matcher is essientially a dictionary of pairs of buy side and sell side trading books. Each key of the dictionary is a stock symbol. 
# 
# 
# - There are three types of trading orders, Limit order, Market order, and Immediate and Cancel (IOC) order. IOC order dies if not matched in one matching round. The execution between buy and sell orders depend on first come first serve criteria. Match is made only when the buy price is higher than the sell price, the final price depends on which order comes earlier.
# 
# 
# - The equity order matcher deals with 5 kinds of orders. Each is defined as a class. They are New order which adds new trading orders to the matcher, Amend orders which change the existing order, Match order that triggers trading order match, Cancel orders that cancel existing order, and Query order which is used to make screen shoot of a matcher, or restore historical matcher screen.
# 
# 
# - Essentially the equity order book is implemented as a deque for most time we add to the order book from the end, and pop from the top.
# 
# 
# - Classes are made for orders, buy and sell trading book, one stock symbol's trading book (both buy and sell), and equity order matcher (dictionary of stock symbol's trading books).
# 
# 
# - A simple test is added at the end of the project, which demonstrates how to use the existing classes and methods.

# In[1]:


import numpy as np


# -    Here we define a customerror class, the content of which can be changed for practice, basically all mistakes that could happen during this project will raise customerror

# In[2]:


#define error class
class Customerror(Exception):
    pass


# In[3]:


#deal with order string separating

import re
def tostringt(stringwithspace):
    clean_string =  re.sub(r"\s+", "", stringwithspace)
    clean_string = clean_string.split(',')
    return clean_string


# In[4]:


#handy function for judge a string to be an int

def isint(x):
    try:
        a = float(x)
        b = int(a)
    except ValueError:
        return False
    else:
        return a == b


# -  For this part, we define mutiple order classes, one reason is that, an order can be given as a string in different format, making the string into a structured class will provide convenience. 
# -  Besides, with class we define the comparison functions between different orders, buy or sell orders will be compared in price first, then compared with ordered time, this process will decide which order is "larger". It helps future order matching.

# In[5]:


#First start with making an order class

#new order

class neworder:
    def __init__(self, orderstr):
        
        self.strep = re.sub(r"\s+", "", orderstr)
        
        orderstr = tostringt(orderstr)
        
        self.action = 'N'
        
        if len(orderstr)!=8:
            raise Customerror
        
        if not isint(orderstr[1]) or not isint(orderstr[2]):
            raise Customerror
        
        self.orderid = int(orderstr[1])       
        
        if float(orderstr[6])<0:
            print("{}-303-invalid".format(self.orderid))
            raise Customerror
        
        if not isint(orderstr[7]) or (int(orderstr[7])<0 and int(orderstr[7])>2**63-1):
            print("{}-303-invalid".format(self.orderid))
            raise Customerror
        
        self.timestamp = int(orderstr[2])   
        self.symbol = orderstr[3]
        self.ordertype = orderstr[4]
        self.side = orderstr[5]   
        self.price = float(orderstr[6]) 
        self.quantity = int(orderstr[7])
        
    def __str__(self):
        return self.strep
                                          
    def __repr__(self):
        return str(self)
    
    def getstring(self):
        lst = []
        lst.append(str(self.orderid))
        lst.append(str(self.ordertype))
        lst.append(str(self.quantity))
        lst.append(str(self.price))
        return ",".join(lst)
    
    def getrevstring(self):
        lst = []
        lst.append(str(self.price))
        lst.append(str(self.quantity))
        lst.append(str(self.ordertype))
        lst.append(str(self.orderid))
        return ",".join(lst)
        
    
    # if the change is to decrease quantity, the timestamp does not change, other cases time need to be changed 
    
    def change(self, s, quant, newtimestamp):
        if s == 'quantity':
            if not isint(quant):
                raise Customerror
                
            if int(quant) <= self.quantity:
                self.quantity = int(quant)
                tempstr = self.strep.split(',')
                tempstr[7]=quant
                self.strep = ','.join(tempstr)
                
            else:
                self.quantity = quant
                self.timestamp = int(newtimestamp)               
                tempstr = self.strep.split(',')
                tempstr[7]=quant
                tempstr[2]=newtimestamp
                self.strep = ','.join(tempstr)
        
        elif s == 'price':
            if float(quant)!=self.price:
                self.price = float(quant)
                self.timestamp = int(newtimestamp)
                tempstr = self.strep.split(',')
                tempstr[6]=quant
                tempstr[2]=newtimestamp
                self.strep = ','.join(tempstr)
        
        else:
            print("only quantity and price are allowed to be changed")
            raise Customerror
    
    # operators should be carefully defined here
    
    # for market order, it will be larger than (prior to) any other order only if its time is earlier
    # for limit buy order, the higher the price, the larger (greater priority), then it should be based on FIFO
    # for limit sell order, the lower the price, the larger, then it should be based on FIFO
    # IOC order in priority should be the same as limit order
    
    # Here we assume only the orders of the same stock are compared
    
    #larger than is defined, then larger than is defined too
    def __gt__(self, other):
        
        #case 1, at least one market order, then comparison is only based on time,
        #comparison between two different sides are not defined
        
        if self.symbol != other.symbol:
            print("Compare between two same stocks order!")
            raise Customerror
        
        if (self.ordertype == "M" or other.ordertype == "M") and self.side == other.side:
            return self.timestamp < other.timestamp
        
        #case 2, two buy side limit order (limit or IOC)
        
        elif self.side == "B" and other.side == "B":
            if self.price != other.price:
                return self.price > other.price
            else:
                return self.timestamp < other.timestamp
        
        elif self.side == 'S' and other.side == "S":
            if self.price != other.price:
                return self.price < other.price
            else:
                return self.timestamp < other.timestamp
        
        #define comparison between different direction order will be handy in matching
        
        else:
            return self.timestamp < other.timestamp
            
    def __lt__(self, other):
        #case 1, at least one market order, then comparison is only based on time,
        #comparison between two different sides are not defined
        
        if self.symbol != other.symbol:
            print("Compare between two same stocks order!")
            raise Customerror
        
        if (self.ordertype == "M" or other.ordertype == "M") and self.side == other.side:
            return self.timestamp > other.timestamp
        
        #case 2, two buy side limit order (limit or IOC)
        
        elif self.side == "B" and other.side == "B":
            if self.price != other.price:
                return self.price < other.price
            else:
                return self.timestamp > other.timestamp
        
        elif self.side == 'S' and other.side == "S":
            if self.price != other.price:
                return self.price > other.price
            else:
                return self.timestamp > other.timestamp
        
        else:
            return self.timestamp > other.timestamp
     

    def ___le__(self, other):
        return not self.__gt__(other)
    
    def __ge__(self, other):
        return not self.__lt__(other)
    
    def __eq__(self, other):
        return self.__ge__(other) and self.__le__(other)
    
    def __ne__(self, other):
        return not self.__eq__(other)


# In[6]:


class amendorder(neworder):
    def __init__(self, orderstr):
        neworder.__init__(self, orderstr)
        self.action = 'A'
    
    def change(self, s, quant, newtimestamp):
        raise AttributeError( "'amendorder' object has no attribute 'change'" )


# In[7]:


class cancelorder(neworder):
    def __init__(self, orderstr):
        self.strep = re.sub(r"\s+", "", orderstr) 
        orderstr = tostringt(orderstr)
            
        self.action = 'X'
        
        if len(orderstr)!=3:
            raise Customerror
        
        if not isint(orderstr[1]) or not isint(orderstr[2]):
            raise Customerror
        
        self.orderid = int(orderstr[1])  
        self.timestamp = int(orderstr[2])
    
    def change(self, s, quant, newtimestamp):
        raise AttributeError( "'amendorder' object has no attribute 'change'" )


# In[8]:


class matchorder(cancelorder):
    def __init__(self, orderstr):
        self.strep = re.sub(r"\s+", "", orderstr) 
        orderstr = tostringt(orderstr)
            
        self.action = 'X'
        
        if len(orderstr)!=3 and len(orderstr)!=2:
            raise Customerror
        
        if not isint(orderstr[1]):
            raise Customerror
        
        self.timestamp = int(orderstr[1])  
        if len(orderstr)==3:
            self.symbol = orderstr[2]
        else:
            self.symbol = 'all'
        self.action = 'M'


# In[9]:


class queryorder(neworder):
    def __init__(self, orderstr):
        self.strep = re.sub(r"\s+", "", orderstr) 
        orderstr = tostringt(orderstr)
            
        self.action = 'Q'
        self.timestamp = '$'
        self.symbol = '$'
    
        if len(orderstr)==1:
            if orderstr[0] == 'Q':
                return
            else:
                print("invalid query order")
                raise Customerror
    
        #symbol is made up of only alphabets
        elif len(orderstr)==2:
            if isint(orderstr[1]):
                self.timestamp = orderstr[1]
            else:
                self.symbol = orderstr[1]
            
        elif len(orderstr)==3:
            if isint(orderstr[1]):
                self.timestamp = orderstr[1]
                self.symbol = orderstr[2]
            elif isint(orderstr[2]):
                self.timestamp = orderstr[2]
                self.symbol = orderstr[1]
            else:
                print("invalid query order")
                raise Customerror


# - When an order is added into a book, either buy side or sell side, the book should get sorted, by doing this, we perform swap inside a deque, then each new order getting added takes linear time.

# In[10]:


def swapp(lst, before, after):
    temp = lst[before]
    lst[before]=lst[after]
    lst[after]=temp


# In[11]:


from collections import deque
bv = deque()


# -    Orderbook is the class for one side order book, namely either buy side or sell side. It should have order property, can be used to modify or cancel order inside, and manually gets sorted. Orderbook should also track orderid, latest time inside the class, in case one new order with replicated id, or passed time will be added by mistake or by the purpose of cheating.

# In[12]:


from collections import deque

#use an deque to construct a buy or sell orderbook
#market order should only be placed with respect to time, but limit and IOC order should first be placed in order by price,
#then by time.


class orderbook:
    def __init__(self, symbol = "default"):
        self.list = deque()
        self.dct = {}
        self.latestime = -1
        self.symbol = symbol
        
    # I don't see any need to update latestime when an item is deleted
    
    def add_order(self, data):
        if data.action != 'N':
            print("Only new type order can be added to orderbook".format(data.orderid))
            raise Customerror
        
        if data.timestamp < self.latestime:
            print("{}-505-invalid time".format(data.orderid))
            raise Customerror
            
        if data.orderid in self.dct:
            print("{}-506-duplicated order id".format(data.orderid))
            raise Customerror
        
        self.dct[data.orderid]=1
        self.list.append(data)
        self.latestime = data.timestamp
        
        self.swapreorder(len(self.list)-1)
        
        print("{}-Accept".format(data.orderid))
    
    def getlist(self):
        return self.list
    
    def getdct(self):
        return self.dct
    
    def length(self):
        return len(self.list)
    
    def __getitem__(self, key):
        return self.list[key]
    
    def clear(self):
        self.list.clear()
        self.dct.clear()
        self.latestime = -1
        
    def change_order(self, amenddata):
        if amenddata.action!='A':
            print("Not an amend order to amend my order")
            raise Customerror
        
        if amenddata.orderid not in self.dct:
            print("{}-AmendReject-101-invalid amendment details".format(amenddata.orderid))
            raise Customerror
        
        targetind = -1
        
        #brutally search if the amend target id is inside the book, we assume amend does not happen often
        
        for i in range(len(self.list)):
            if self.list[i].orderid == amenddata.orderid:
                targetind = i
                
        if targetind == -1:
            print("{}-AmendReject-101-invalid amendment detials".format(amenddata.orderid))
            raise Customerror
        
        
        self.list[targetind].change('price',str(amenddata.price),str(amenddata.timestamp).zfill(7))
        self.list[targetind].change('quantity',str(amenddata.quantity),str(amenddata.timestamp).zfill(7))
                         
        #place the order to the right place (sorted in order)
        self.swapreorder(targetind)
    
    # to fixed a break of order property, namely earlier order should be in front of later order, we swap the changed cell with earlier left neighbor.
    
    def swapreorder(self, tempind):
        
        # here we directly call the class comaprison for order
        while tempind!=0 and self.list[tempind]>self.list[tempind-1]:
            swapp(self.list, tempind, tempind-1)
            tempind -=1
        
        while tempind!=len(self.list)-1 and self.list[tempind]<self.list[tempind+1]:
            swapp(self.list, tempind, tempind+1)
            tempind+=1
    
    def poprightorder(self):
        if len(self.list)==0:
            print("list is empty")
            raise Customerror
        temp = self.list.pop()

        del self.dct[temp.orderid]
        return temp
    
    def popleftorder(self):
        if len(self.list)==0:
            print("list is empty")
            raise Customerror
        temp = self.list.popleft()
        
        del self.dct[temp.orderid]
        return temp
    
    #most inefficient one 
    def deleteid(self, tempind):
        if len(self.list)==0:
            print("list is empty")
            raise Customerror
        
        if len(self.list)<=tempind:
            print("invalid delete index")
            raise Customerror
        
        if tempind == 0:
            return self.popleftorder()
        
        if tempind == len(self.list)-1:
            return self.poprightorder()
        
        temp = self.list[tempind]
        tempkey = self.list[tempind].orderid
        del self.dct[tempkey]
        del self.list[tempind]
        return temp
    
    def deleteorderid(self, orderid1):
        if orderid1 not in self.dct:
            return
        else:
            tempid = -1
            for j in range(len(self.list)):
                if self.list[j].orderid == orderid1:
                    tempid = j
                    break
            if tempid != -1:
                self.deleteid(tempid)
    
    def deleteioc(self):
        ioc = []
        for i in range(self.length()):
            if self.list[i].ordertype == 'I':
                ioc.append(self.list[i].orderid)
        for j in ioc:
            self.deleteorderid(j)
    
    #only used manually
    
    def updatelatestime(self):
        if len(self.list)==0:
            self.latestime = -1
        else:
            mintime = -1
            for k in self.list:
                if k.timestamp > mintime:
                    mintime = k.timestamp
            self.latestime = mintime
                
             


# In[13]:


from collections import OrderedDict


# -    Match methods are defined separately here but will be implemented inside double sided orderbook class. The basic logic is that, start from buy side, three cases will be encountered from the very top: we meet two limit orders (IOC orders are viewed limit orders here), one market order and one limit order, or two market orders. We define three methods to deal with those three situations.
# 
# -    In the double side order book, we start from the top and matching down, as said above one of three cases will be encountered. The trick is that once two limit orders do not match with each other, by the order property of the orderbooks, we know no more limit orders will get matched. Hence the rest of work is to satisfy the market orders on both side then the work is done.

# In[14]:


# we define match functions


# In[15]:


def limitmatch(bookb, books, idxb, idxs):
    
    result = []
    
    if idxb >= bookb.length() or idxs >= books.length():
        return result
    
    if bookb[idxb].ordertype not in ['L','I'] or books[idxs].ordertype not in ['L','I']:
        return result
    
    if bookb[idxb].ordertype in ['L','I'] and books[idxs].ordertype in ['L','I']:
        if bookb[idxb].price < books[idxs].price:
            #return a dollar sign to indicate, in the current book, no more limit order can be matched
        
            return ["$"]
        else:
            while bookb[idxb].price >= books[idxs].price and bookb[idxb].quantity > 0 and books.length()!=0:
                if bookb[idxb] > books[idxs]:
                    dealprice = bookb[idxb].price
                else:
                    dealprice = books[idxs].price
                    
                if bookb[idxb].quantity <= books[idxs].quantity:
                    dealquant = bookb[idxb].quantity
                    orderstring = bookb[idxb].symbol +"|" + bookb[idxb].getstring()+"|"+books[idxs].getrevstring()
                    result.append([orderstring, dealprice, dealquant])
                    books[idxs].change('quantity',str(books[idxs].quantity - dealquant), -1)
                    if books[idxs].quantity == 0:
                        books.deleteid(idxs)
                    bookb.deleteid(idxb)
                    return [result]
                    
                elif bookb[idxb].quantity > books[idxs].quantity:
                    dealquant = books[idxs].quantity
                    orderstring = bookb[idxb].symbol +"|" + bookb[idxb].getstring()+"|"+books[idxs].getrevstring()
                    
                    result.append([orderstring, dealprice, dealquant])
                    
                    bookb[idxb].change('quantity',str(bookb[idxb].quantity - dealquant), -1)
                    if bookb[idxb].quantity == 0:
                        bookb.deleteid(idxb)
                        return [result]
                    books.deleteid(idxs)
        return ['$', result] 


# In[16]:


def marketbuymatch(bookb, books, idxb, idxs):
    result = []
    
    if idxb >= bookb.length() or idxs >= books.length() or bookb.length()==0 or books.length()==0:
        return result
    
    if bookb[idxb].ordertype != 'M':
        return result
    
    if books[idxs].ordertype == 'M':
        idxs+=1
        
    while bookb[idxb].quantity > 0 and books.length()!=0:
        
        dealprice = books[idxs].price
        
        if bookb[idxb].quantity <= books[idxs].quantity:
            dealquant = bookb[idxb].quantity
            orderstring = bookb[idxb].symbol +"|" + bookb[idxb].getstring()+"|"+books[idxs].getrevstring()
            result.append([orderstring, dealprice, dealquant])
            books[idxs].change('quantity',str(books[idxs].quantity - dealquant), -1)
            if books[idxs].quantity == 0:
                books.deleteid(idxs)
            bookb.deleteid(idxb)
            return result
        
        elif bookb[idxb].quantity > books[idxs].quantity:
            dealquant = books[idxs].quantity
            orderstring = bookb[idxb].symbol +"|" + bookb[idxb].getstring()+"|"+books[idxs].getrevstring()
            result.append([orderstring, dealprice, dealquant])
            bookb[idxb].change('quantity',str(bookb[idxb].quantity - dealquant), -1)
            if bookb[idxb].quantity == 0:
                bookb.deleteid(idxb)
                return result
            books.deleteid(idxs)


# In[17]:


def marketsellmatch(bookb, books, idxb, idxs):
    result = []
    
    if idxb >= bookb.length() or idxs >= books.length() or bookb.length()==0 or books.length()==0:
        return result
    
    if books[idxs].ordertype != 'M':
        return result
    
    if bookb[idxb].ordertype == 'M':
        idxb+=1
        
    while books[idxs].quantity > 0 and bookb.length()!=0:
        
        dealprice = bookb[idxb].price
        
        if books[idxs].quantity <= bookb[idxb].quantity:
            dealquant = books[idxs].quantity
            orderstring = bookb[idxb].symbol +"|" + bookb[idxb].getstring()+"|"+books[idxs].getrevstring()
            result.append([orderstring, dealprice, dealquant])
            bookb[idxb].change('quantity',str(bookb[idxb].quantity - dealquant), -1)
            if bookb[idxb].quantity == 0:
                bookb.deleteid(idxb)
            books.deleteid(idxs)
            return result
        
        elif books[idxs].quantity > bookb[idxb].quantity:
            dealquant = bookb[idxb].quantity
            orderstring = bookb[idxb].symbol +"|" + bookb[idxb].getstring()+"|"+books[idxs].getrevstring()
            result.append([orderstring, dealprice, dealquant])
            books[idxs].change('quantity',str(books[idxs].quantity - dealquant), -1)
            if books[idxs].quantity == 0:
                books.deleteid(idxs)
                return result
            bookb.deleteid(idxb)


# -    With match functions defined above, here we define equitybook class, namely a double side orderbook, a structure that holds two orderbook instances. 
# 
# -    There is one method called presentmyself, it presents the buyside and sellside order books from top to down.
# 
# -    In this class, one tribute is called log, which records all historical orders, tribute orderlog records all the executed orders.

# In[18]:


# now we need a function to perform match orders, FIFO, which means the match and price is decided by the time of order
    
class equitybook():
    
    def __init__(self, symbol = 'Default'):
        self.buybook = orderbook(symbol)
        self.sellbook = orderbook(symbol)
        self.symbol = symbol
        self.log = OrderedDict()
        self.orderlog = []
        
    def clear(self):
        self.buybook.clear()
        self.sellbook.clear()
        self.symbol = 'Default'        
        self.log.clear()
        self.orderlog.clear()
    
    def getbuy(self):
        return self.buybook.getlist()
    
    def getsell(self):
        return self.sellbook.getlist()
    
    def deleteIOC(self):
        #this is used after each match, we clear all IOC order not matched
        self.buybook.deleteioc()
        self.sellbook.deleteioc()
    
    def addto_book(self, ordertxt):
    
        ty = ordertxt[0]
        if ty == 'N':
            order1 = neworder(ordertxt)
            if order1.side == 'B':
                self.buybook.add_order(order1)
            elif order1.side == 'S':
                self.sellbook.add_order(order1)
            
            self.orderlog.append([order1.timestamp, ordertxt])
                        
        elif ty == 'A':
            order1 = amendorder(ordertxt)
            if order1.side == 'B':
                self.buybook.change_order(order1)
            elif order1.side == 'S':
                self.sellbook.change_order(order1)
            self.orderlog.append([order1.timestamp, ordertxt])
            
        elif ty == 'X':
            order1 = cancelorder(ordertxt)
            self.buybook.deleteorderid(order1.orderid)
            self.sellbook.deleteorderid(order1.orderid)
            self.orderlog.append([order1.timestamp, ordertxt])
        
        elif ty == 'M':
            order1 = matchorder(ordertxt)
            self.matchbook(order1.timestamp)
            self.orderlog.append([order1.timestamp, ordertxt])
            
        '''
        elif ty == 'Q':
            order1 = queryorder(ordertxt)
        
        '''
    
    def intolog(self, times, result):
        if result == '$' or result is None or len(result)==0 or result[0]=='$':
            return
        
        if times not in self.log:
            if len(result)== 2 and result[0]=='$':
                self.log[times]=result[1]
            else:
                self.log[times]=result
        else:
            if len(result)== 2 and result[0]=='$':
                self.log[times]+=result[1]
            else:
                self.log[times]+=result
    
    def matchbook(self, times):
        buyidx = 0
        sellidx = 0
        
        flagfli = 1
        bigresult = []
        
        while buyidx != self.buybook.length() and sellidx != self.sellbook.length() and self.buybook.length()!=0 and self.sellbook.length()!=0:
            if self.buybook[buyidx].ordertype == 'M' and self.sellbook[sellidx].ordertype != 'M':
                result = marketbuymatch(self.buybook, self.sellbook, buyidx, sellidx)
                self.intolog(times, result)
                bigresult += result
                if self.sellbook.length() == 0:
                    break
                           
            elif self.buybook[buyidx].ordertype != 'M' and self.sellbook[sellidx].ordertype == 'M':
                result = marketsellmatch(self.buybook, self.sellbook, buyidx, sellidx)
                self.intolog(times, result)
                bigresult += result
                if self.buybook.length() == 0:
                    break
                    
            elif self.buybook[buyidx].ordertype != 'M' and self.sellbook[sellidx].ordertype != 'M':
                if flagfli == 1:
                    result = limitmatch(self.buybook, self.sellbook, buyidx, sellidx)
                    self.intolog(times, result)
                    if result is not None and len(result)!=0:
                        if result[0]!='$':
                            bigresult += result[0]
                        elif result[0]=='$':
                            if len(result)==2:
                                bigresult += result[1]
                            flagfli = 0
                            
                elif flagfli == 0:
                    buyidx+=1
            
            elif self.buybook[buyidx].ordertype == 'M' and self.sellbook[sellidx].ordertype == 'M':
                tempbuyidx = buyidx
                tempsellidx = sellidx
                targetbuy = -1
                targetsell = -1
                
                while tempsellidx!=self.sellbook.length():
                    if self.sellbook[tempsellidx].ordertype!='M':
                        targetsell = tempsellidx
                        break
                    tempsellidx+=1
                    
                result1 = marketbuymatch(self.buybook, self.sellbook, buyidx, targetsell)
                self.intolog(times, result1)
                bigresult += result1
                
                while tempbuyidx!=self.buybook.length():
                    if self.buybook[tempbuyidx].ordertype!='M':
                        targetbuy = tempbuyidx
                        break
                    tempbuyidx+=1
                
                result2 = marketsellmatch(self.buybook, self.sellbook, targetbuy, sellidx)
                self.intolog(times, result2)
                bigresult += result2
                
                if self.buybook.length()==0 or self.sellbook.length()==0:
                    break
        
        # we trace on the buy side, there might be some market order left on the sell side
        buyidx = 0
        while buyidx != self.buybook.length() and sellidx != self.sellbook.length() and self.buybook.length()!=0 and self.sellbook.length()!=0:
            if self.sellbook[sellidx].ordertype != 'M':
                sellidx+=1
            else:
                result = marketsellmatch(self.buybook, self.sellbook, buyidx, sellidx)
                self.intolog(times, result)
                bigresult += result
                if self.buybook.length() == 0:
                    break
        
        self.deleteIOC()
                    
        for k in bigresult:
            print(k)
    
    def presentmyself(self):
        buylen = self.buybook.length()
        selllen = self.sellbook.length()
        
        buyidx = 0
        sellidx = 0
        
        while buyidx!=buylen and sellidx!=selllen:
            temp = self.buybook.symbol +"|" + self.buybook[buyidx].getstring()+"|"+self.sellbook[sellidx].getrevstring()
            print(temp)
            buyidx+=1
            sellidx+=1
            
        while buyidx!=buylen:
            temp = self.buybook.symbol +"|" + self.buybook[buyidx].getstring()+"|"
            print(temp)
            buyidx+=1
        
        while sellidx!=selllen:
            temp = self.buybook.symbol +"|" +"|" + self.sellbook[sellidx].getrevstring()
            print(temp)
            sellidx+=1
            
            
            
    


# -    As for we want to restore all the historical orders, querybook function is separately defined here. The funciton simply starts from a brand new book and redo all the historical orders recorded in the tribute log. If a specific timestamp is given, we first traverse the log tribute to get the target time, and redo all the orders before that timestamp.

# In[19]:


# we should make a separate function for query command #

def querybook(bbook, ordertxt):
    qorder = queryorder(ordertxt)
    if qorder.timestamp == '$':
        bbook.presentmyself()
        return bbook
    
    elif qorder.timestamp != '$':
        targtime = int(qorder.timestamp)
        kk = -1
        for i in range(len(bbook.orderlog)):
            tt = int(bbook.orderlog[i][0])
            if tt > targtime:
                kk = i
                break
        if kk != -1: 
            newlog = bbook.orderlog[0:i]
        else:
            newlog = bbook.orderlog
        
        tempbook = equitybook()
        for i in newlog:
            tempbook.addto_book(i[1])
        
        tempbook.presentmyself()
    
        return tempbook
            
        


# In[20]:


def toorder(ordertxt):
    ty = ordertxt[0]
    if ty == 'M':
        return matchorder(ordertxt)
    elif ty == 'N':
        return neworder(ordertxt)
    elif ty == 'A':
        return amendorder(ordertxt)
    elif ty == 'X':
        return cancelorder(ordertxt)
    elif ty == 'Q':
        return queryorder(ordertxt)


# -   This is the final equity matcher, it is essentially a dictionary of tradebooks we defined before, each tradebook corresponds to one stock symbol.

# In[21]:


# Let us combine all these

class equitymatcher:
    def __init__(self, symbol = 'Default'):
        self.stomach = {}
        
    def add_order(self, ordertxt):
        ty = ordertxt[0]
        order1 = toorder(ordertxt)
        if ty == 'M':
            if order1.symbol == 'all':
                for key in self.stomach:
                    self.stomach[key].addto_book(ordertxt)
            else:
                if order1.symbol in self.stomach:
                    self.stomach[order1.symbol].addto_book(ordertxt)
                else:
                    print("symbol not in the book")
        
        elif ty == 'N':
            if order1.symbol in self.stomach:
                self.stomach[order1.symbol].addto_book(ordertxt)
            else:
                self.stomach[order1.symbol] = equitybook(order1.symbol)
                self.stomach[order1.symbol].addto_book(ordertxt)
        
        elif ty == 'A':
            if order1.symbol in self.stomach:
                self.stomach[order1.symbol].addto_book(ordertxt)
            else:
                print("no such symbol to amend")
        
        elif ty == 'X':
            for key in self.stomach:
                self.stomach[key].addto_book(ordertxt)
        
        elif ty == 'Q':
            if order1.symbol == '$':
                outt = []
                for key in self.stomach:
                    bbook = querybook(self.stomach[key],ordertxt)
                    bbook.symbol = key
                    bbook.buybook.symbol = key
                    bbook.sellbook.symbol = key
                    outt.append(bbook)
                
                for i in outt:
                    print()
                    print("The query for symbol {} is:".format(i.symbol))
                    i.presentmyself()
                #with outt we can restore the record
                return outt
            
            elif order1.symbol != '$':
                key = order1.symbol
                if key not in self.stomach:
                    print()
                    print("no such symbol")
                    return
                else:
                    bbook = querybook(self.stomach[key],ordertxt)
                    bbook.symbol = key
                    bbook.buybook.symbol = key
                    bbook.sellbook.symbol = key
                    print()
                    print("The query for symbol {} is".format(key))
                    bbook.presentmyself()
                    return bbook
        
    def getsymboldct(self):
        for key in self.stomach:
            print(key)
    
    def getsymbolbook(self, key):
        return self.stomach[key]
    
    def clear(self):
        for key in self.stomach:
            self.stomach[key].clear()
            
    def present(self):
        i = 0
        for key in self.stomach:
            if i!=0:
                print()
            print("Symbol {} stock book:".format(key))
            self.stomach[key].presentmyself()
            if i == 0:
                i=1
        


# # Let's run some test:

# ### We type in two stocks' trading order in our matcher:

# In[22]:


#for stock XYZ

s1 = "N,1,0000003,XYZ,M,B,0,100"
s2 = "N,2,0000004,XYZ,L,B,104,100"
s3 = "N,3,0000005,XYZ,L,B,105,100"
s4 = "N,4,0000006,XYZ,L,B,106,100"
s5 = "N,5,0000007,XYZ,M,B,0,200"
s6 = "N,6,0000008,XYZ,I,B,104.5,100"

ss1 = "N,8,0000013,XYZ,M,S,0,200"
ss2 = "N,9,0000014,XYZ,L,S,104,100"
ss3 = "N,13,0000015,XYZ,L,S,106.6,100"
ss4 = "N,14,0000016,XYZ,L,S,106.7,100"
ss5 = "N,15,0000017,XYZ,I,S,107.7,200"
ss6 = "N,16,0000018,XYZ,M,S,0,100"


# In[23]:


ax = [s1,s2,s3,s4,s5,s6,ss1,ss2,ss3,ss4,ss5,ss6]
bb = equitymatcher()
for i in ax:
    bb.add_order(i)


# ### This is how the equity matcher looks like:

# In[24]:


bb.present()


# In[25]:


#We now type in stock JAY

s1 = "N,17,0000019,JAY,M,B,0,100"
s2 = "N,18,0000020,JAY,L,B,55,100"
s3 = "N,19,0000025,JAY,L,B,57,100"
s4 = "N,20,0000027,JAY,L,B,58,100"
s5 = "N,21,0000030,JAY,L,B,56,200"
s6 = "N,22,0000033,JAY,L,B,60,100"

ss1 = "N,24,0000021,JAY,M,S,0,200"
ss2 = "N,26,0000022,JAY,L,S,57,100"
ss3 = "N,27,0000023,JAY,L,S,80,100"
ss4 = "N,28,0000024,JAY,L,S,70,100"
ss5 = "N,29,0000035,JAY,L,S,54,200"
ss6 = "N,30,0000036,JAY,M,S,0,100"


# In[26]:


ax = [s1,s2,s3,s4,s5,s6,ss1,ss2,ss3,ss4,ss5,ss6]
for i in ax:
    bb.add_order(i)


# In[27]:


bb.present()


# ### We amend order 22:

# In[28]:


# now 22 will be placed lower than 19, since the change of price will alter the timestamp of the order
q1 = "A,22,0000033,JAY,L,B,57,100"
bb.add_order(q1)
bb.getsymbolbook('JAY').presentmyself()


# In[29]:


# notice that if you just lower the quantity, no change of timestamp will be made
q1 = "A,20,0000033,JAY,L,B,58,90"
bb.add_order(q1)
bb.getsymbolbook('JAY').presentmyself()


# ### We now cancel order 27 since the price is ridiculous:

# In[30]:


q1 = "X, 27, 0000040"
bb.add_order(q1)
bb.present()


# ### Now we match the order, the output includes [trade detail, price reached, volumn]:

# In[31]:


q1 = "M, 0000041"
bb.add_order(q1)


# ### Note that orderid 15 did not get executed, it died simply because it is an IOC order:

# In[32]:


bb.present()


# ### We can reach all the log file for each book, and executed trade log:

# In[33]:


bb.getsymbolbook('XYZ').orderlog


# In[34]:


# For executed trade
bb.getsymbolbook('XYZ').log


# In[35]:


bb.getsymbolbook('JAY').orderlog


# In[36]:


bb.getsymbolbook('JAY').log


# ### I can also view the equity matcher with query order:

# In[37]:


q1 = "Q"
temp = bb.add_order(q1)


# ### With the log file we can restore what the equity matcher looked like at a certain time stamp, the below query order returns a list for restored books for different stocks:

# In[38]:


q1 = "Q, 20"
temp = bb.add_order(q1)
#this restore the log up to timestamp 20, which is the second add command to the JAY book

