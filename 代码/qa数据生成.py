import json
import random
import os

def generate_qa_from_triples(file_path, output_path, num_samples=30):
    """
    从 entity_relation.txt 中读取三元组，并利用模板生成 QA 数据
    """
    triples = []
    
    # 1. 读取你的 entity_relation.txt
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # 跳过注释、无关行
            if not line or line.startswith('/*') or line.startswith('[') or '无关' in line:
                continue
            
            parts = line.split()
            if len(parts) >= 3:
                head, tail, relation = parts[0], parts[1], parts[2]
                triples.append((head, relation, tail))
    
    # 2. 定义简单的自然语言模板 (根据你的 relations.txt 里的关系名来定制)
    # 这里的 key 必须是你 entity_relation.txt 里真实出现的 relation 名字
    templates = {
        "包含": [
            "{head}包含哪些内容？",
            "{head}主要由什么组成？",
            "列举{head}的一个组成部分。"
        ],
        "属于": [
            "{head}属于什么类别？",
            "{head}是哪种概念的实例？"
        ],
        "反义": [
            "{head}的对立概念是什么？",
            "与{head}含义相反的是什么？"
        ],
        "同义": [
            "{head}的别名是什么？",
            "{head}还可以怎么称呼？"
        ],
        "定义": [  # 假设你有这个关系
            "什么是{head}？",
            "请解释一下{head}的概念。"
        ],
        # 如果你的关系是英文的 (比如 has_complexity)，改成英文 key
        "has_complexity": [
            "{head}的时间复杂度是多少？"
        ]
    }
    
    qa_data = []
    
    # 3. 随机抽取并生成
    # 为了保证质量，我们这里简单打乱一下
    random.shuffle(triples)
    
    count = 0
    for head, relation, tail in triples:
        if count >= num_samples:
            break
            
        # 查找是否有对应的模板
        if relation in templates:
            question_template = random.choice(templates[relation])
            question = question_template.format(head=head)
            
            # 构建 JSON 对象
            item = {
                "question": question,
                "start_entity": head,
                "target_entity": tail,
                # 注意：ground_truth_path 必须是 [实体, 关系, 实体...] 的格式
                # 这里是单跳，所以直接就是三元组
                "ground_truth_path": [head, relation, tail]  
            }
            qa_data.append(item)
            count += 1
    
    # 4. 保存为 JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(qa_data, f, ensure_ascii=False, indent=2)
    
    print(f"已生成 {len(qa_data)} 条 QA 数据到 {output_path}")

# 使用示例
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(base_dir, 'entity_relation.txt')
    output_file = os.path.join(base_dir, 'dataset_train_seed.json')
    
    generate_qa_from_triples(input_file, output_file, num_samples=30)