import base64
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import render
import csv
import graphviz
import json
import os
from bs4 import BeautifulSoup


def search(request):
    return render(request, 'init/index.html')


def create_node(papers, dot):
    papers.sort(key=(lambda x: x[2]))

    # 取出论文的所有年份
    publication_time = []
    for paper in papers:
        year = int(paper[2])
        if year not in publication_time:
            publication_time.append(year)

    citation_count = {}
    # 根据已有年份对论文重新分类，分成subgraph()
    for year in publication_time:
        citation_count[str(year)] = 0
        with dot.subgraph() as s:
            s.attr(rank='same')
            s.node(name=str(year))
            for paper in papers:
                if int(paper[2]) == year:
                    if int(paper[4]) != -1:
                        citation_count[str(year)] += int(paper[4])
                    s1 = paper[8].split(' ')
                    s2 = paper[1].split(' ')
                    label = s1[0] + str(year) + s2[0]
                    if int(paper[4]) == -1:
                        paper_name = label + '\n' + '???'
                    else:
                        paper_name = label + '\n' + paper[4]
                    if float(paper[6]) >= 0.5:
                        paper_color = 'red'
                    else:
                        paper_color = 'black'
                    if int(paper[4]) == -1:
                        s.node(name=paper[0], label=paper_name, style='dashed', color=paper_color)
                    elif int(paper[4]) != -1 and int(paper[4]) <= 10:
                        s.node(name=paper[0], label=paper_name, style='solid', color=paper_color)
                    elif int(paper[4]) > 10 and int(paper[4]) <= 100:
                        s.node(name=paper[0], label=paper_name, style='solid', color=paper_color, penwidth='3')
                    elif int(paper[4]) > 100:
                        s.node(name=paper[0], label=paper_name, style='solid', color=paper_color, penwidth='10')

    # 将表示年份的点先连接
    for i in range(0, len(publication_time)):
        if i:
            dot.edge(str(publication_time[i - 1]), str(publication_time[i]), arrowsize='0')

    return citation_count


def create_edge(influence, papers, dot):
    for link in influence:
        citingpaperID = link[0]
        citedpaperID = link[1]
        x = len(papers)
        y = len(papers)
        for i in range(0, len(papers)):
            if citingpaperID in papers[i]:
                x = i
            if citedpaperID in papers[i]:
                y = i
        if x < len(papers) and y < len(papers):
            dot.edge(str(papers[y][0]), str(papers[x][0]))

def create_partial_graph(influence, papers, dot):
    papers.sort(key=(lambda x: x[2]))
    for link in influence:
        citingpaperID = link[0]
        citedpaperID = link[1]
        x = len(papers)
        y = len(papers)
        for i in range(0, len(papers)):
            if citingpaperID in papers[i]:
                x = i
            if citedpaperID in papers[i]:
                y = i
        if x < len(papers) and y < len(papers):
            papers[x][12] += 1
            papers[y][12] += 1

    papers_backup = []
    paper_shown = []
    for paper in papers:
        if paper[12] > 0:
            item = []
            for i in paper:
                item.append(i)
            papers_backup.append(item)
            paper_shown.append([item[0], item[1]])

    citation_count = create_node(papers_backup, dot)

    create_edge(influence, papers_backup, dot)

    return citation_count, paper_shown

def get_node(nodes, papers, citation_count):
    pos = []
    for node in nodes:
        ellipse = node.select('ellipse')
        title = node.find('title').string
        dict = {}
        dict['id'] = title
        if len(dict['id']) == 4:
            dict['citation_count'] = citation_count[dict['id']]
            dict['name'] = citation_count[dict['id']]
        for paper in papers:
            if paper[0] == title:
                dict['name'] = paper[1]
                dict['publication_data'] = int(paper[2])
                if paper[4] == '-1':
                    dict['citation'] = '???'
                else:
                    dict['citation'] = int(paper[4])
                if paper[11] == None:
                    dict['abstract'] = ""
                else:
                    dict['abstract'] = paper[11]
                break
        dict['cx'] = float(ellipse[0]['cx'])
        dict['cy'] = float(ellipse[0]['cy'])
        dict['rx'] = float(ellipse[0]['rx'])
        dict['ry'] = float(ellipse[0]['ry'])
        dict['stroke'] = ellipse[0]['stroke']
        dict['width'] = None
        dict['dasharray'] = None
        if 'stroke-width' in ellipse[0].attrs:
            dict['width'] = ellipse[0]['stroke-width']
        elif 'stroke-dasharray' in ellipse[0].attrs:
            dict['dasharray'] = ellipse[0]['stroke-dasharray']
        else:
            dict['width'] = 1
        pos.append(dict)
    return pos

