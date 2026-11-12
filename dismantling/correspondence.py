"""Check the manuscript source extracts against the public mathematical inputs.

The source hashes identify the exact extracts. Separate parsers compare the
three minimum-order tables with the graphs, reductions and expected counts.
The existing article checker handles the other three tables and all figures.
"""
import hashlib
import re
from pathlib import Path
from .graphs import ROOT, require, strict_json, parameters, from_lists, family_graph, induced


def rows(name):
    text = (ROOT / 'data/article_tables' / name).read_text(encoding='utf-8')
    result = []
    for line in text.splitlines():
        if line.startswith(r'\(X_'):
            parts = line.removesuffix(r'\\').split('&')
            result.append([s.strip().removeprefix(r'\(').removesuffix(r'\)') for s in parts])
    require(len(result) == 7, 'A minimum-order table has missing or extra rows')
    require([int(re.fullmatch(r'X_(\d)', row[0])[1]) for row in result] == list(range(1,8)),
            'Minimum-order table labels are out of order')
    return result


def run(pdf=None):
    record = strict_json((ROOT/'data/article_correspondence.json').read_text(encoding='utf-8'))
    for item in record['files']:
        require(hashlib.sha256((ROOT/item['repository_file']).read_bytes()).hexdigest() == item['sha256'],
                'An article source extract differs: ' + item['repository_file'])
    seeds = strict_json((ROOT/'data/minimum_order/seeds.json').read_text(encoding='utf-8'))
    require([r['graph'] for r in seeds] == list(range(1,8)), 'The seven seed labels differ')
    for row, seed in zip(rows('small_seeds.tex'), seeds):
        missing = [[int(s[0]), int(s[1])] for s in row[1].split(',')]
        require(missing == seed['missing_edges'], 'A printed missing-edge list differs')
    for row, seed in zip(rows('small_reductions.tex'), seeds):
        first = int(row[1])
        path = list(map(int, row[2].split(',')))
        folds = [list(map(int, p)) for p in re.findall(r'(\d+)\\to\s*(\d+)',row[3])]
        require((first,path,folds,int(row[4])) == (seed['first'],seed['path'],seed['folds'],seed['apex']),
                'A printed seed reduction differs')
    expected = strict_json((ROOT/'data/minimum_order/expected_extensions.json').read_text(encoding='utf-8'))
    keys = ['nonzero_q','D0','strict1','zero_q_outside_D2']
    for row, wanted in zip(rows('small_extensions.tex'),expected):
        require(list(map(int,row[1:])) == [wanted['unordered'][key] for key in keys],
                'A printed extension count differs')
    missing_text = (ROOT/'data/article_tables/secondary_missing.tex').read_text(encoding='utf-8')
    missing = {tuple(map(int,p)) for p in re.findall(r'\((\d+),(\d+)\)',missing_text)}
    require(len(missing) == 23,'Secondary seed must have exactly 23 missing edges')
    a = from_lists([[u for u in range(16) if u != v and tuple(sorted((u,v))) not in missing] for v in range(16)])
    params = parameters('4k4')
    require(a == from_lists(params['A']), 'The secondary-family seed differs from its article equation')
    profiles_text = (ROOT/'data/article_tables/secondary_profiles.tex').read_text(encoding='utf-8')
    omissions = re.findall(r'P_(\d).*?\\setminus\\\{([\d,]+)\\\}',profiles_text)
    require([int(j) for j,_ in omissions] == [0,1,2], 'The article profile equation is incomplete')
    require([sorted(set(range(16))-set(map(int,s.split(',')))) for _,s in omissions] == params['profiles'],
            'The profiles differ from the article equation')
    h1,_ = family_graph('4k4',1)
    h2,_ = family_graph('4k4',2)
    require(h1 == induced(a,params['prefix']['1']) and h2 == induced(a,params['prefix']['2']),
            'The H_1 or H_2 prefix differs')
    from .h2 import FOLDS
    folds_text = (ROOT/'data/article_tables/h2_folds.tex').read_text(encoding='utf-8')
    fold_rows = re.findall(r'^\\\((\d+)\\\)&\\\((.*?)\\\)',folds_text,re.M)
    printed = {int(v): [tuple(map(int,p)) for p in re.findall(r'(\d+)\\to\s*(\d+)',s)] for v,s in fold_rows}
    require(printed == FOLDS, 'The octahedral reductions differ from the article table')
    answer = {'source_files':len(record['files']), 'minimum_order_table_rows':21,
              'H2_neighbourhood_rows':4,'secondary_seed_and_profiles':True,
              'identified_pdf_sha256':record['manuscript_pdf_sha256'],
              'scope':'Extract bytes match the recorded hashes and their numerical values match the calculation inputs. The source-to-manuscript mapping is recorded by the authors; PDF layout is not parsed.'}
    if pdf is not None:
        digest = hashlib.sha256(Path(pdf).read_bytes()).hexdigest()
        allowed = [record['manuscript_pdf_sha256']] + record.get('citation_only_derivatives',[])
        require(digest in allowed, 'The supplied PDF is not one of the identified manuscript files')
        answer['supplied_pdf_sha256'] = digest
    return answer
