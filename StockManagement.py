from datetime import datetime
import pygal
import smtplib
from email.message import EmailMessage
import re
class Stock:
    """This class keeps a warehouse stock"""
    tot_categ = 0
    tot_prod = 0
    categories = list()
    products = list()
    categ_prod = {}
    transaction_out = {}
    transaction_in = {}
    def __init__(self, prod, categ, um='Pie', balance=0):
        self.prod = prod  # default parameters remain at the end of the list
        self.categ = categ  # every instatiation will be created with the first 3 param.
        self.balance = balance  # The fourth param will be by default 0
        self.um = um
        self.i = {}  # each instantiation will have 3 dictionaries i->products in,e->products exit,d->dates
        self.e = {}
        self.d = {}
        self.f = {}   #...
        self.g = {}
        Stock.tot_prod += 1  # la fiecare instantiere se calculeaza numarul produselor si al categ
        Stock.products.append(prod)  # populam lista cu produse

        if categ not in Stock.categories:  # if there is no categories we will add it as a unique categ
            Stock.tot_categ += 1
            Stock.categories.append(categ)
            Stock.categ_prod[categ] = {prod}
        else:
            Stock.categ_prod[categ].add(prod)

    def tr_in(self, quant, data=datetime.now().strftime('%Y/%m/%d')):
        self.balance += quant # the balance is recalculated after each transaction
        if self.d.keys():  # every transaction have a date
            one_key = max(self.d.keys()) + 1
        else:
            one_key = 1
        self.i[one_key] = quant  # the values are inserted in the dictionaries with dates
        self.d[one_key] = data
        self.f[data] = quant
        Stock.transaction_in[self.prod] = self.f
    def tr_out(self, quant, data=datetime.now().strftime('%Y/%m/%d')):
        self.balance -= quant
        if self.d.keys():
            one_key = max(self.d.keys()) + 1
        else:
            one_key = 1
        self.e[one_key] = quant  # same with the previous method but with the transactions out
        self.d[one_key] = data
        self.g[data] = quant
        Stock.transaction_out[self.prod] = self.g
    def prod_sheet(self):

        print('Product sheet ' + self.prod + ': ' + self.um)
        print('----------------------------')
        print(' Nrc ', '  Date ', 'Entries', 'Outputs')
        print('----------------------------')
        for v in self.d.keys():
            if v in self.i.keys():
                print(str(v).rjust(5), self.d[v], str(self.i[v]).rjust(6), str(0).rjust(6))
            else:
                print(str(v).rjust(5), self.d[v], str(0).rjust(6), str(self.e[v]).rjust(6))
        print('----------------------------')
        print('Current Stock       ' + str(self.balance).rjust(10))
        print('----------------------------\n')

    def generate_charts(self,prod):
        """Generates charts related to the user input date"""
        entry_dates_list = [x for x in prod.f.keys()]
        #creates the list with all entry dates from the self.f dictionary
        user_date = input('Insert the date until you want to see the charts as "YYYY/MM/DD"')
        final_entries_list = []  # a list which contains all the dates with the last date the user_date
        for i in entry_dates_list:
            if i <= str(user_date):
                final_entries_list.append(i)
        ox1_dates_list = [datetime.strptime(x, '%Y/%m/%d') for x in final_entries_list]
        #transforms list elements in  datetime elements to be used on the OX axis of the graphs
        out_dates_list = [x for x in prod.g.keys()]
        # creates the list with all outputs dates from the self.g dictionary
        final_outputs_list = []
        for i in out_dates_list:
            if i <= str(user_date):
                final_outputs_list.append(i)
        ox2_dates_list = [datetime.strptime(x, '%Y/%m/%d') for x in final_outputs_list]
        mvals = [x for x in ox1_dates_list]  # cretes points on OX axis
        interm_list_1=list(prod.i.values())
        oy1_use_list=interm_list_1[0:len(ox1_dates_list)]
        # the list which contains the oy coords has the same elements lenght with the dates list used on OX axis
        nvals = [x for x in oy1_use_list]  # creates points on OY axis
        kvals = [x for x in ox2_dates_list]
        interm_list_2=list(prod.e.values())
        oy2_use_list=interm_list_2[0:len(ox2_dates_list)]
        jvals = [x for x in oy2_use_list]
        coords_1 = [(mval, nval) for mval, nval in zip(mvals, nvals)]
        #generates a list with 2 elements tuples, each tuple represents the point coordinates on the graph
        coords_2 = [(kval, jval) for kval, jval in zip(kvals, jvals)]
        ox_elements=ox1_dates_list+ox2_dates_list
        xyplot = pygal.DateTimeLine(height=500, x_label_rotation=45, x_title='Data', y_title='Quantity [{0}]'.format(self.um))
        xyplot.title = 'Stock management'
        xyplot.add('Entries {0}'.format(prod.prod), coords_1)
        xyplot.add('Outputs {0}'.format(prod.prod), coords_2)
        xyplot.x_labels=[x for x in ox_elements]
        xyplot.render_to_file(f'{input("Insert a name for the file")}.svg')
        print('The charts have been created, check your working folder PycharmProjects')

    def send_info_inmail(self):
        """Method which sends an email on a google account with informations about the products"""
        user_request = input('Insert one of the following options in order to receive the info on email:\n'
                                  '1-Display products list on stock\n'
                                  '2-Display current stock of the requested product\n'
                                  '3-Display the entry and out dates dictionary\n'
                                  '4-Display the date and quantity of the last entries/outputs')
        if user_request == '1':
            msg = EmailMessage()
            msg.set_content(f'Available products list : \n'
                            f'{Stock.products}')
            msg['Subject'] = 'Info products'
            msg['From'] = input("Insert your gmail address from which the email will be sent:")
            msg['To'] = input("Insert the gmail destination address:")
            username=input('Insert your gmail address')
            password = input('Insert your gmail account password:')
            '''this password is a special password generated by gmail after you give the permission to use applications
            from outside like python.This feature must be set from your google account settings'''
            try:
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.login(username, password)
                server.send_message(msg)
                server.quit()
                print('Message sent successfully!')
            except:
                print('The message could not be sent!')

        elif user_request == '2':
            msg = EmailMessage()
            msg.set_content(f'{self.prod} stock is {self.balance} {self.um}')
            msg['Subject'] = f'Product info-{self.prod}'
            msg['From'] = input("Insert your gmail address from which the email will be sent:")
            msg['To'] = input("Insert the gmail destination address:")
            username = input('Insert your gmail address')
            password = input('Insert your gmail account password:')
            try:
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.login(username, password)
                server.send_message(msg)
                server.quit()
                print('Message sent successfully!')
            except:
                print('The message could not be sent!')
        elif user_request == '3':
            msg = EmailMessage()
            msg.set_content(f'''Entries dictionary Date:Quantity {self.um}->
                                {self.f}

                    Outputs dictionary Date:Quantity {self.um}-> 
                                    {self.g}''')
            msg['Subject'] = f'Product info-{self.prod}'
            msg['From'] = input("Insert your gmail address from which the email will be sent:")
            msg['To'] = input("Insert the gmail destination address:")
            username = input('Insert your gmail address')
            password = input('Insert your gmail account password:')
            try:
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.login(username, password)
                server.send_message(msg)
                server.quit()
                print('Message sent successfully!')
            except:
                print('The message could not be sent!')
        elif user_request == '4':
            msg = EmailMessage()
            msg.set_content(f'''The last entry was made on {list(self.f.keys())[-1]} ,
quantity entered-> {list(self.f.values())[-1]}, 
The last output was made on {list(self.g.keys())[-1]},
output quantity-> {list(self.g.values())[-1]}''')
            msg['Subject'] = f'Product info-{self.prod}'
            msg['From'] = input("Insert your gmail address from which the email will be sent:")
            msg['To'] = input("Insert the gmail destination address:")
            username = input('Insert your gmail address')
            password = input('Insert your gmail account password:')
            try:
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.login(username, password)
                server.send_message(msg)
                server.quit()
                print('Message sent successfully!')
            except:
                print('The message could not be sent!')

    def product_search(self):
        """This method uses regex to search a if a product is on stock or not"""
        while True:
            user_word = input('Insert product full name or a few letters from it: ')
            r = re.compile(f".*{user_word}")
            newlist = list(filter(r.match, Stock.products))
            if len(newlist) > 0:
                print(f'On stock there are the following products : {newlist}')
                option1 = input('Looking for another product? Type Yes or No')
                if option1.lower() == 'yes':
                    continue
                elif option1.lower() == 'no':
                    print('You are out of search mode')
                    break
            else:
                print('The product you are looking for is not on our stock'.upper())
                option2 = input('You can resume the search by typing "again" or you can exit by typing "ready"')
                if option2.lower() == 'ready':
                    print('You are out of search mode')
                    break
                elif option2.lower() == 'again':
                    continue
                else:
                    print('The selected option does not exist')
                    break

    def search_transaction(self):
        """This method search the entries and the outputs of a product requested by the user"""
        while True:
            searched_transaction = input('Enter the number corresponding to the variants below: \n'
                                       '1-Search for inbound transactions\n'
                                       '2-Search for output transactions')
            if searched_transaction == '1':
                product_insert = input('Enter the product for which you want to see the transactions:')

                r = re.compile(f"^{product_insert}$")
                newlist = list(filter(r.match, Stock.transaction_in.keys()))
                for i in Stock.transaction_in.keys():
                    if i in newlist:
                        print(f"'Date':Quant {Stock.transaction_in[i]}")
                break
            elif searched_transaction == '2':
                product_insert = input('Enter the product for which you want to see the transactions:')

                r = re.compile(f"^{product_insert}$")
                newlist = list(filter(r.match, Stock.transaction_out.keys()))
                for i in Stock.transaction_out.keys():
                    if i in newlist:
                        print(f"'Date':Quant {Stock.transaction_out[i]}")
                break
            else:
                print('You entered a wrong number')
                continue

    def set_discount(self):
        """Method which set a discount for a product in case it will be sold related to its price"""
        initial_price = int(input(f'Insert the price per {self.um} in $'))
        while True:
            desired_quantity = int(input(f'Enter the quantity you want to buy in {self.um}'))
            if desired_quantity > self.balance:
                print(f'The desired quantity is not in stock, you can buy maximum {self.balance} {self.um}')
                continue
            else:
                if initial_price < 10 and desired_quantity < 50:
                    discount = 0
                elif initial_price < 10 and desired_quantity >= 50:
                    discount = 0.15
                elif initial_price >= 10 and desired_quantity < 50:
                    discount = 0.1
                elif initial_price >= 10 and desired_quantity >= 50:
                    discount = 0.25
                final_price = (initial_price * desired_quantity) - (initial_price * desired_quantity * discount)
                print(f'The amount to be paid is: {final_price} $,applied discount {discount * 100} % ')
                break

    def infofile_creation(self):
        """Method which creates a text file with different informations about a product"""
        text = open(f"{self.prod}.txt", "w")
        text.write(f'''On {datetime.today().now()}, the product  {self.prod} has the following specifications:

Supplies No:->{len(list(self.i.values()))}
Sales No: ->{len(list(self.e.values()))}

Quantity in stock:-> {self.balance} {self.um}

The first supply was made on:->{list(self.f.keys())[0]},quantity entered-> {list(self.f.values())[0]} {self.um}
The last supply was made on:->{list(self.f.keys())[-1]},quantity entered-> {list(self.f.values())[-1]} {self.um}
The biggest supply was:->{max(list(self.f.values()))} {self.um}

The first sale was made on:->{list(self.g.keys())[0]},quantity sold:->{list(self.g.values())[0]} {self.um}
The last sale was made on:->{list(self.g.keys())[-1]},quantity sold:->{list(self.g.values())[-1]} {self.um}
The biggest sale was :->{max(list(self.g.values()))} {self.um}

The total amount supplied:->{sum(list(self.i.values()))}
The total amount sold:->{sum(list(self.e.values()))}

Percentage of quantity sold depending on quantity supplied :->
{sum(list(self.e.values())) / sum(list(self.i.values())) * 100} %

If the products remain in stock, to cover losses, the price of the product "{self.prod}" 
will have to increase with the difference up to 100% of the percentage calculated previously''')

        text.close()
        print(f'Your file {self.prod}.txt was created successfully, check your work folder "PycharmProjects"')