def get_edge(edges):
    path = []
    for edge in edges:
        edge_path = edge.select('path')
        d = edge_path[0]['d']
        temp = edge.find('title').string
        for i in range(0, len(temp)):
            if temp[i] == '-' and temp[i + 1] == '>':
                source = temp[0: i]
                target = temp[i + 2:]
                break
        dict = {}
        dict['source'] = source
        dict['target'] = target
        dict['d'] = d
        path.append(dict)
    return path

def get_text(nodes):
    label = []
    for node in nodes:
        text = node.select('text')
        text_content = node.find_all('text')
        for i in range(0, len(text)):
            text_dict = {}
            text_dict['id'] = node.find('title').string
            text_dict['name'] = text_content[i].string
            text_dict['x'] = text[i]['x']
            text_dict['y'] = text[i]['y']
            label.append(text_dict)
    return label

def get_polygon(edges):
    polygon = []
    for edge in edges:
        edge_polygon = edge.select('polygon')
        d = edge_polygon[0]['points']
        polygon.append(d)
    return polygon

def write_d3_data(papers, detail, citation_count):
    cmd = 'dot -Tsvg ./static/image/graph/' + detail + ' -o ./templates/graph/' + detail + '.html'
    os.system(cmd)
    cmd = './templates/graph/' + detail + '.html'
    soup = BeautifulSoup(open(cmd), features='html.parser')
    nodes = soup.select('.node')
    edges = soup.select('.edge')
    data1 = get_node(nodes, papers, citation_count)
    data2 = get_edge(edges)
    data3 = get_text(nodes)
    data4 = get_polygon(edges)
    data = json.dumps([data1, data2, data3, data4], indent=4, separators=(',', ': '))
    cmd = './static/json/' + detail + '.json'
    f = open(cmd, 'w')
    f.write(data)
    f.close()
    svg = soup.select('svg')
    width = int(svg[0]['width'][0:-2])
    height = int(svg[0]['height'][0:-2])
    return [width, height, len(nodes) - len(citation_count.keys()), len(edges) - len(citation_count.keys()) + 1]

def index(request):
    author = request.POST.get("author")
    check_box_list = request.POST.getlist("partial_match")
    if len(check_box_list) == 1:
        filename = './csv/top_1000_arc_authors.csv'
        f = open(filename, 'r', encoding='utf-8')
        csv_reader = csv.reader(f)
        list = []
        for row in csv_reader:
            if author in row[1]:
                scholar = {}
                scholar['seq'] = int(row[9])
                scholar['name'] = str(row[1])
                scholar['num'] = int(row[4])
                list.append(scholar)
        return render(request, "init/list.html", {'scholarList': list})

    # 匹配所查询的author
    filename = './csv/top_1000_arc_authors.csv'
    f = open(filename, 'r', encoding='utf-8')
    csv_reader = csv.reader(f)
    s1 = author.replace(' ', '')
    flag = 0
    for row in csv_reader:
        s2 = row[1].replace(' ', '')
        if s1 == s2:
            seq = int(row[10])
            author = row[1]
            paperNum = int(row[4])
            citationCount = int(row[5])
            isFellow = int(row[10])
            flag = 1
            break
    f.close()
    if flag == 0:
        error = 'No author named ' + author
        return render(request, 'init/index_alt.html', {'error': error})

    request.session['seq'] = seq
    request.session['name'] = author
    request.session['paperNum'] = paperNum
    request.session['citationCount'] = citationCount
    request.session['isFellow'] = isFellow

    isKeyPaper = 0
    inheritance = -1

    detail = str(seq) + '_1_0_0'
    dot = graphviz.Digraph(filename=detail, format='png')
    # 读取相应papers文件
    file = s1 + str(seq)
    filename = './csv/papers_arc_' + file + '.csv'
    f = open(filename, 'r', encoding='utf-8')
    csv_reader = csv.reader(f)
    filename = './csv/abstract.csv'
    f_abstract = open(filename, 'r', encoding='utf-8')
    abstracts = csv.reader(f_abstract)
    abstractsList = []
    for abstract in abstracts:
        tmp = []
        tmp.append(str(abstract[0]))
        tmp.append(str(abstract[1]))
        abstractsList.append(tmp)
    papers = []
    paper_shown = []
    for paper in csv_reader:
        item = []
        for i in paper:
            item.append(i)
        for abstract in abstractsList:
            if abstract[0] == str(paper[0]):
                item.append(abstract[1])
                break
        item.append(0)
        t = float(item[6])
        if t >= isKeyPaper:
            papers.append(item)
            paper_shown.append([item[0], item[1]])

    citation_count = create_node(papers, dot)

    filename = './csv/influence_arc_' + file + '.csv'
    f = open(filename, 'r', encoding='utf-8')
    csv_reader = csv.reader(f)
    influence = []
    for link in csv_reader:
        item = []
        for i in link:
            item.append(i)
        if item[3][1] == 'N':
            t = 0
        else:
            t = float(item[3])
        if t >= inheritance:
            influence.append(item)

    create_edge(influence, papers, dot)

    f.close()
    dot.render(directory="./static/image/graph", view=False)
    # data = base64.b64encode(dot.pipe(format='png')).decode("utf-8")

    params = write_d3_data(papers, detail, citation_count)
    params.append(isFellow)

    return render(request, "filter/index.html",
                  {'seq': seq, 'name': author, 'paperNum': paperNum, 'citationCount': citationCount, 'params': params, 'paper_shown': paper_shown})

