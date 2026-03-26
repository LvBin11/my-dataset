import os

class KnowledgeGraph:
    def __init__(self, data_dir):
        """
        初始化知识图谱，加载三个核心文件
        :param data_dir: 包含 entities.txt, relations.txt, triples.txt 的目录路径
        """
        self.data_dir = data_dir
        self.entity2id = {}
        self.id2entity = {}
        self.relation2id = {}
        self.id2relation = {}
        self.triples = []
        self.adj_list = {}  # 邻接表，用于快速查找邻居

        # 加载数据
        self._load_entities(os.path.join(data_dir, 'entities.txt'))
        self._load_relations(os.path.join(data_dir, 'relations.txt'))
        self._load_triples(os.path.join(data_dir, 'triples.txt'))

    def _load_entities(self, path):
        print(f"Loading entities from {path}...")
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    eid, name = parts[0], parts[1]
                    self.entity2id[name] = int(eid)
                    self.id2entity[int(eid)] = name

    def _load_relations(self, path):
        print(f"Loading relations from {path}...")
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    rid, name = parts[0], parts[1]
                    self.relation2id[name] = int(rid)
                    self.id2relation[int(rid)] = name

    def _load_triples(self, path):
        print(f"Loading triples from {path}...")
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 3:
                    h, r, t = int(parts[0]), int(parts[1]), int(parts[2])
                    self.triples.append((h, r, t))
                    
                    # 构建邻接表: head -> [(relation, tail), ...]
                    if h not in self.adj_list:
                        self.adj_list[h] = []
                    self.adj_list[h].append((r, t))

    def get_neighbors(self, entity_id):
        """
        查询某个节点的所有邻居
        :param entity_id: 实体ID
        :return: 列表 [(关系名, 邻居实体名)]
        """
        if entity_id not in self.adj_list:
            return []
        
        neighbors = []
        for rid, tid in self.adj_list[entity_id]:
            r_name = self.id2relation.get(rid, "Unknown")
            t_name = self.id2entity.get(tid, "Unknown")
            neighbors.append((r_name, t_name))
        return neighbors

    def get_id_by_name(self, name):
        return self.entity2id.get(name)

# ==========================================
# 辅助工具：将你的 entity_relation.txt 转换为标准格式
# ==========================================
def convert_your_files_to_standard_format(input_file, output_dir):
    print("正在转换数据格式...")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    entities = set()
    relations = set()
    raw_triples = []

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # 跳过注释和空行
            if not line or line.startswith('/*') or line.startswith('*/') or line.startswith('['):
                continue
            
            parts = line.split()
            if len(parts) < 3: continue
            
            h, t, r = parts[0], parts[1], parts[2]
            
            # 重要：过滤掉“无关”关系，这在构建知识图谱时非常重要
            if r == '无关':
                continue

            entities.add(h)
            entities.add(t)
            relations.add(r)
            raw_triples.append((h, r, t))

    # 生成 ID 映射
    entity_list = sorted(list(entities))
    relation_list = sorted(list(relations))
    
    e2id = {e: i for i, e in enumerate(entity_list)}
    r2id = {r: i for i, r in enumerate(relation_list)}

    # 写入 entities.txt
    with open(os.path.join(output_dir, 'entities.txt'), 'w', encoding='utf-8') as f:
        for e, i in e2id.items():
            f.write(f"{i}\t{e}\n")

    # 写入 relations.txt
    with open(os.path.join(output_dir, 'relations.txt'), 'w', encoding='utf-8') as f:
        for r, i in r2id.items():
            f.write(f"{i}\t{r}\n")

    # 写入 triples.txt
    with open(os.path.join(output_dir, 'triples.txt'), 'w', encoding='utf-8') as f:
        for h, r, t in raw_triples:
            f.write(f"{e2id[h]}\t{r2id[r]}\t{e2id[t]}\n")

    print(f"转换完成！文件已保存在: {output_dir}")

# ==========================================
# 使用示例
# ==========================================
if __name__ == "__main__":
    # 获取当前脚本所在目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(base_dir, 'entity_relation.txt')
    output_dir = os.path.join(base_dir, 'kg_data')

    # 1. 先进行数据转换
    convert_your_files_to_standard_format(input_file, output_dir)

    # 2. 初始化知识图谱类
    kg = KnowledgeGraph(output_dir)

    # 3. 测试查询
    test_entity_name = "有向图"  # 你的数据里有的实体
    eid = kg.get_id_by_name(test_entity_name)
    
    if eid is not None:
        print(f"\n查询实体: {test_entity_name} (ID: {eid})")
        neighbors = kg.get_neighbors(eid)
        print(f"找到 {len(neighbors)} 个邻居:")
        for relation, neighbor in neighbors:
            print(f"  --[{relation}]--> {neighbor}")
    else:
        print(f"未找到实体: {test_entity_name}")