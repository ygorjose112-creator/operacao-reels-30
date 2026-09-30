import csv, io, json, re, urllib.request, urllib.parse

BASE = 'https://docs.google.com/spreadsheets/d/11bpG9xgvn2cWDNjYxrLW-Gi3whoApThEIF7mwMYVbVE/gviz/tq?tqx=out:csv&sheet='
def rows(name):
    return list(csv.reader(io.StringIO(urllib.request.urlopen(BASE + urllib.parse.quote(name)).read().decode())))
def clean(text):
    text = text.strip().replace('Abra o desafio', 'Abra seu calendário editorial').replace('final do desafio', 'final da sequência editorial').replace('esse desafio', 'essa sequência editorial').replace('Último reel do desafio', 'Último reel do calendário editorial').replace('durante o desafio', 'durante a sequência editorial')
    return re.sub(r'desafio', 'calendário editorial', text, flags=re.I)
def pillar(text):
    return re.sub(r'^[^A-Za-zÀ-ÿ]+', '', text).strip().title().replace('Strong Take', 'Strong Take')
missions=[]
for r in rows('🗓️ Missões 1–30'):
    if len(r)>6 and re.match(r'Dia \d+',r[1]):
        missions.append(dict(day=int(r[1].split()[1]),name=r[2].replace('🎯 ',''),pillar=pillar(r[3]),format=r[4],duration=r[5],difficulty=r[6].count('★'),hooks=[],references=[]))
current=None
for r in rows('📍 Missões Detalhadas'):
    match=re.search(r'DIA (\d+)',r[1] if len(r)>1 else '')
    if match: current=missions[int(match[1])-1]
    if current and len(r)>3:
        key=r[2]; value=clean(r[3])
        if key=='Briefing': current['briefing']=value
        elif key.startswith('Gancho'): current['hooks'].append(value)
        elif key=='Métrica-alvo': current['metric']=value
        elif 'Dica de produção' in key: current['tip']=value
        if len(r)>4:
            for url in re.findall(r'https?://[^\s]+',r[4]): current['references'].append({'url':url,'label':key if key else 'Referência'})
hooks=[]; p=''
for r in rows('🪝 Banco de Ganchos'):
    if len(r)>2 and r[1].startswith('#'): hooks.append({'pillar':p,'text':clean(r[2])})
    elif len(r)>1 and any(x in r[1] for x in ['STRONG TAKE','STORYTIME','RANKING','BREAKDOWN','DADOS','CENÁRIO']): p=pillar(r[1])
assert len(missions)==30 and len(hooks)==60 and all(len(m['hooks'])==5 for m in missions)
with open('data.js','w') as f: f.write('const CONTENT = '+json.dumps({'missions':missions,'hooks':hooks},ensure_ascii=False)+';\n')
print(f'{len(missions)} missões, {len(hooks)} ganchos, {sum(len(m["references"]) for m in missions)} referências importadas.')
