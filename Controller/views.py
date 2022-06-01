import base64
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import render
import csv
import graphviz
import json
import os
from bs4 import BeautifulSoup

# paper: 0-ID; 1-title; 2-year; 4-citationCount; 6-isKeyPaper; 8-firstAuthor; 9-venue; 11-abstract

def search(request):
    return render(request, 'search.html')

def create_node(papers, dot):
    papers.sort(key=(lambda x: x[2]))

    # 取出论文的所有年份
    publication_time = []
    for paper in papers:
        year = int(paper[2])
        if year not in publication_time:
            publication_time.append(year)

    papers_num_year = {}    # 每年发表的论文数
    # 根据已有年份对论文重新分类，分成subgraph()
    for year in publication_time:
        papers_num_year[str(year)] = 0
        with dot.subgraph() as s:
            s.attr(rank='same')
            s.node(name=str(year))
            for paper in papers:
                if int(paper[2]) == year:
                    papers_num_year[str(year)] += 1
                    s1 = paper[8].split(' ')
                    s2 = paper[1].split(' ')
                    label = s1[0] + str(year) + s2[0]   # label: 第一作者首字+发表年份+论文标题首字
                    # label下为该论文引用量
                    if int(paper[4]) == -1:
                        paper_name = label + '\n' + '???'
                    else:
                        paper_name = label + '\n' + paper[4]
                    # isKeyPaper > 0.5节点边框为红色; 否则为黑色
                    if float(paper[6]) >= 0.5:
                        paper_color = 'red'
                    else:
                        paper_color = 'black'
                    # 论文引用量未知为虚线; 否则为实线
                    # 引用量0~10、10~100、100以上为三种不同边框宽度
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

    return papers_num_year

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
    # 当节点没有边与其相连时，删去
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
            papers[x][-1] += 1
            papers[y][-1] += 1

    papers_backup = []
    paper_shown = []
    for paper in papers:
        if paper[-1] > 0:
            item = []
            for i in paper:
                item.append(i)
            papers_backup.append(item)
            paper_shown.append([item[0], item[1]])

    papers_num_year = create_node(papers_backup, dot)

    create_edge(influence, papers_backup, dot)

    return papers_num_year, paper_shown

def get_node(nodes, papers, papers_num_year):
    node_data = []
    for node in nodes:
        title = node.find('title').string   # 节点的id
        ellipse = node.select('ellipse')
        dict = {}
        dict['id'] = title
        # 当该节点为年份
        if len(dict['id']) == 4:
            dict['name'] = papers_num_year[dict['id']]
            dict['papers_count'] = papers_num_year[dict['id']]    # TODO
        for paper in papers:
            if paper[0] == title:
                dict['name'] = paper[1]
                dict['year'] = int(paper[2])
                if paper[4] == '-1':
                    dict['citation_count'] = '???'
                else:
                    dict['citation_count'] = int(paper[4])
                if paper[-1] == None:
                    dict['abstract'] = "Missing"
                else:
                    dict['abstract'] = paper[11]
                break
        dict['cx'] = float(ellipse[0]['cx'])
        dict['cy'] = float(ellipse[0]['cy'])
        dict['rx'] = float(ellipse[0]['rx'])
        dict['ry'] = float(ellipse[0]['ry'])
        dict['stroke'] = ellipse[0]['stroke']   # 边框颜色
        dict['width'] = None    # 边框宽度
        dict['dasharray'] = None    # 边框是否为虚线
        # 边框要么有宽度，要么为虚线，二者取其一
        if 'stroke-width' in ellipse[0].attrs:
            dict['width'] = ellipse[0]['stroke-width']
        elif 'stroke-dasharray' in ellipse[0].attrs:
            dict['dasharray'] = ellipse[0]['stroke-dasharray']
        else:
            dict['width'] = 1
        node_data.append(dict)
    return node_data

def get_edge(edges, influence):
    edge_data = []
    for edge in edges:
        edge_path = edge.select('path')
        temp = edge.find('title').string    # temp为起始点->终点
        for i in range(0, len(temp)):
            if temp[i] == '-' and temp[i + 1] == '>':
                source = temp[0: i]
                target = temp[i + 2:]
                break
        d = edge_path[0]['d']
        dict = {}
        dict['source'] = source
        dict['target'] = target
        dict['d'] = d
        for link in influence:
            if target == link[0] and source == link[1]:
                dict['citation_context'] = link[4]
        edge_data.append(dict)
    return edge_data

def get_text(nodes):
    label = []
    for node in nodes:
        text = node.select('text')  # text节点
        text_content = node.find_all('text')    # text节点的内容
        for i in range(0, len(text)):
            dict = {}
            dict['id'] = node.find('title').string
            dict['name'] = text_content[i].string
            dict['x'] = text[i]['x']
            dict['y'] = text[i]['y']
            label.append(dict)
    return label