#instantiation of three products for the fruit category
apples=Stock('apples','fruits','kg')
pears=Stock('pears','fruits','kg')
bananas=Stock('bananas','fruits','kg')

#instantiation of three products for the vegetables category
tomatoes=Stock('tomatoes','vegetables','kg')
cucumbers=Stock('cucumbers','vegetables','kg')
peppers=Stock('peppers','vegetables','kg')

#instantiation of three products for the dairy category
cheese=Stock('cheese','dairy','kg')
milk=Stock('milk','dairy','liters')
yogurt=Stock('yogurt','dairy','liters')

# inputs and outputs for each product in the fruit category
apples.tr_in(100,'2019/01/15')
apples.tr_in(70,'2019/01/30')
apples.tr_out(40,'2019/01/22')
apples.tr_in(50,'2019/03/12')
apples.tr_out(45,'2019/02/18')
apples.tr_in(77,'2019/03/29')
apples.tr_out(60,'2019/03/30')
apples.tr_in(83,'2019/05/15')
apples.tr_out(77,'2019/05/21')
apples.tr_in(25,'2019/06/14')
apples.tr_out(30,'2019/06/23')
apples.tr_in(80,'2019/07/15')
apples.tr_out(55,'2019/07/29')
apples.tr_in(80,'2019/08/22')
apples.tr_out(70,'2019/09/01')
apples.tr_in(120,'2019/09/23')
apples.tr_out(70,'2019/10/03')
apples.tr_in(30,'2019/11/27')
apples.tr_out(77,'2019/11/08')
apples.tr_in(34,'2019/12/04')
apples.tr_out(44,'2019/12/15')
apples.tr_in(89,'2019/12/31')

