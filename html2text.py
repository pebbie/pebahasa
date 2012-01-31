"""

HTML Cleaning tool

Author: Peb Ruswono Aryan
Description: extract text part from html document

"""
import re
import sys

replacer = [
            (re.compile(r"\r"), r""),
            (re.compile(r"&nbsp;"), r""),
            (re.compile(r"&(amp|#38);", re.I), r"&"),
            (re.compile(r"[\n\t]+"), r" "),
            (re.compile(r"<meta[^>]*\/?>", re.I), r""),
            (re.compile(r"<link[^>]*\/?>", re.I), r""),
            (re.compile(r"<script[^>]*>.*?<\/script>", re.I), r""),
            (re.compile(r"<style[^>]*>.*?<\/style>", re.I), r""),
            (re.compile(r"<!.*-->", re.I), r""),
            (re.compile(r"<h[123][^>]*>(.*?)<\/h[123]>", re.I), r"\1\n"),
            (re.compile(r"<h[456][^>]*>(.*?)<\/h[456]>", re.I), r"\1"),
            (re.compile(r"<\/?p[^>]*>", re.I), r"\n"),
            (re.compile(r" \w+=\"\"", re.I), r""),
            (re.compile(r"&quot;", re.I), r""),
            (re.compile(r"<o:smarttagtype[^>]*>(.*?)<\/o:smarttagtype>", re.I), r"\1 "),
            (re.compile(r"<st1:place[^>]*>(.*?)<\/st1:place>", re.I), r"\1 "),
            (re.compile(r"<st1:city[^>]*>(.*?)<\/st1:city>", re.I), r"\1 "),
            (re.compile(r"<st1:country-region[^>]*>(.*?)<\/st1:country-region>", re.I), r"\1 "),
            (re.compile(r"<o:p[^>]*>(.*?)<\/o:p>", re.I), r"\1 "),
            
            (re.compile(r"<\/?span[^>]*>", re.I), r""),
            
            (re.compile(r"<br[^>]*>", re.I), r"\n"),
            (re.compile(r"<a [^>]*href=\"([^\"]+)\"[^>]*>(.*?)<\/a>", re.I), r"\2 [\1]"),
            
            (re.compile(r"( \w+=\"(.+:.+;)?\")*", re.I), r''),#attr
            (re.compile(r" \w+=\"(.+)\"", re.I), r""),
            
            (re.compile(r"<b[^>]*>(.*?)<\/b>", re.I), r"\1"),
            (re.compile(r"<strong[^>]*>(.*?)<\/strong>", re.I), r"\1"),
            (re.compile(r"<em[^>]*>(.*?)<\/em>", re.I), r"\1"),
            (re.compile(r"<i[^>]*>(.*?)<\/i>", re.I), r"\1"),
            (re.compile(r"<div[^>.]*>(.*?)<\/div>", re.I), r"\1"),
            
            (re.compile(r"<tbody[^>.]*>(.*?)<\/tbody>", re.I), r"\1"),
            (re.compile(r"<thead[^>.]*>(.*?)<\/thead>", re.I), r"\1"),
            (re.compile(r"<table[^>.]*>(.*?)<\/table>", re.I), r"\1"),
            #(re.compile(r"<th[^>]*>(.*?)<\/th>", re.I), r"\1"),
            #(re.compile(r"<tr[^>]*>(.*?)<\/tr>", re.I), r"\1"),
            #(re.compile(r"<td[^>]*>(.*?)<\/td>", re.I), r"\1"),
            (re.compile(r"<\/?t.[^>]*[ ]?>", re.I), r""),
            
            (re.compile(r"\n([ ]+)\n"), r"\n\n"),
            (re.compile(r"\n[ ]\n"), r"\n\n"),
            (re.compile(r"\n{3,}"), r"\n\n"),
            (re.compile(r"[ ]{2,}"), r" "),
            (re.compile(r"&[^&;]+;"), r""),            
            (re.compile(r"<\/?.+[^>]*[ ]?>", re.I), r""),
            ]
            
def get_text(src):
    for p,r in replacer:
        src = p.sub(r, src)
    return src
            
if __name__ == '__main__':
    src = r'<meta name="abc">    <!--[if gt 8] abcdef --><br/><b>abcdef</b>'
    src += r'<span style="">1.<span style="font-family: &quot;Times New Roman&quot;; font-style: normal; font-variant: normal; font-weight: normal; font-size: 7pt; line-height: normal; font-size-adjust: none; font-stretch: normal; -x-system-font: none;"></span></span>'
        
    if len(sys.argv)>1:
        f = open(sys.argv[1])
        src = f.read()
        f.close()
        
    src = get_text(src)
        
    if len(sys.argv)>1:
        f = open(sys.argv[2], 'w')
        f.write(src)
        f.close()
    else:
        print src