def index_id(request, id):
    filename = './csv/top_1000_arc_authors.csv'
    f = open(filename, 'r', encoding='utf-8')
    csv_reader = csv.reader(f)
    for row in csv_reader:
        if int(id) == int(row[10]):
            seq = int(row[10])
            author = row[1]
            paperNum = int(row[4])
            citationCount = int(row[5])
            if str(row[12])[1] == 'N':
                isFellow = 0
            else:
                isFellow = 1
            break
    f.close()

    request.session['seq'] = seq
    request.session['name'] = author
    request.session['paperNum'] = paperNum
    request.session['citationCount'] = citationCount
    request.session['isFellow'] = isFellow

    isKeyPaper = 0
    inheritance = -1

    detail = id + '_1_0_0'
    dot = graphviz.Digraph(filename=detail, format='png')
    s1 = author.replace(' ', '')
    file = s1 + str(seq)
    filename = './csv/papers_arc_' + file + '.csv'
    f = open(filename, 'r', encoding='utf-8')
    csv_reader = csv.reader(f)
    filename = './csv/abstract.csv'
    f_abstract = open(filename, 'r', encoding='utf-8')
    abstracts = csv.reader(f_abstract)
    abstractsList = []
    for abstract in abstracts:
        tmp = []
        tmp.append(str(abstract[0]))
        tmp.append(str(abstract[1]))
        abstractsList.append(tmp)
    papers = []
    paper_shown = []
    for paper in csv_reader:
        item = []
        for i in paper:
            item.append(i)
        for abstract in abstractsList:
            if abstract[0] == str(paper[0]):
                item.append(abstract[1])
                break
        item.append(0)
        t = float(item[6])
        if t >= isKeyPaper:
            papers.append(item)
            paper_shown.append([item[0], item[1]])

    citation_count = create_node(papers, dot)

    filename = './csv/influence_arc_' + file + '.csv'
    f = open(filename, 'r', encoding='utf-8')
    csv_reader = csv.reader(f)
    influence = []
    for link in csv_reader:
        item = []
        for i in link:
            item.append(i)
        if item[3][1] == 'N':
            t = 0
        else:
            t = float(item[3])
        if t >= inheritance:
            influence.append(item)

    create_edge(influence, papers, dot)

    f.close()
    dot.render(directory="./static/image/graph", view=False)
    # data = base64.b64encode(dot.pipe(format='png')).decode("utf-8")

    params = write_d3_data(papers, detail, citation_count)
    params.append(isFellow)

    return render(request, "filter/index.html",
                  {'seq': seq, 'name': author, 'paperNum': paperNum, 'citationCount': citationCount, 'params': params, 'paper_shown': paper_shown})

def update(request):
    seq = request.session.get('seq')
    author = request.session.get('name')
    file = author.replace(' ', '') + str(seq)
    mode = request.POST.get("mode")
    isKeyPaper = request.POST.get("isKeyPaper")
    inheritance = request.POST.get("inheritance")
    print(mode, isKeyPaper, inheritance)
    detail = str(seq) + '_' + mode + '_' + isKeyPaper + '_' + inheritance
    if mode != None:
        mode = int(mode)
    else:
        mode = 1
    if isKeyPaper != None:
        isKeyPaper = float(isKeyPaper)
    else:
        isKeyPaper = 0
    if inheritance != None:
        if inheritance == '0':
            inheritance = -1
        else:
            inheritance = float(inheritance)
    else:
        inheritance = -1

    filename = './csv/papers_arc_' + file + '.csv'
    f = open(filename, 'r', encoding='utf-8')
    csv_reader = csv.reader(f)
    filename = './csv/abstract.csv'
    f_abstract = open(filename, 'r', encoding='utf-8')
    abstracts = csv.reader(f_abstract)
    abstractsList = []
    for abstract in abstracts:
        tmp = []
        tmp.append(str(abstract[0]))
        tmp.append(str(abstract[1]))
        abstractsList.append(tmp)
    papers = []
    paper_shown = []
    for paper in csv_reader:
        item = []
        for i in paper:
            item.append(i)
        for abstract in abstractsList:
            if abstract[0] == str(paper[0]):
                item.append(abstract[1])
                break
        item.append(0)
        t = float(item[6])
        if t >= isKeyPaper:
            papers.append(item)
            paper_shown.append([item[0], item[1]])

    dot = graphviz.Digraph(filename=detail, format='png')
    if mode == 1:
        citation_count = create_node(papers, dot)

    filename = './csv/influence_arc_' + file + '.csv'
    f = open(filename, 'r', encoding='utf-8')
    csv_reader = csv.reader(f)
    influence = []
    for link in csv_reader:
        item = []
        for i in link:
            item.append(i)
        if item[3][1] == 'N':
            t = 0
        else:
            t = float(item[3])
        if t >= inheritance:
            influence.append(item)

    if mode == 1:
        create_edge(influence, papers, dot)
    else:
        citation_count, paper_shown = create_partial_graph(influence, papers, dot)

    f.close()
    dot.render(directory="./static/image/graph", view=False)
    # data = base64.b64encode(dot.pipe(format='png')).decode("utf-8")
    # return render(request, "filter/index.html", {'seq': seq, 'name': author, 'paperNum': paperNum})

    param = write_d3_data(papers, detail, citation_count)
    params = {}
    params['param'] = param
    params['detail'] = detail
    params['paper_shown'] = paper_shown

    return JsonResponse(params, json_dumps_params={'ensure_ascii': False})