pears.tr_in(88,'2019/02/12')
pears.tr_out(23,'2019/02/18')
pears.tr_in(35,'2019/03/01')
pears.tr_out(37,'2019/02/28')
pears.tr_in(55,'2019/04/19')
pears.tr_out(60,'2019/04/15')
pears.tr_in(70,'2019/04/30')
pears.tr_out(50,'2019/05/15')
pears.tr_in(45,'2019/05/23')
pears.tr_out(33,'2019/06/10')
pears.tr_in(75,'2019/07/15')
pears.tr_out(99,'2019/07/28')
pears.tr_in(100,'2019/08/15')
pears.tr_out(79,'2019/08/29')
pears.tr_in(57,'2019/09/15')
pears.tr_out(49,'2019/09/25')
pears.tr_in(67,'2019/10/12')
pears.tr_out(89,'2019/10/22')
pears.tr_in(22,'2019/12/07')
pears.tr_out(19,'2019/12/22')

bananas.tr_in(77,'2019/01/22')
bananas.tr_out(55,'2019/01/29')
bananas.tr_in(66,'2019/02/17')
bananas.tr_out(45,'2019/02/26')
bananas.tr_in(23,'2019/03/18')
bananas.tr_out(55,'2019/03/29')
bananas.tr_in(12,'2019/05/04')
bananas.tr_out(47,'2019/05/17')
bananas.tr_in(89,'2019/06/17')
bananas.tr_out(23,'2019/06/25')
bananas.tr_in(67,'2019/07/04')
bananas.tr_out(44,'2019/07/18')
bananas.tr_in(37,'2019/08/19')
bananas.tr_out(78,'2019/08/26')
bananas.tr_in(69,'2019/09/12')
bananas.tr_out(45,'2019/10/03')
bananas.tr_in(63,'2019/10/28')
bananas.tr_out(59,'2019/11/04')
bananas.tr_in(40,'2019/12/09')
bananas.tr_out(33,'2019/12/27')