def get_polygon(edges):
    polygon = []
    for edge in edges:
        edge_polygon = edge.select('polygon')
        d = edge_polygon[0]['points']
        polygon.append(d)
    return polygon

def write_d3_data(papers, detail, papers_num_year, influence, paper_shown, isFellow):
    cmd = 'dot -Tsvg ./static/image/graph/' + detail + ' -o ./templates/graph/' + detail + '.html'
    os.system(cmd)
    cmd = './templates/graph/' + detail + '.html'
    soup = BeautifulSoup(open(cmd), features='html.parser')
    nodes = soup.select('.node')
    edges = soup.select('.edge')
    node_data = get_node(nodes, papers, papers_num_year)    # 节点怎么画
    edge_data = get_edge(edges, influence)     # 边怎么画
    label = get_text(nodes)     # 节点内容
    polygon = get_polygon(edges)    # 边的箭头

    svg = soup.select('svg')
    viewBox = svg[0]['viewbox']
    g = soup.select('g')
    transform = g[0]['transform']
    # viewBox属性, g的transform, 不包含年份的节点数, 不包含连接年份的边的边数
    graph = [viewBox, transform, len(nodes) - len(papers_num_year.keys()), len(edges) - len(papers_num_year.keys()) + 1, isFellow]

    data = json.dumps([node_data, edge_data, label, polygon, paper_shown, graph], indent=4, separators=(',', ': '))
    cmd = './static/json/' + detail + '.json'
    f = open(cmd, 'w')
    f.write(data)
    f.close()

def index(request):
    author = request.POST.get("author")
    field = request.POST.get("field")
    request.session['field'] = field
    check_box_list = request.POST.getlist("partial_match")
    if len(check_box_list) == 1:
        print(1)
        filename = './csv/top_1000_arc_authors.csv'
        f = open(filename, 'r', encoding='utf-8')
        csv_reader = csv.reader(f)
        list = []
        for row in csv_reader:
            if author in row[1]:
                scholar = find_scholar(row)
                list.append(scholar)
        return render(request, "list.html", {'scholar_list': list})

    # 匹配所查询的author
    # filename = './csv/' + field + '/top_1000_arc_authors.csv'
    filename = './csv/top_1000_arc_authors.csv'
    f = open(filename, 'r', encoding='utf-8')
    csv_reader = csv.reader(f)
    s1 = author.replace(' ', '')
    flag = 0
    for row in csv_reader:
        s2 = row[1].replace(' ', '')
        if s1 == s2:
            authorRank = int(row[10])
            name = row[1]
            paperCount = int(row[4])
            citationCount = int(row[5])
            hIndex = int(row[6])
            if str(row[12])[1] == 'N':
                isFellow = 0
            else:
                isFellow = 1
            flag = 1
            break
    f.close()
    if flag == 0:
        error = 'No author named ' + author
        return render(request, 'error.html', {'error': error})

    request.session['authorRank'] = authorRank
    request.session['name'] = name

    # full为1,partial为0
    isKeyPaper = 0
    extends_prob = 0

    detail = str(authorRank) + '_1_0_0'
    filename = './static/json/' + detail + '.json'

    if os.path.exists(filename) == False:
        dot = graphviz.Digraph(filename=detail, format='png')

        file = s1 + str(authorRank)
        # 读取相应papers文件
        papers, paper_shown = read_papers(field, file, isKeyPaper)

        papers_num_year = create_node(papers, dot)

        # 读取相应influence文件
        influence = read_influence(field, file, extends_prob)

        create_edge(influence, papers, dot)

        dot.render(directory="./static/image/graph", view=False)
        # data = base64.b64encode(dot.pipe(format='png')).decode("utf-8")

        write_d3_data(papers, detail, papers_num_year, influence, paper_shown, isFellow)

    return render(request, "index.html",
                  {'authorRank': authorRank, 'name': name, 'paperCount': paperCount, 'citationCount': citationCount, 'hIndex': hIndex})

