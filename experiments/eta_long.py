
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

        # run compression
        kwargs = stitch_core.from_dreamcoder(j)
        kwargs.update(dict(
            eta_long=True,
            utility_by_rewrite=True
        ))

        assert kwargs['programs'] == stitch_core.dreamcoder_to_stitch(programs,stitch_core.name_mapping_dreamcoder(j))

        res = stitch_core.compress(max_arity=3, iterations=10, **kwargs)

        rewritten = res.json['rewritten_dreamcoder']
        assert len(rewritten) == len(programs)

        # here's an example of adding together two name_mappings:
        assert res.json['rewritten_dreamcoder'] == stitch_core.stitch_to_dreamcoder(res.rewritten, stitch_core.name_mapping_dreamcoder(j) + stitch_core.name_mapping_stitch(res.json))

        print(f"Found {len(res.abstractions)} abstractions for a compression of {res.json['compression_ratio']:.2f}")

        # ensure rewriting with eta long also does the same: importantly pass in **kwargs here too or it
        # won't be in eta long form. rewrite() does an extremely fast variant of compressive search itself internally
        # so it takes all the same arguments as compress()
        rw = stitch_core.rewrite(abstractions=res.abstractions, **kwargs)

        assert rw.rewritten == res.rewritten

        print(rw.json["rewritten_dreamcoder"])

        # unfortunately rw.json["rewritten_dreamcoder"] is currently not supported, but you can get the same thing
        # by passing in the name mapping yourself:
        assert res.json['rewritten_dreamcoder'] == stitch_core.stitch_to_dreamcoder(rw.rewritten, stitch_core.name_mapping_dreamcoder(j) + stitch_core.name_mapping_stitch(res.json))

        # create a new grammar object
        j2 = deepcopy(j)
        j2['DSL']['productions'].extend([{'logProbability': 0, 'expression': abs['dreamcoder']} for abs in res.json['abstractions']])
        g2 = grammar_from_json(j2)

        for (i,(p,request)) in enumerate(zip(rewritten, requests)):
            long = eta_long(p, request, g2)
            assert str(p) == str(long)