def download_picture(request):
    seq = request.session.get('seq')
    mode = request.POST.get("mode")
    isKeyPaper = request.POST.get("isKeyPaper")
    inheritance = request.POST.get("inheritance")
    detail = str(seq) + '_' + mode + '_' + isKeyPaper + '_' + inheritance
    param = {}
    param['detail'] = detail
    param['filename'] = '/src/image/graph/' + detail + '.png'
    return JsonResponse(param, json_dumps_params={'ensure_ascii': False})

def showlist(request):
    filename = './csv/top_1000_arc_authors.csv'
    f = open(filename, 'r', encoding='utf-8')
    csv_reader = csv.reader(f)
    list = []
    for row in csv_reader:
        scholar = {}
        scholar['seq'] = int(row[10])
        scholar['name'] = str(row[1])
        fellow = str(row[12])
        isfellow = ''
        score = 0
        if fellow[1] != 'N':
            for i in range(len(fellow) - 1, -1, -1):
                if fellow[i] == ':':
                    if len(isfellow) > 1:
                        isfellow += '/'
                    if fellow[i - 1] == '3':
                        isfellow += 'ACL LTA award'
                        score += 4
                    if fellow[i - 1] == '2':
                        isfellow += 'ACM Fellow'
                        score += 2
                    if fellow[i - 1] == '1':
                        isfellow += 'ACL Fellow'
                        score += 1
        scholar['fellow'] = isfellow
        scholar['citationCount'] = str(row[5])
        scholar['hindex'] = int(row[6])
        scholar['num'] = int(row[4])
        scholar['score'] = score
        list.append(scholar)
    return render(request, "init/list.html", {'scholarList': list})

def download_detail(request, id, mode, isKeyPaper, inheritance):
    detail = id + '_' + mode + '_' + isKeyPaper + '_' + inheritance
    filename = './static/image/graph/' + detail + '.png'
    if os.path.exists(filename) == False:
        dot = graphviz.Digraph(filename=detail, format='png')
        fname = './csv/top_1000_arc_authors.csv'
        f = open(fname, 'r', encoding='utf-8')
        csv_reader = csv.reader(f)
        for row in csv_reader:
            if int(id) == int(row[10]):
                seq = int(row[10])
                author = row[1]
                break
        f.close()

        mode = int(mode)
        isKeyPaper = float(isKeyPaper)
        if inheritance == '0':
            inheritance = -1
        else:
            inheritance = float(inheritance)

        s1 = author.replace(' ', '')
        file = s1 + str(seq)
        fname = './csv/papers_arc_' + file + '.csv'
        f = open(fname, 'r', encoding='utf-8')
        csv_reader = csv.reader(f)
        papers = []
        for paper in csv_reader:
            item = []
            for i in paper:
                item.append(i)
            item.append("abstract")
            item.append(0)
            t = float(item[6])
            if t >= isKeyPaper:
                papers.append(item)
        f.close()

        if mode == 1:
            create_node(papers, dot)

        fname = './csv/influence_arc_' + file + '.csv'
        f = open(fname, 'r', encoding='utf-8')
        csv_reader = csv.reader(f)
        influence = []
        for link in csv_reader:
            item = []
            for i in link:
                item.append(i)
            if item[3][1] == 'N':
                t = 0
            else:
                t = float(item[3])
            if t >= inheritance:
                influence.append(item)
        f.close()

        if mode == 1:
            create_edge(influence, papers, dot)
        else:
            create_partial_graph(influence, papers, dot)

        dot.render(directory="./static/image/graph", view=False)

    file = open(filename, 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename=' + detail + '.png'
    return response