# inputs and outputs for each product in the vegetables category
tomatoes.tr_in(30,'2019/01/05')
tomatoes.tr_out(45,'2019/01/22')
tomatoes.tr_in(22,'2019/02/14')
tomatoes.tr_out(15,'2019/03/17')
tomatoes.tr_in(70,'2019/06/18')
tomatoes.tr_out(55,'2019/07/28')
tomatoes.tr_in(78,'2019/10/12')
tomatoes.tr_out(66,'2019/11/14')
tomatoes.tr_in(34,'2019/11/29')
tomatoes.tr_out(22,'2019/12/31')

cucumbers.tr_in(30,'2019/01/15')
cucumbers.tr_in(20,'2019/01/30')
cucumbers.tr_out(35,'2019/02/12')
cucumbers.tr_out(15,'2019/02/28')
cucumbers.tr_in(50,'2019/03/22')
cucumbers.tr_out(40,'2019/04/14')
cucumbers.tr_in(12,'2019/07/15')
cucumbers.tr_out(2,'2019/09/15')
cucumbers.tr_in(15,'2019/11/12')
cucumbers.tr_out(21,'2019/12/13')

peppers.tr_in(12,'2019/02/12')
peppers.tr_out(9,'2019/03/15')
peppers.tr_in(19,'2019/04/15')
peppers.tr_out(22,'2019/05/15')
peppers.tr_in(17,'2019/06/12')
peppers.tr_out(18,'2019/07/21')
peppers.tr_in(15,'2019/09/12')
peppers.tr_out(14,'2019/10/21')
peppers.tr_in(22,'2019/11/28')
peppers.tr_out(21,'2019/12/15')
peppers.tr_out(5,'2019/10/15')

