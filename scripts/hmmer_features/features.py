import xml.etree.ElementTree as ET
import json
import sys

data = ""

file_path = sys.argv[1]

with open(file_path, "r") as json_file:
    data = json.load(json_file)


if data["status"] != "SUCCESS":
    raise ValueError

results = data["result"]

stats = results["stats"]

hits = results["hits"]

factual_hits = []

for hit in hits:
    if hit["is_included"] and hit["is_reported"]:
        factual_hits.append(hit)


if not factual_hits:
    raise ValueError


lenght_of_protein_sequence = data["result"]["hits"][0]["domains"][0][
    "alignment_display"
]["l"]
scaled_len_protein = lenght_of_protein_sequence / 2
size_of_svg = scaled_len_protein + 2


svg = ET.Element(
    "svg",
    width=f"{size_of_svg}",
    height="20",
    viewBox=f"0 0 {size_of_svg} 20",
    style=f"width: {size_of_svg * 2}px; height: 40px",
    xmlns="http://www.w3.org/2000/svg",
)

defs = ET.SubElement(svg, "defs")

seq_rect = ET.SubElement(svg, "g", transform="translate(0 10)")

ET.SubElement(
    seq_rect,
    "rect",
    x="0",
    y="-2.5",
    width=f"{scaled_len_protein}",
    height="5",
    fill="#d8d8d8",
    rx="2.5",
    ry="2.5",
)

factual_domains = []

jagged_end_right = "h5l-2.5,2.5l2.5,2.5l-2.5,2.5l2.5,2.5h-5"
jagged_end_left = "h-5l2.5,-2.5l-2.5,-2.5l2.5,-2.5l-2.5,-2.5h5"

straight_end_left = "5v10h-5h"
straight_end_right = "-5v-10h5z"

round_end_left = "A5,5,0,0,1,130.5,10h"  # 130.5 je samo širina domene + 5
round_end_right = "A5,5,0,0,1,5,0"


for hit in factual_hits:
    for i, domain in enumerate(hit["domains"]):
        if domain["is_reported"] and domain["is_included"]:
            factual_domains.append(domain)

            ienv = domain["ienv"] / 2
            iali = domain["iali"] / 2
            jali = domain["jali"] / 2
            jenv = domain["jenv"] / 2

            mask = ET.SubElement(
                defs,
                "mask",
                id=f"{domain['alignment_display']['hmmacc']}_{i}",
                width=f"{jenv - ienv}",
                height="10",
                fill="#fff",
            )

            for x, width, opacity in [
                (0, iali - ienv, 0.6),
                (iali - ienv, jali - iali, 1),
                (jali - ienv, jenv - jali, 0.6),
            ]:
                ET.SubElement(
                    mask,
                    "rect",
                    x=str(x),
                    y="0",
                    width=str(width),
                    height="10",
                    opacity=str(opacity),
                )

            domain_len = ienv
            g = ET.SubElement(
                svg,
                "g",
                transform=f"translate({domain_len}, 5)",
                dataentity=domain["alignment_display"]["hmmacc"],
            )

            path = ET.SubElement(
                g,
                "path",
                d=f"m5,0h{(jenv - ienv) - 10}h{straight_end_left}{-((jenv - ienv) - 10)}h{straight_end_right}",
                fill=hit["metadata"]["color"],
                mask=f"url(#{domain['alignment_display']['hmmacc']}_{i})",
            )
            text_attributes = {
                "x": f"{(jenv - ienv) / 2}",
                "y": "8",
                "text-anchor": "middle",
                "font-size": "7.5",
                "fill": "white",
                "opacity": "1",
                "data-maxwidth": "61",
                "font-family": "Monospace",
            }
            domain_name = hit["metadata"]["identifier"]

            text_element = ET.SubElement(g, "text", attrib=text_attributes)
            text_element.text = domain_name


print(len(factual_domains))


ET.indent(svg, space="    ", level=0)
tree = ET.ElementTree(svg)

tree.write(sys.argv[2], encoding="utf-8", xml_declaration=False)
