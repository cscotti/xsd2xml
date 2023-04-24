#!/usr/bin/python3.10

# pip3 install xmlschema

from argparse import ArgumentParser
import xmlschema
from xmlschema import (
    XsdElement,
)

from xmlschema.validators import (
    XsdAnyElement,
    XsdComplexType,
    XsdAtomicBuiltin,
    XsdSimpleType,
    XsdList,
    XsdUnion,
    XsdGroup
)

# sample data is hardcoded
def valsmap(v):
    # numeric types
    v['decimal']    = '-3.72'
    v['float']      = '-42.217E11'
    v['double']     = '+24.3e-3'
    v['integer']    = '-176'
    v['positiveInteger'] = '+3'
    v['negativeInteger'] = '-7'
    v['nonPositiveInteger'] = '-34'
    v['nonNegativeInteger'] = '35'
    v['long'] = '567'
    v['int'] = '109'
    v['short'] = '4'
    v['byte'] = '2'
    v['unsignedLong'] = '94'
    v['unsignedInt'] = '96'
    v['unsignedShort'] = '24'
    v['unsignedByte'] = '17'
    # time/duration types
    v['dateTime'] = '2004-04-12T13:20:00-05:00'
    v['date'] = '2004-04-12'
    v['gYearMonth'] = '2004-04'
    v['gYear'] = '2004'
    v['duration'] = 'P2Y6M5DT12H35M30S'
    v['dayTimeDuration'] = 'P1DT2H'
    v['yearMonthDuration'] = 'P2Y6M'
    v['gMonthDay'] = '--04-12'
    v['gDay'] = '---02'
    v['gMonth'] = '--04'
    # string types
    v['string'] = 'lol'
    v['normalizedString'] = 'The cure for boredom is curiosity.'
    v['token'] = 'There is no cure for curiosity.'
    v['language'] = 'en-US'
    v['NMTOKEN'] = 'A_BCD'
    v['NMTOKENS'] = 'ABCD 123'
    v['Name'] = 'myElement'
    v['NCName'] = '_my.Element'
    # magic types
    v['ID'] = 'IdID'
    v['IDREFS'] = 'IDrefs'
    v['ENTITY'] = 'prod557'
    v['ENTITIES'] = 'prod557 prod563'
    # oldball types
    v['QName'] = 'pre:myElement'
    v['boolean'] = 'true'
    v['hexBinary'] = '0FB8'
    v['base64Binary'] = '0fb8'
    v['anyURI'] = 'http://miaozn.github.io/misc'
    v['notation'] = 'asd'



