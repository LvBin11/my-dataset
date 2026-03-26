import os
import ast

def read_sentences(path):
    sentences = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            if s.startswith('/*') or s.startswith('*/'):
                continue
            try:
                obj = ast.literal_eval(s)
            except Exception:
                continue
            if isinstance(obj, dict) and 'sentence' in obj:
                sentences.append(str(obj['sentence']).strip())
    return sentences

def dedup(seq):
    return list(dict.fromkeys(seq))

def filter_by_length(seq, min_len, max_len):
    return [s for s in seq if min_len <= len(s) <= max_len]

def write_lines(path, lines):
    with open(path, 'w', encoding='utf-8') as f:
        for s in lines:
            f.write(s + '\n')

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ae237-main', '数据结构图谱构建与关系抽取数据集'))
    in_path = os.path.join(base_dir, 'sjjg_datasets.txt')
    sentences = read_sentences(in_path)
    sentences = dedup(sentences)
    filtered_10_500 = filter_by_length(sentences, 10, 500)
    core_50_200 = filter_by_length(sentences, 50, 200)
    out_clean = os.path.join(base_dir, 'sjjg_datasets.cleaned.txt')
    out_core = os.path.join(base_dir, 'sjjg_datasets.core.txt')
    write_lines(out_clean, filtered_10_500)
    write_lines(out_core, core_50_200)
    print('total', len(sentences))
    print('clean_10_500', len(filtered_10_500))
    print('core_50_200', len(core_50_200))

if __name__ == '__main__':
    main()
