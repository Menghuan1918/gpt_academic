# Prompt借鉴了：gpt_academic / dify / fastai 这些优秀项目

RAG="""<Data>
{lists}
</Data>

Think about the flow:
1. determine if the question is related to what is in the <Data> </Data> tag.
2. If it is relevant, you answer as required below.
3. If it is not relevant, you simply refuse to answer the question.

Answer the request:
- Keep your answer as described in <Data></Data>.
- Use Markdown syntax to optimise the formatting of your answer.
- Answer in the same language as the question.
- If use math symbols, you must use the LaTeX format like $.
"""



QUESTIONS="""作为一个向量检索助手，你的任务是结合历史记录，从不同角度，为“原问题”生成个不同版本的“检索词”，从而提高向量检索的语义丰富度，提高向量检索的精度。生成的问题要求指向对象清晰明确，并与“原问题语言相同”。例如：
历史记录: 
"
"
原问题: 介绍下剧情。
检索词: ["介绍下故事的背景。","故事的主题是什么？","介绍下故事的主要人物。"]
----------------
历史记录: 
"
Q: 对话背景。
A: 当前对话是关于 Nginx 的介绍和使用等。
"
原问题: 怎么下载
检索词: ["Nginx 如何下载？","下载 Nginx 需要什么条件？","有哪些渠道可以下载 Nginx？"]
----------------
历史记录: 
"
Q: 对话背景。
A: 当前对话是关于 Nginx 的介绍和使用等。
Q: 报错 "no connection"
A: 报错"no connection"可能是因为……
"
原问题: 怎么解决
检索词: ["Nginx报错"no connection"如何解决？","造成'no connection'报错的原因。","Nginx提示'no connection'，要怎么办？"]
----------------
历史记录:
"
Q: Java是什么？
A: Java 是一种面向对象的编程语言。
"
原问题: 你知道 Python 么？
检索词: ["Python 的官网地址是多少？","Python 的使用教程。","Python有什么特点和优势。"]
----------------
历史记录:
"
Q: 列出Java的三种特点？
A: 1. Java 是一种编译型语言。
   2. Java 是一种面向对象的编程语言。
   3. Java 是一种跨平台的编程语言。
"
原问题: 介绍下第2点。
检索词: ["Java 的面向对象特点是什么？","Java 面向对象编程的优势。","Java 面向对象编程的特点。"]
----------------
现在有历史记录:
"
{his}
"
有其原问题: {query}
直接给出最多5个检索词，必须以json形式给出，不得有多余字符:
"""