# inputs and outputs for each product in the dairy category
cheese.tr_in(40,'2019/02/15')
cheese.tr_out(10,'2019/03/15')
cheese.tr_out(20,'2019/04/15')
cheese.tr_out(5,'2019/04/29')
cheese.tr_in(12,'2019/03/18')

milk.tr_in(150,'2019/02/15')
milk.tr_out(78,'2019/01/22')
milk.tr_in(55,'2019/04/12')
milk.tr_out(49,'2019/07/12')
milk.tr_in(33,'2019/06/29')
milk.tr_out(78,'2019/08/22')

yogurt.tr_in(34,'2019/10/12')
yogurt.tr_in(33,'2019/02/18')
yogurt.tr_in(55,'2019/05/13')
yogurt.tr_out(23,'2019/11/15')
yogurt.tr_out(45,'2019/07/05')
yogurt.tr_out(34,'2019/03/22')

#testing generate charts method
apples.generate_charts(apples)
pears.generate_charts(pears)
bananas.generate_charts(bananas)
tomatoes.generate_charts(tomatoes)
cucumbers.generate_charts(cucumbers)
peppers.generate_charts(peppers)
cheese.generate_charts(cheese)
milk.generate_charts(milk)
yogurt.generate_charts(yogurt)

#testing method send info inmail
apples.send_info_inmail()
pears.send_info_inmail()
bananas.send_info_inmail()

#testing method product search and method search transaction
apples.product_search()  #no need to insert full name
apples.search_transaction() #need to insert full name

#testing method set discount
apples.set_discount()
pears.set_discount()
bananas.set_discount()

#testing method infofile creation
apples.infofile_creation()
pears.infofile_creation()
bananas.infofile_creation()
milk.infofile_creation()
