import zipfile
from xml.etree.ElementTree import Element, SubElement, ElementTree


def test_create_xml_and_zip(tmp_path):
    data = {
        "title": "Chat",
        "messages": [
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "ok"},
        ],
        "uploaded_files_metadata": [{"name": "f.pdf", "type": ".pdf"}],
    }

    xsd = """<?xml version=\"1.0\"?>
    <xs:schema xmlns:xs=\"http://www.w3.org/2001/XMLSchema\">
       <xs:element name=\"conversation\">
          <xs:complexType>
             <xs:sequence>
                <xs:element name=\"title\" type=\"xs:string\"/>
                <xs:element name=\"messages\">
                   <xs:complexType>
                      <xs:sequence>
                         <xs:element name=\"message\" maxOccurs=\"unbounded\">
                           <xs:complexType>
                              <xs:simpleContent>
                                 <xs:extension base=\"xs:string\">
                                   <xs:attribute name=\"role\" type=\"xs:string\" use=\"required\"/>
                                 </xs:extension>
                              </xs:simpleContent>
                           </xs:complexType>
                         </xs:element>
                      </xs:sequence>
                   </xs:complexType>
                </xs:element>
                <xs:element name=\"uploaded_files\">
                   <xs:complexType>
                     <xs:sequence>
                       <xs:element name=\"file\" maxOccurs=\"unbounded\">
                         <xs:complexType>
                           <xs:attribute name=\"name\" type=\"xs:string\" use=\"required\"/>
                           <xs:attribute name=\"type\" type=\"xs:string\" use=\"required\"/>
                         </xs:complexType>
                       </xs:element>
                     </xs:sequence>
                   </xs:complexType>
                </xs:element>
             </xs:sequence>
          </xs:complexType>
       </xs:element>
    </xs:schema>
    """
    xsd_file = tmp_path / "schema.xsd"
    xsd_file.write_text(xsd, encoding="utf-8")

    conv = Element("conversation")
    title = SubElement(conv, "title")
    title.text = data["title"]

    messages_elem = SubElement(conv, "messages")
    for msg in data["messages"]:
        m = SubElement(messages_elem, "message", role=msg["role"])
        m.text = msg["content"]

    uploaded = SubElement(conv, "uploaded_files")
    for f in data["uploaded_files_metadata"]:
        SubElement(uploaded, "file", name=f["name"], type=f["type"])

    xml_file = tmp_path / "conversation.xml"
    ElementTree(conv).write(xml_file, encoding="utf-8", xml_declaration=True)

    zip_path = tmp_path / "xml.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.write(xml_file, arcname=xml_file.name)

    assert zip_path.exists()
