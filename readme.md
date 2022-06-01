# 1.表格形式

## 1.1 top_1000_arc_authors.csv

| 0        | 1    | 2        | 3            | 4              | 5                 | 6          | 
| -------- | ---- | -------- | ------------ | -------------- | ----------------- | ---------- | 
| authorID | name | name_MAG | authorID_MAG | PaperCount_ARC | CitationCount_ARC | hIndex_ARC | 

| 7                  | 8                     | 9              | 10         | 11             | 12         |
| ------------------ | --------------------- | -------------- | ---------- | -------------- | ---------- |
| PaperCount_MAG_NLP | CitationCount_MAG_NLP | hIndex_MAG_NLP | authorRank | PaperCount_ACL | FellowType |

## 1.2 papers_arc_.csv

| 0       | 1     | 2    | 3    | 4             | 5           |
| ------- | ----- | ---- | ---- | ------------- | ----------- |
| paperID | title | year |      | citationCount | authorOrder |

| 6          | 7             | 8               | 9     | 10         | 11       |
| ---------- | ------------- | --------------- | ----- | ---------- | -------- |
| isKeyPaper | firstAuthorID | firstAuthorName | venue | isACLPaper | abstract |

# 2.svg格式

## 2.1 总体

```html
<svg width="13549pt" height="1318pt" viewBox="0.00 0.00 13548.57 1318.10">
    <g id="graph0" class="graph" transform="scale(1 1) rotate(0) translate(4 1314.1)">
        节点和边
    </g>
</svg>
```

## 2.2 节点

* 年份

  ```html
  <g id="node1" class="node">
      <title>2006</title>
  	<ellipse fill="none" stroke="black" cx="28.5975" cy="-1283.23" rx="28.6953" ry="18"/>
  	<text text-anchor="middle" x="28.5975" y="-1279.53" font-size="14.00">2006</text>
  </g>
  ```

* 论文

  ```html
  <g id="node2" class="node">
      <title>P06&#45;2100</title>
  	<ellipse fill="none" stroke="red" stroke-width="3" cx="3700.6" cy="-1283.23" rx="110.118" ry="26.7407"/>
      <text x="3700.6" y="-1287.03" font-family="Times New Roman,serif" font-size="14.00">label</text>
  	<text x="3700.6" y="-1272.03" font-family="Times New Roman,serif" font-size="14.00">60</text>
  </g>
  ```

## 2.3 边

```html
<g id="edge1" class="edge">
    <title>2006&#45;&gt;2008</title>
	<path fill="none" stroke="black" d="M28.5975,-1264.9C28.5975,-1249.54 28.5975,-1227.22 28.5975,-1211.85"/>
	<polygon fill="black" stroke="black" points="28.5975,-1211.49 28.5975,-1211.49 28.5975,-1211.49 28.5975,-1211.49"/>
</g>
```



# 3.css

```css
#home {
    /*background: url(../../image/filter/header-bg.jpg) no-repeat center top;*/
    background-size: cover;
    -webkit-background-size: cover;
    -moz-background-size: cover;
    -o-background-size: cover;
    -ms-background-size: cover;
    min-height:650px;
   position: relative;
}
```