def index_id(request, id):
    field = request.session.get('field')
    # filename = './csv/' + field + '/top_1000_arc_authors.csv'
    filename = './csv/top_1000_arc_authors.csv'
    f = open(filename, 'r', encoding='utf-8')
    csv_reader = csv.reader(f)
    for row in csv_reader:
        if int(id) == int(row[10]):
            authorRank = int(row[10])
            name = row[1]
            paperCount = int(row[4])
            citationCount = int(row[5])
            hIndex = int(row[6])
            if str(row[12])[1] == 'N':
                isFellow = 0
            else:
                isFellow = 1
            break
    f.close()

    request.session['authorRank'] = authorRank
    request.session['name'] = name

    isKeyPaper = 0
    extends_prob = 0

    detail = id + '_1_0_0'
    filename = './static/json/' + detail + '.json'

    if os.path.exists(filename) == False:
        dot = graphviz.Digraph(filename=detail, format='png')

        s1 = name.replace(' ', '')
        file = s1 + str(authorRank)
        # 读取相应papers文件
        papers, paper_shown = read_papers(field, file, isKeyPaper)

        papers_num_year = create_node(papers, dot)

        # 读取相应influence文件
        influence = read_influence(field, file, extends_prob)

        create_edge(influence, papers, dot)

        dot.render(directory="./static/image/graph", view=False)
        # data = base64.b64encode(dot.pipe(format='png')).decode("utf-8")

        write_d3_data(papers, detail, papers_num_year, influence, paper_shown, isFellow)

    return render(request, "index.html",
                  {'authorRank': authorRank, 'name': name, 'paperCount': paperCount, 'citationCount': citationCount, 'hIndex': hIndex})

def update(request):
    field = request.session.get('field')
    authorRank = request.session.get('authorRank')
    name = request.session.get('name')
    file = name.replace(' ', '') + str(authorRank)
    mode = request.POST.get("mode")
    isKeyPaper = request.POST.get("isKeyPaper")
    extends_prob = request.POST.get("extends_prob")
    detail = str(authorRank) + '_' + mode + '_' + isKeyPaper + '_' + extends_prob
    if mode != None:
        mode = int(mode)
    else:
        mode = 1
    if isKeyPaper != None:
        isKeyPaper = float(isKeyPaper)
    else:
        isKeyPaper = 0
    if extends_prob != None:
        extends_prob = float(extends_prob)
    else:
        extends_prob = 0

    filename = './static/json/' + detail + '.json'
    if os.path.exists(filename) == False:
        dot = graphviz.Digraph(filename=detail, format='png')

        papers, paper_shown = read_papers(field, file, isKeyPaper)

        if mode == 1:
            papers_num_year = create_node(papers, dot)

        influence = read_influence(field, file, extends_prob)

        if mode == 1:
            create_edge(influence, papers, dot)
        else:
            papers_num_year, paper_shown = create_partial_graph(influence, papers, dot)

        dot.render(directory="./static/image/graph", view=False)
        # data = base64.b64encode(dot.pipe(format='png')).decode("utf-8")

        write_d3_data(papers, detail, papers_num_year, influence, paper_shown, 0)
    param = {}
    param['detail'] = detail

    return JsonResponse(param, json_dumps_params={'ensure_ascii': False})

def download_picture(request):
    authorRank = request.session.get('authorRank')
    mode = request.POST.get("mode")
    isKeyPaper = request.POST.get("isKeyPaper")
    extends_prob = request.POST.get("extends_prob")
    detail = str(authorRank) + '_' + mode + '_' + isKeyPaper + '_' + extends_prob
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
        scholar = find_scholar(row)
        list.append(scholar)
    return render(request, "init/list.html", {'scholar_list': list})

def download_detail(request, id, mode, isKeyPaper, extends_prob):
    detail = id + '_' + mode + '_' + isKeyPaper + '_' + extends_prob
    filename = './static/image/graph/' + detail + '.png'
    if os.path.exists(filename) == False:
        dot = graphviz.Digraph(filename=detail, format='png')
        fname = './csv/top_1000_arc_authors.csv'
        f = open(fname, 'r', encoding='utf-8')
        csv_reader = csv.reader(f)
        for row in csv_reader:
            if int(id) == int(row[10]):
                authorRank = int(row[10])
                name = row[1]
                break
        f.close()

        mode = int(mode)
        isKeyPaper = float(isKeyPaper)
        extends_prob = float(extends_prob)

        s1 = name.replace(' ', '')
        file = s1 + str(authorRank)
        papers, paper_shown = read_papers('', file, isKeyPaper)

        if mode == 1:
            create_node(papers, dot)

        influence = read_influence('', file, extends_prob)

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

def find_scholar(row):
    scholar = {}
    scholar['authorRank'] = int(row[10])
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
    return scholar

def read_papers(field, file, isKeyPaper):
    # filename = './csv/' + field + '/papers_arc_' + file + '.csv'
    filename = './csv/papers_arc_' + file + '.csv'
    f = open(filename, 'r', encoding='utf-8')
    csv_reader = csv.reader(f)
    papers = []
    paper_shown = []
    for paper in csv_reader:
        item = []
        for i in paper:
            item.append(i)
        item.append(0)
        t = float(item[6])
        if t >= isKeyPaper:
            papers.append(item)
            paper_shown.append([item[0], item[1]])
    f.close()
    return papers, paper_shown

def read_influence(field, file, extends_prob):
    # filename = './csv/' + field + '/influence_arc_' + file + '.csv'
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
        if t >= extends_prob:
            influence.append(item)
    f.close()
    return influence
