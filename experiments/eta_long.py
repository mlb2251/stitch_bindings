
from dreamcoder.program import EtaLongVisitor, Program
from dreamcoder.grammar import Grammar
from pathlib import Path
import json
from dreamcoder.type import Type
from copy import deepcopy
import stitch_core
from dreamcoder.domains.list.listPrimitives import bootstrapTarget_extra
bootstrapTarget_extra()


def eta_long(p, request, g):
    prog = Program.parse(p)
    expanded = EtaLongVisitor(request=request).execute(prog)
    g.logLikelihood(request, expanded)
    return expanded


domains = ['logo', 'towers', 'list', 'text', 'physics', 'origami']

def grammar_from_json(j):
        g = j['DSL']
        g = Grammar(g["logVariable"],
            [(l, p.infer(), p)
                for production in g["productions"]
                for l in [production["logProbability"]]
                for p in [Program.parse(production["expression"])]],
            continuationType=Type.fromjson(g["continuationType"]) if "continuationType" in g else None)
        return g

for domain in domains:
    for f in Path("compression_benchmark/benches/").glob(f"{domain}*/*.json"):
        print(f)


        with open(f, "r") as fp:
            j = json.load(fp)
        progs = [(p['program'], Type.fromjson(f['request'])) for f in j["frontiers"] for p in f["programs"]]

        g = grammar_from_json(j)

        # ensure all the inputs were eta-long before we start compression
        for (p,request) in progs:
            long = eta_long(p, request, g)
            assert str(p) == str(long)
        
        programs, requests = zip(*progs)

        name_mapping = stitch_core.name_mapping_dreamcoder(j)
        stitch_programs = stitch_core.dreamcoder_to_stitch(programs,name_mapping)

        # run compression
        compress_kwargs = stitch_core.from_dreamcoder(j, eta_long=True)

        assert compress_kwargs['programs'] == stitch_programs

        res = stitch_core.compress(max_arity=3, iterations=10, **compress_kwargs)

        name_mapping += stitch_core.name_mapping_stitch(res.json)

        rewritten = res.json['rewritten_dreamcoder']
        assert len(rewritten) == len(programs)
        assert res.json['rewritten_dreamcoder'] == stitch_core.stitch_to_dreamcoder(res.rewritten, name_mapping)

        print(f"Found {len(res.abstractions)} abstractions for a compression of {res.json['compression_ratio']:.2f}")

        # ensure rewriting with eta long also does the same
        compress_kwargs.pop('tasks')
        compress_kwargs.pop('name_mapping')
        rw = stitch_core.rewrite(abstractions=res.abstractions, **compress_kwargs)

        assert rw.rewritten == res.rewritten
        assert res.json['rewritten_dreamcoder'] == stitch_core.stitch_to_dreamcoder(rw.rewritten, name_mapping)

        # create a new grammar object
        j2 = deepcopy(j)
        j2['DSL']['productions'].extend([{'logProbability': 0, 'expression': abs['dreamcoder']} for abs in res.json['abstractions']])
        g2 = grammar_from_json(j2)

        for (i,(p,request)) in enumerate(zip(rewritten, requests)):
            long = eta_long(p, request, g2)
            assert str(p) == str(long)
