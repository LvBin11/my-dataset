import os
import json
import random
import re

# 定义文件路径
base_dir = r"c:\Users\15657\Desktop\大论文\实验阶段\数据处理--数据结构\代码"
entity_relation_file = os.path.join(base_dir, 'entity_relation.txt')
dataset_dir = os.path.join(base_dir, 'DS-KG-Data-Small')
data_dir = os.path.join(dataset_dir, 'data')
schema_dir = os.path.join(dataset_dir, 'schema')
scripts_dir = os.path.join(dataset_dir, 'scripts')

# --- 1. 读取 entity_relation.txt 并提取三元组 ---
triples = []
entities_set = set()
relations_set = set()

with open(entity_relation_file, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('/*') or line.startswith('[entity1]'):
            continue
        
        parts = line.split()
        if len(parts) >= 3:
            head, tail, relation = parts[0], parts[1], parts[2]
            if relation == '无关': # 过滤无关关系
                continue
            triples.append((head, relation, tail))
            entities_set.add(head)
            entities_set.add(tail)
            relations_set.add(relation)

unique_triples = list(set(triples))
random.shuffle(unique_triples)

print(f"从 {entity_relation_file} 中读取到 {len(unique_triples)} 个不重复的三元组。")
if len(unique_triples) > 5:
    print("前5个三元组:", unique_triples[:5])
else:
    print("所有三元组:", unique_triples)

# --- 2. 定义异构文本模板 ---
# 模板可以根据关系类型或实体类型进行选择性使用
# 包含公式、代码、自然语言等异构特征
heterogeneous_templates = [
    # 属性关系
    {"template": "{head}的平均时间复杂度为O(n log n)，这是一种{tail}的特性。", "keywords": ["时间复杂度", "效率"], "relation_type": "拥有属性"},
    {"template": "理解{head}的关键在于其{tail}的特点。例如，{head}的时间复杂度常被分析为O(n log n)。", "keywords": ["时间复杂度", "特点"], "relation_type": "拥有属性"},
    {"template": "在{head}中，{tail}是其核心属性之一。例如，在实现{head}时，我们经常会看到类似 `p->next` 的指针操作。", "keywords": ["指针", "实现"], "relation_type": "拥有属性"},
    {"template": "当我们讨论{head}时，不得不提及它的{tail}。它通常涉及例如 `if (condition) {{ /* code */ }}` 这样的逻辑判断。", "keywords": ["逻辑判断", "实现"], "relation_type": "拥有属性"},
    {"template": "对于{head}而言，{tail}是衡量其性能的重要指标。其计算通常涉及到复杂的数学推导。", "keywords": ["性能", "指标"], "relation_type": "拥有属性"},
    {"template": "{head}通常具有{tail}的特性。例如，在C语言中，这种特性可能通过结构体和指针实现。", "keywords": ["结构体", "指针"], "relation_type": "拥有属性"},

    # 包含关系
    {"template": "{head}通常包含{tail}。在某些情况下，{tail}可能是一个复杂的子结构，如链表中的 `struct Node {{ int data; Node* next; }};`。", "keywords": ["链表", "结构体"], "relation_type": "包含"},
    {"template": "{head}是由{tail}构成的。例如，{tail}可能是诸如 `int array[MAX_SIZE];` 这样的数据存储形式。", "keywords": ["数组", "数据存储"], "relation_type": "包含"},
    {"template": "{head}可以被分解为{tail}。理解{head}的运作，就需要深入分析其内部的{tail}。", "keywords": ["分解", "内部机制"], "relation_type": "包含"},
    {"template": "在{head}的实现中，{tail}是必不可少的组成部分。这通常涉及模块化的设计。", "keywords": ["实现", "组成部分"], "relation_type": "包含"},

    # 反义/对比关系
    {"template": "{head}与{tail}是相对的概念。在数据结构中，理解它们之间的区别至关重要。", "keywords": ["相对", "区别"], "relation_type": "反义"},
    {"template": "与{head}不同，{tail}提供了另一种解决问题的方法。", "keywords": ["不同", "方法"], "relation_type": "反义"},
    {"template": "{head}和{tail}在特定语境下具有相反的含义。", "keywords": ["相反", "含义"], "relation_type": "反义"},

    # 属于关系
    {"template": "{head}属于{tail}这一大类。例如，{tail}可能是一个更抽象的范畴，包含多种具体的实现。", "keywords": ["大类", "范畴"], "relation_type": "属于"},
    {"template": "{head}是{tail}的一个典型实例。其实现细节可以从{tail}的定义中推导出来。", "keywords": ["实例", "定义"], "relation_type": "属于"},
    {"template": "将{head}归类为{tail}，有助于我们更好地理解其在整个数据结构体系中的位置。", "keywords": ["归类", "体系"], "relation_type": "属于"},

    # 依赖/被依赖关系
    {"template": "{head}的正确运行依赖于{tail}。如果没有{tail}，{head}的功能将无法实现。", "keywords": ["依赖", "运行"], "relation_type": "依赖"},
    {"template": "{head}被{tail}所依赖。这意味着{tail}是{head}的先决条件。", "keywords": ["被依赖", "先决条件"], "relation_type": "被依赖"},
    {"template": "要实现{head}，我们通常需要先准备好{tail}。这在编程中是常见的依赖关系。", "keywords": ["实现", "准备"], "relation_type": "依赖"},

    # 通用模板（备用）
    {"template": "在数据结构领域，{head}和{tail}之间的关系是{relation}。这需要深入理解其内部机制。", "keywords": ["通用"], "relation_type": ""},
    {"template": "深入探讨{head}与{tail}，可以发现它们之间存在{relation}。例如，考虑一个简单的循环 `for (i = 0; i < n; i++)`。", "keywords": ["通用", "循环"], "relation_type": ""},
    {"template": "关于{head}和{tail}，存在一个重要的{relation}。这在解决问题时需要特别注意。", "keywords": ["通用"], "relation_type": ""}
]

def get_template(head, relation, tail):
    # 尝试匹配特定关系类型的模板
    suitable_templates = [t for t in heterogeneous_templates if t["relation_type"] == relation]
    
    # 如果有匹配的关系类型模板，则从中选择一个包含相关关键词的，或者随机一个
    if suitable_templates:
        # 优先选择包含相关关键词的模板
        for template_info in suitable_templates:
            if any(k in head or k in tail or k in relation for k in template_info["keywords"]):
                return template_info["template"]
        # 如果没有关键词匹配，则随机选择一个该关系类型的模板
        return random.choice(suitable_templates)["template"]
    
    # 如果没有匹配的关系类型模板，则退回到通用模板
    # 优先选择包含相关关键词的通用模板
    general_templates = [t for t in heterogeneous_templates if t["relation_type"] == ""]
    for template_info in general_templates:
        if any(k in head or k in tail or k in relation for k in template_info["keywords"]):
            return template_info["template"]

    return random.choice(general_templates)["template"] # 随机选择一个通用模板


id_counter = 1
generated_samples = []

for i, (head, relation, tail) in enumerate(unique_triples):
    # 仅打印前几个三元组的详细调试信息
    if i < 5:
        print(f"\n--- 处理三元组 {i+1}: ({head}, {relation}, {tail}) ---")

    template_str = get_template(head, relation, tail)
    if i < 5:
        print(f"  选定的模板: {template_str}")
    
    # 填充模板
    try:
        text = template_str.format(head=head, relation=relation, tail=tail)
    except KeyError:
        if '{head}' in template_str and '{tail}' in template_str:
            text = template_str.format(head=head, tail=tail)
        else:
            text = f"{head}和{tail}之间存在{relation}关系。"
    
    if i < 5:
        print(f"  生成的文本: {text}")

    entities_list = []
    
    # 精确标注实体位置
    # 使用 re.escape() 处理特殊字符
    
    # 查找头实体
    head_match = re.search(re.escape(head), text)
    if head_match:
        head_start = head_match.start()
        head_end = head_match.end()
        entities_list.append({"text": head, "start": head_start, "end": head_end, "type": "概念"})
    
    # 查找尾实体，确保不与头实体重叠，并且避免重复添加
    tail_match = re.search(re.escape(tail), text)
    if tail_match:
        tail_start = tail_match.start()
        tail_end = tail_match.end()
        
        is_duplicate = False
        for ent in entities_list:
            if ent["text"] == tail and ent["start"] == tail_start and ent["end"] == tail_end:
                is_duplicate = True
                break
        
        if not is_duplicate: # 避免重复添加完全相同的实体
            entities_list.append({"text": tail, "start": tail_start, "end": tail_end, "type": "概念"})

    if i < 5:
        print(f"  匹配到的实体: {entities_list}")

    # 过滤条件
    # 如果头尾实体相同，entities_list应该至少有一个实体。
    # 如果头尾实体不同，entities_list应该至少有两个实体。
    # 否则跳过。
    if head == tail:
        if not entities_list:
            if i < 5:
                print(f"  跳过: 头尾实体相同，但未找到任何匹配。")
            continue
    else: # head != tail
        if len(entities_list) < 2:
            if i < 5:
                print(f"  跳过: 实体列表少于2个，且头尾实体不同。")
            continue
    
    relations_list = [
        {"head": head, "tail": tail, "relation": relation}
    ]
    
    generated_samples.append({
        "id": f"KG_{id_counter:04d}",
        "text": text,
        "entities": entities_list,
        "relations": relations_list
    })
    id_counter += 1

# --- 3. 生成 schema 文件 ---
# entity_types.txt
with open(os.path.join(schema_dir, 'entity_types.txt'), 'w', encoding='utf-8') as f:
    f.write("# 实体类型列表及说明\n")
    f.write("概念\t通用概念\n") 
    # 可以根据实际提取的实体进一步细化类型

# relation_types.txt
with open(os.path.join(schema_dir, 'relation_types.txt'), 'w', encoding='utf-8') as f:
    f.write("# 关系类型列表及说明\n")
    for rel in sorted(list(relations_set)):
        f.write(f"{rel}\t{rel}关系\n")

# ontology_rules.json (占位)
with open(os.path.join(schema_dir, 'ontology_rules.json'), 'w', encoding='utf-8') as f:
    json.dump({}, f, ensure_ascii=False, indent=2)

# --- 4. 生成 train.jsonl, dev.jsonl, test.jsonl ---
# 目标样本数 (500条或所有生成样本)
total_target_samples = 500
actual_generated_samples = len(generated_samples)
samples_to_use = min(total_target_samples, actual_generated_samples)

random.shuffle(generated_samples) # 再次打乱以确保抽样随机性

selected_samples = generated_samples[:samples_to_use]

train_ratio = 0.7
dev_ratio = 0.1
test_ratio = 0.2

n_train = int(len(selected_samples) * train_ratio)
n_dev = int(len(selected_samples) * dev_ratio)
n_test = len(selected_samples) - n_train - n_dev

train_set = selected_samples[:n_train]
dev_set = selected_samples[n_train : n_train + n_dev]
test_set = selected_samples[n_train + n_dev : n_train + n_dev + n_test]

def write_jsonl_file(filepath, data_set):
    with open(filepath, 'w', encoding='utf-8') as f:
        for entry in data_set:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

write_jsonl_file(os.path.join(data_dir, 'train.jsonl'), train_set)
write_jsonl_file(os.path.join(data_dir, 'dev.jsonl'), dev_set)
write_jsonl_file(os.path.join(data_dir, 'test.jsonl'), test_set)

# --- 5. 创建 scripts 占位文件 ---
with open(os.path.join(scripts_dir, 'convert_to_bioes.py'), 'w', encoding='utf-8') as f:
    f.write("# 占位脚本文件，用于将 jsonl 转换为 BIOES 格式\n")

print(f"数据集生成完成！共生成 {actual_generated_samples} 条样本，实际使用 {samples_to_use} 条。")
print(f"训练集: {len(train_set)} 条, 验证集: {len(dev_set)} 条, 测试集: {len(test_set)} 条。")

# 打印一些样本进行初步检查
print("\n--- 随机抽样样本 (前3条) ---")
for i, sample in enumerate(selected_samples[:3]):
    print(json.dumps(sample, ensure_ascii=False, indent=2))
    if i == 2:
        break
