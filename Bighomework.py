import pandas as pd
from pyvis.network import Network
import webbrowser

# 读取三元组数据
df = pd.read_csv('data/relation_utf8_clean.csv', header=None, names=['Subject', 'Relation', 'Object'])
# 读取人物名片数据
profile_data = pd.read_csv('data/attribute.csv', encoding='gbk')

# 计算节点权重，如果没有则默认为零
in_degree = df['Object'].value_counts()
out_degree = df['Subject'].value_counts()

# 读取节点频率和权重
node_weight = {}
word_freq_df = pd.read_csv('data/词频.csv', encoding='gbk')
for index, row in df.iterrows():
    subject = row['Subject']
    obj = row['Object']
    subject_weight = word_freq_df.loc[word_freq_df['姓名'] == subject, '权重']
    obj_weight = word_freq_df.loc[word_freq_df['姓名'] == obj, '权重']
    node_weight[subject] = in_degree.get(subject, 0) + subject_weight.iloc[0] if subject in in_degree and not subject_weight.empty else 0
    node_weight[obj] = out_degree.get(obj, 0) + obj_weight.iloc[0] if obj in out_degree and not obj_weight.empty else 0

# 创建网络图
net = Network(height="750px", width="100%", filter_menu=True)

# 添加节点和边
for index, row in df.iterrows():
    subject_profile = profile_data[profile_data['姓名'] == row['Subject']].squeeze()
    object_profile = profile_data[profile_data['姓名'] == row['Object']].squeeze()

    # 建立属性列表
    attributes_to_check = ['性别', '别名', '法宝', '兵器', '神通', '本相', '技能', '坐骑', '住所', '相关文本']

    # 循环检查每个属性是否在profile中存在
    subject_attributes = f"姓名: {row['Subject']}\n"
    for attribute in attributes_to_check:
        if attribute in subject_profile and pd.notna(subject_profile[attribute]):
            subject_attributes += f"{attribute}: {subject_profile[attribute]}\n"

    object_attributes = f"姓名: {row['Object']}\n"
    for attribute in attributes_to_check:
        if attribute in subject_profile and pd.notna(object_profile[attribute]):
            object_attributes += f"{attribute}: {object_profile[attribute]}\n"

    # 添加节点
    net.add_node(row['Subject'], label=row['Subject'], title=subject_attributes)

    # 添加目标节点和边
    net.add_node(row['Object'], label=row['Object'], title=object_attributes)
    net.add_edge(row['Subject'], row['Object'], title=row['Relation'], label=row['Relation'], arrows='to')

# 修改节点大小
for node in net.nodes:
    weight = node_weight.get(node['id'], 0)
    scaled_weight = weight / max(node_weight.values()) * 30 + 10  # 缩小权重范围到10-40
    node['size'] = scaled_weight


options = """
var options = {
   "configure": {
        "enabled": true
   }
}
"""

# 生成页面下方的控制面板
net.set_options(options)

# 可视化
net.show("knowledge_graph.html", notebook=False)

# 打开生成的 HTML 文件
'''无法自动在浏览器打开文件时，使用改行代码'''
# webbrowser.open("knowledge_graph.html")