class GenXML:
    def __init__(self, xsd, elem, enable_choice):
        self.xsd = xmlschema.XMLSchema(xsd)
        self.elem = elem
        self.enable_choice = enable_choice
        self.root = True
        self.vals = {}
    
    # shorten the namespace
    def short_ns(self, ns):
        for k, v in self.xsd.namespaces.items():
            if k == '':
                continue
            if v == ns:
                return k
        return ''
    
    # if name is using long namespace,
    # lets replace it with the short one
    def use_short_ns(self, name):
        if name[0] == '{':
            x = name.find('}')
            ns = name[1:x]
            short_ns=self.short_ns(ns)
            if short_ns =='':
                temp= name[x + 1:]
            else:
                temp= + ":" + name[x + 1:]
            return temp
        return name
    
    
    # remove the namespace in name
    def remove_ns(self, name):
        if name[0] == '{':
            x = name.find('}')
            return name[x + 1:]
        return name

    # header of xml doc
    def print_header(self):
        print("<?xml version=\"1.0\" encoding=\"UTF-8\" ?>")

    
    # put all defined namespaces as a string
    def ns_map_str(self):
        ns_all = ''
        for k, v in self.xsd.namespaces.items():
            if k == '':
                self.element_xmlns=v
                continue
            else:
                ns_all += 'xmlns:' + k + '=\"' + v + '\"' + ' '
        return ns_all
        

    # start a tag with name
    def start_tag(self, name):
        x = '<' + name
        if self.root:
            self.root = False
            ns_list=self.ns_map_str()
            if self.element_xmlns:
                x += " xmlns=\""+ self.element_xmlns + "\""
            else:
                x += ' ' + ns_list
        x += '>'
        return x


    # end a tag with name
    def end_tag(self, name):
        return '</' + name + '>'
    
        
    # make a sample data for primitive types
    def genval(self, name):
        name = self.remove_ns(name)
        if name in self.vals:
            return self.vals[name]
        return 'ERROR !'
    
    
    # print a group
    def group2xml(self, g):
        model = str(g.model)
        model = self.remove_ns(model)
        nextg = g._group
        y = len(nextg)
        if y == 0:
            print('<!--empty-->')
            return
    
        print('<!--START:[' + model + ']-->')
        if self.enable_choice and model == 'choice':
            print('<!--next item is from a [choice] group with size=' + str(y) + '-->')
        else:
            print('<!--next ' + str(y) + ' items are in a [' + model + '] group-->')
            
        for ng in nextg:
            if isinstance(ng, XsdElement):
                self.node2xml(ng)
            elif isinstance(ng, XsdAnyElement):
                self.node2xml(ng)
            else:
                self.group2xml(ng)
        
            if self.enable_choice and model == 'choice':
                break
        print('<!--END:[' + model + ']-->')
    
    
    # print a node
    def node2xml(self, node):
        if hasattr(node, "minOccurs") and node.minOccurs == 0:
            print('<!--next 1 item is optional (minOcuurs = 0)-->')
        if hasattr(node, "maxOccurs") and node.maxOccurs >  1:
            print('<!--next 1 item is multiple (maxOccurs > 1)-->')
        
        if isinstance(node, XsdAnyElement):
            print('<_ANY_/>')
            return

        if isinstance(node.type, XsdComplexType):
            n = self.use_short_ns(node.name)
            if node.type.is_simple():
                print('<!--simple content-->')
                tp = str(node.type.content)
                print(self.start_tag(n) + self.genval(tp) + self.end_tag(n))
            else:
                print('<!--complex content-->')
                if isinstance(node.type.content, XsdGroup):
                    print(self.start_tag(n))
                    self.group2xml(node.type.content)
                    print(self.end_tag(n))
                else:
                    # XsdAtomicBuiltin
                    node1 = node.type.content
                    n = self.use_short_ns(node1.name)
                    tp = str(node1.name)
                    # print(self.start_tag(n) + self.genval(tp) + self.end_tag(n))
                    
        elif isinstance(node.type, XsdAtomicBuiltin):
            n = self.use_short_ns(node.name)
            tp = str(node.type)
            print(self.start_tag(n) + self.genval(tp) + self.end_tag(n))
        elif isinstance(node.type, XsdSimpleType):
            n = self.use_short_ns(node.name)
            if isinstance(node.type, XsdList):
                print('<!--simpletype: list-->')
                tp = str(node.type.item_type)
                print(self.start_tag(n) + self.genval(tp) + self.end_tag(n))
            elif isinstance(node.type, XsdUnion):
                print('<!--simpletype: union.-->')
                print('<!--default: using the 1st type-->')
                tp = str(node.type.member_types[0].base_type)
                print(self.start_tag(n) + self.genval(tp) + self.end_tag(n))
            # else:
            #     tp = str(node.type.base_type)
            #     print(self.start_tag(n) + self.genval(tp) + self.end_tag(n))
        else:
            print('ERROR: unknown type: ' + node.type)
    
    
    # setup and print everything
    def run(self):
        valsmap(self.vals)
        self.print_header()

        self.node2xml(self.xsd.elements[self.elem])
        # without_ns_elem=self.xsd.elements[self.elem]
        # # remove namespace
        # if hasattr(without_ns_elem.tag, 'find'):
        #     # remove namespace
        #     i = without_ns_elem.tag.find('}')
        #     if i >= 0:
        #         without_ns_elem.tag = without_ns_elem.tag[i+1:]
        #         self.node2xml(self.xsd.elements[without_ns_elem])
        # else:
        #     self.node2xml(self.xsd.elements[self.elem])



##############


def main():
    DEBUG=False
    if DEBUG ==True:
      
        generator = GenXML("test.xsd", "root", False)
    else:

        parser = ArgumentParser()
        parser.add_argument("-s", "--schema", dest="xsdfile", required=True, 
                            help="select the xsd used to generate xml")
        parser.add_argument("-e", "--element", dest="element", required=True,
                            help="select an element to dump xml")
        parser.add_argument("-c", "--choice",
                            action="store_true", dest="enable_choice", default=False,
                            help="enable the <choice> mode")
        args = parser.parse_args()

        generator = GenXML(args.xsdfile, args.element, args.enable_choice)
    generator.run()



if __name__ == "__main__":
    main()
    
    
