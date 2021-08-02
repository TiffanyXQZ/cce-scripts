import collections
import xml.etree.ElementTree as ET
from xml.etree import ElementTree

from rich import print

from pyecharts import options as opts
from pyecharts.charts import Tree

data = [
    {
        "children": [
            {"name": "B"},
            {
                "children": [{"children": [{"name": "I"}], "name": "E"}, {"name": "F"}],
                "name": "C",
            },
            {
                "children": [
                    {"children": [{"name": "J"}, {"name": "K"}], "name": "G"},
                    {"name": "H"},
                ],
                "name": "D",
            },
        ],
        "name": "FlowStats",
    }
]


# tree = ET.parse('../../../data/flow_monitor.xml')
# root = tree.getroot()
# data = {}


# def bfs(root):
#     q = collections.deque()
#     res = {'name':root.tag, 'children':[]}
#     q.append((root,res))
#
#     while q:
#         node, cur = q.popleft()
#         print(node, cur)
#         children = set()
#         print(cur)
#         for child in node: children.add((child.tag,child))
#         for tag, child in children:
#             print(cur)
#             cur['children'].append({'name': tag, 'children':[]})
#             q.append((tag, child))
#
#     return [res]
#
# print(bfs(root))

def tree_data(l):
    if len(l) == 0: return None
    mid = len(l) // 2
    children = []
    left, right = tree_data(l[0:mid]), tree_data(l[mid + 1:])
    if left: children.append(left)
    if right: children.append(right)

    return {'name': l[mid], 'children': children}


# print(tree_data([1,2,3,4,5]))

def tree_charts(data):
    c = (
        Tree()
            .add("", data)
            .set_global_opts(title_opts=opts.TitleOpts(title="Tree-基本示例"))
            .render("../../../data/tree_base.html")
    )


# tree_charts([tree_data([1, 2, 3, 4, 5, 6, 7])])

tree = ET.parse('../../../data/flow_monitor.xml')
root = tree.getroot()


def xml_tag_tree(root_xml: ElementTree) -> dict:
    '''

    :param root_xml: xml elementTree
    :return: root_tag: {'name': name, 'count':count, 'children':[]}
    '''
    root_tag, q = {'name': root_xml.tag,'count': 1}, collections.deque()
    q.append((root_tag, root_xml))
    while q:
        node_tag, node_xml = q.popleft()
        # build children for current node_tag while a dict then covert it to list
        children = {}
        for child_xml in node_xml:
            if child_xml.tag not in children:
                child_tag = {
                    'name': child_xml.tag,
                    'count': 1,
                    'attribute': child_xml.attrib,
                    'children': []
                }
                q.append((child_tag, child_xml))
                children[child_xml.tag] = child_tag
            else:
                children[child_xml.tag]['count'] += 1
        node_tag['children'] = list(children.values())
    return root_tag

tag_tree = xml_tag_tree(root)
print(tag_tree)
tree_charts([tag_tree])