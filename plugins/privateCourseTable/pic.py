from io import BytesIO

import weasyprint as wsp


def toImage(htmlSource: str):
    html = wsp.HTML(string=htmlSource)
    css = wsp.CSS(string='''
@page {
    size: 1500px 910px;
    margin: 0 0 0 0;
    border: 50px 0 0 0;
    background: #fff;
}
.table_border{
    width:100%;border:0;border-collapse:collapse;border-spacing:0px;
}
.table_border tr {
    background-color: #fff;
}
.table_border tr:hover{
    background-color: #effff0;
}
.table_border td {
    border:1px solid #9F7E42 ;height:30px;text-align:center;
}
.table_border th {
    border:1px solid #9F7E42 ;height:30px; background-color:#EFECC5; font-weight:bold;text-align:center;
}
.form-style{
    background: #fff; padding:15px; border: 1px solid #ccc; font-size: 14px; box-sizing: border-box; width: 100%;
}
.frame-table{background: #fff; margin-bottom: 10px; width: 100%; margin-top: 10px; float: left; }
''')
    f = BytesIO()
    # imgpath = Path(r'F:\python\swjtu-jwc')
    f.write(html.write_png(stylesheets=[css]))
    # png = Image.open(f)
    # png.load()
    # background = Image.new("RGB", png.size, (255, 255, 255))
    # background.paste(png) # 3 is the alpha channel
    # background.save(f, 'JPEG', quality=90)
    # jpg = Image.open(f).resize((1500,900), Image.ANTIALIAS)
    # jpg.save(f, 'JPEG', quality = 80)
    return f
