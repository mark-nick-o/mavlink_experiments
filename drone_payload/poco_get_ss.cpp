// This is a port of my boost library using poco so that a test can be made without loading boost on the other Pi.
// We can use this for setting the shutter-speed into a list from the DronePayloadMaanger until the boost libraries are loaded
// as the other version is more efficient
// Compiles with :: g++-8 -I/usr/local/include -L/usr/local/lib -lPocoFoundation -lPocoXML -std=c++17 xml5.cpp
//
#ifndef __get_ss_using_poco_
#define __get_ss_using_poco_

#include <string>
#include <iostream>
#include <sstream>
#include <Poco/AutoPtr.h>
#include "Poco/XML/XML.h"
#include "Poco/XML/XMLString.h"
#include "Poco/DOM/DOMParser.h"
#include "Poco/DOM/Document.h"
#include "Poco/DOM/NodeIterator.h"
#include "Poco/DOM/NodeFilter.h"
#include "Poco/DOM/NamedNodeMap.h"
/*
#include "Poco/SAX/ContentHandler.h"
#include "Poco/SAX/LexicalHandler.h"
#include "Poco/SAX/DTDHandler.h"
#include "Poco/SAX/NamespaceSupport.h"
*/
#include <Poco/Util/XMLConfiguration.h>
#include "Poco/XML/XMLString.h"
#include "Poco/XML/XMLStream.h"
#include "Poco/XML/Name.h"
#include "Poco/TextEncoding.h"
#include "Poco/StreamConverter.h"
#include <vector>
#include <map>
#include "Poco/Exception.h"
#include <Poco/RegularExpression.h>

#include "focus_adjustment.h"

using Poco::Exception;

std::vector<std::uint32_t> read_xml_value_for_tag(Poco::AutoPtr<Poco::XML::Document> doc, std::string ID) {
    std::uint32_t ret = 0;
    Poco::XML::NodeIterator it(doc, Poco::XML::NodeFilter::SHOW_ALL);

    Poco::XML::Node* a = it.nextNode();
    std::vector<std::uint32_t> vec;

    int collect1 = 0;
    int count_defaults = 0;

    Poco::RegularExpression found_value("value");
    Poco::RegularExpression found_end("default");

    // print the whole xml in case we need to use this
    while (a) {
        Poco::XML::NamedNodeMap* map1 = a->attributes();
        if (map1) {
            for (size_t i = 0; i < map1->length(); ++i) {
                Poco::XML::Node* attr = map1->item(i);
                std::cout << "-----nb----" << std::endl;
                std::cout << attr->nodeName() << std::endl;
                std::cout << attr->nodeValue() << std::endl;
                Poco::RegularExpression re(ID);
                Poco::RegularExpression::Match match;
                std::stringstream sssss;
                sssss << attr->nodeValue();

                std::string ss;
                if (0 != re.extract(sssss.str(), ss)) {
                    std::cout << "\033[31m extract" << ss << std::endl;
                    collect1 = 1;
                }
                else if (collect1 == 1) {

                    Poco::RegularExpression::Match match1;
                    match1.offset = 0;
                    sssss << attr->nodeName();
                    if (0 != found_value.extract(sssss.str(), ss)) {
                        std::cout << "\033[32m value" << ss << " " << collect1 << std::endl;
                        std::string v1 = attr->nodeValue();
                        ret = std::stoi(v1);
                        vec.push_back(ret);
                    }

                    sssss << attr->nodeName();
                    if (0 != found_end.extract(sssss.str(), ss)) {
                        count_defaults = ++count_defaults;
                        std::cout << "\033[33m end stop.... \033[0m" << ss << std::endl;
                        if (count_defaults >= 2) collect1 = 0;
                    }
                }
                std::cout << "-----ne----" << std::endl;
            }
        }
        std::cout << "-----b-----" << std::endl;
        std::cout << a->nodeName() << std::endl;
        std::cout << a->nodeValue() << std::endl;
        std::cout << "-----e-----" << std::endl;
        a = it.nextNode();
    }
    return vec;
}

std::uint32_t get_shutter_from_index_pl(std::vector<std::uint32_t> sss, sony_focus_settings_t* sfs) {
    sfs->use_sdk_shut = sfs->use_sdk_shut % sss.size();
    sfs->prev_sdk_shut = sfs->use_sdk_shut;
    return sss[sfs->use_sdk_shut];
}

void get_index_from_shutter_pl(std::vector<std::uint32_t> sss, sony_focus_settings_t* sfs, std::uint32_t request_val) {
    for (auto index : sss) {
        if (index == request_val) {
            sfs->use_sdk_shut = index;
            break;
        }
    }
}

std::uint32_t get_FNum_from_index_pl(std::vector<std::uint32_t> sss, sony_focus_settings_t* sfs) {
    sfs->use_sdk_fnum = sfs->use_sdk_fnum % sss.size();
    sfs->prev_sdk_fnum = sfs->use_sdk_fnum;
    return sss[sfs->use_sdk_fnum];
}

void get_index_from_FNum_pl(std::vector<std::uint32_t> sss, sony_focus_settings_t* sfs, std::uint32_t request_val) {
    for (auto index : sss) {
        if (index == request_val) {
            sfs->use_sdk_fnum = index;
            break;
        }
    }
}

std::uint32_t get_Iso_from_index_pl(std::vector<std::uint32_t> sss, sony_focus_settings_t* sfs) {
    sfs->use_sdk_iso = sfs->use_sdk_iso % sss.size();
    sfs->prev_sdk_iso = sfs->use_sdk_iso;
    return sss[sfs->use_sdk_iso];
}

void get_index_from_Iso_pl(std::vector<std::uint32_t> sss, sony_focus_settings_t* sfs, std::uint32_t request_val) {
    for (auto index : sss) {
        if (index == request_val) {
            sfs->use_sdk_iso = index;
            break;
        }
    }
}

// #define __test_ss_poco_
#ifdef __test_ss_poco_

int main(int argc, char* argv[]) {
    try {
        Poco::XML::DOMParser parser;
        // -----> parse the xml and read into the vector the values for shutter speed in the xml order <-----
        //
        Poco::AutoPtr<Poco::XML::Document> doc = parser.parse("/home/pi/cam_init/sony_new_xml.xml");

        std::string tag = "CAM_SHUTTERSPD";

        std::vector<std::uint32_t> vv = read_xml_value_for_tag(doc, tag);
        for (auto x : vv) {
            std::cout << "result : " << x << std::endl;
        }

        return 0;
    }
    catch (Exception& e) {
        std::cerr << e.displayText() << std::endl;
    }
}
#endif

#endif
