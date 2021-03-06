from bs4 import BeautifulSoup

class ProductSellersPageParser():
    Name = "ProductSellersPageParser"
    
    def __init__(self):
        
        # product offers info
        self.product_offers = []
        # true when the html has a next page
        self.has_next_page = False
        # true when the html was not correctly parsed
        self.blocked = False
    
    def feed(self, html):
        self.soup = BeautifulSoup(html)
        
        self.blocked = False
        
        if not self.soup.title:
            self.blocked = True
            return
        
        sellers_content_div = self.soup.find(id="ps-sellers-content")
        
        if sellers_content_div == None:
            if not self.soup.title or self.soup.title.get_text() != "302 Moved":
                print "Unknown page! Here's the html:\n"
                print html + "\n"
            self.blocked = True
            return
        
        rows = sellers_content_div.find_all("tr", { "class" : "online-sellers-row" })
        
        for row in rows:
            seller_name_spam = row.find_all("td", { "class" : "seller-col" })[0].find_all("span", { "class" : "seller-name" })[0]
            
            # setting the store name
            name = seller_name_spam.a.get_text()
            if name == "": name = None
            
            # setting the store url
            url = seller_name_spam.a["href"]
            url = url.split("url?q=")[1].split("&usg=")[0]
            if url == "":  url = None            
            
            # setting the store domain
            domain_div = row.find_all("td", { "class" : "rating-col" })[0].find_all("a", { "class" : "a" })
            
            if len(domain_div) > 0:
                has_page = True
                
                store_zmi = domain_div[0]["href"].split("zmi=")
                if len(store_zmi) > 1:
                    store_zmi = store_zmi[1].split("&q=")[0]
                else:
                    store_zmi = None
                    store_cmi = domain_div[0]["href"].split("cmi=")
                    if len(store_cmi) > 1:
                        store_cmi = store_cmi[1].split("&q=")[0]
                
                if store_zmi != None:
                    domain = store_zmi
                    domain_type = "zmi"
                else:
                    domain = store_cmi
                    domain_type = "cmi"
                    
            else:
                has_page = False
                if url != None:
                    domain = url.replace("http://", "").replace("https://", "").replace("www.", "").split("/")[0]
                    domain_type = "url"
                else:
                    domain = None
                    domain_type = None
            
            # setting the product condition
            condition = row.find_all("td", { "class" : "condition-col" })[0].find_all("span", { "class" : "f" })[0].get_text()
            if condition == "": condition = None            
            
            # setting the estimated tax and shipping for the offer"
            tax_shipping_spam = row.find_all("td", { "class" : "taxship-col" })[0].find_all("span", { "class" : "f" })
            
            if len(tax_shipping_spam) == 0:
                tax_shipping = None
            else:
                tax_shipping_nb = tax_shipping_spam[0].find_all("nobr")
                
                if len(tax_shipping_nb) > 0:
                    multiple_tax_shipping = []
                    for i in range(len(tax_shipping_nb)):
                        multiple_tax_shipping.append(tax_shipping_nb[i].get_text().strip())
                        tax_shipping = ','.join(multiple_tax_shipping)
                elif len(tax_shipping_spam[0].get_text().strip()) > 0:
                    tax_shipping = tax_shipping_spam[0].get_text().strip()
                else:
                    tax_shipping = None
            
            # setting the product total price
            total_price_spam = row.find_all("td", { "class" : "total-col" })[0].find_all("span", { "class" : "f" })
            
            if len(total_price_spam) == 0:
                total_price = None
            else:
                total_price = total_price_spam[0].get_text().strip()[1:].replace(",", "")
                if total_price == "": total_price = None
                
            # setting the product base price
            base_price_spam = row.find_all("td", { "class" : "price-col" })[0].find_all("span", { "class" : "base-price" })
            
            if len(base_price_spam) == 0:
                base_price = None
            else:
                base_price = base_price_spam[0].get_text().strip()[1:].replace(",", "")
                if base_price == "": base_price = None
            
            self.product_offers.append({ "seller_name" : name,
                                         "seller_domain" : domain,
                                         "seller_domain_type" : domain_type,
                                         "offer_url" : url,
                                         "offer_condition" : condition,
                                         "offer_tax_shipping" : tax_shipping,
                                         "offer_total_price" : total_price,
                                         "offer_base_price" : base_price
                                       })
        
        # setting the has_next_page value
        pagination_div = self.soup.find(id="online_stores_pagination")
        
        if pagination_div != None: 
            current_page = pagination_div.find(id="n-to-n-start").get_text().strip()
            current_page = current_page.split(" of ")
        
            if len(current_page) > 0:
                if current_page[0].split(" - ")[1] < current_page[1]:
                    self.has_next_page = True
    
    def get_product_offers(self):
        return self.product_offers
    
    def crawled(self):
        return not self.blocked