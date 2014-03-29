# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import re

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Analyze_HTML(object):
    """
    Analyzes HTML
    requires LXML
    """
    
    def __init__(self):
        
        self.match_comments = re.compile(r'(<!--.*-->)')


    def set_html(self, HTML):
        self.soup = BeautifulSoup(HTML, "lxml")
    
    def get_html(self):
        return self.soup.encode(formatter=None).decode('utf-8')

    def extract_text_from_soup(self):
        self.texts = self.soup.findAll(text=True)
        return self.texts

    def find_tag(self, tag):
        return self.soup.findAll(tag)

    def find_tag_with_attr_that_matches(self, tag, attr, the_match):
        """
        Finds all instances of a tag with attribute that matches the_match
        example:
        finds all img 'tags' that the 'src' attribute matches "the_match" re object 
        
        analyze_html.find_tag_with_attr_that_matches(tag='img', attr='src', the_match=match_urls)
        """
        elements = self.find_tag(tag)
        return [el for el in elements if the_match.match(el[attr])]


    def find_img_sources_in_img_elements(self, elements):        
        return [el['src'] for el in elements]


    def find_all_img_sources(self):
        img_elements = self.find_tag('img')
        return self.find_img_sources_in_img_elements(img_elements)


    def remove_hyperlinked_element(self, element):
        """
        returns elements that are not in a hyperlink or img or ... tags
        so you can deal with elements that are ready to be modified and don't have any links or ...
        """
        if element.parent.name in ['style', 'script', '[document]', 'head', 'title','a','img']:
            return False
        #elif self.match_comments.search(str(element)):
        elif self.match_comments.search(element): 
            return False

        return True

    def get_texts_that_contains_no_links(self):
        self.extract_text_from_soup()
        self.texts_that_contains_no_links = filter(self.remove_hyperlinked_element, self.texts)
        return self.texts_that_contains_no_links


    def replace_element_with(self, element, find_it, target, count=0):
        """
        replaces the target_text in the element with target_link
        Make sure you again set_html after replacing elements throught the HTML since once you replace an element,
        you can't replace it again unless you parse the html again.
        Count: maximum number of times an item will be replaced. 0 means unlimited.
        """
        result=False

        
        if re.search(find_it, element):
            replacement = re.sub(find_it, target, element, count)
            #changing the actual element in the soup
            try:
                element.replace_with(replacement)
                result = True
            except:
                logger.error("caught:", exc_info=True)
                pass
        
        return result
    


