import os
import json
from collections import defaultdict

# 定义文件路径
base_dir = r"c:\Users\15657\Desktop\大论文\实验阶段\数据处理--数据结构\代码"
dataset_dir = os.path.join(base_dir, 'DS-KG-Data-Small')
data_dir = os.path.join(dataset_dir, 'data')

all_samples = []

# 加载所有数据集文件
for split in ['train', 'dev', 'test']:
    filepath = os.path.join(data_dir, f'{split}.jsonl')
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            all_samples.append(json.loads(line))

total_samples = len(all_samples)
total_text_length = 0
total_entities = 0
total_relations = 0
entity_type_counts = defaultdict(int)
relation_type_counts = defaultdict(int)

for sample in all_samples:
    total_text_length += len(sample['text'])
    total_entities += len(sample['entities'])
    for entity in sample['entities']:
        entity_type_counts[entity['type']] += 1
    
    total_relations += len(sample['relations'])
    for relation in sample['relations']:
        relation_type_counts[relation['relation']] += 1

promedio_text_length = total_text_length / total_samples if total_samples > 0 else 0

print(f"总样本数: {total_samples}")
print(f"平均文本长度 (字符数): {promedio_text_length:.2f}")
print(f"实体总数: {total_entities}")
print(f"关系三元组总数: {total_relations}")
print(f"实体类型数: {len(entity_type_counts)}")
print(f"关系类型数: {len(relation_type_counts)}")

print("\n实体类型分布:")
for etype, count in entity_type_counts.items():
    print(f"- {etype}: {count} ({count/total_entities:.1%})")

print("\n关系类型分布:")
for rtype, count in relation_type_counts.items():
    print(f"- {rtype}: {count} ({count/total_relations:.1%})")
