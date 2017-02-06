#!/bin/env python3

from aiohttp import web
import os, sys, getopt, mimetypes

async def handle(request):
    filename = '.' + str(request.rel_url)
    print('Handling: ' + filename)
    if filename == './favicon.ico':
        return web.Response()
    if os.path.isdir(filename):
        return web.Response(body=get_directory_listing(filename).encode(), headers={
            'Content-Type': 'text/html'
        })
    mime = mimetypes.guess_type(filename)
    filetype = mime[0]
    if 'text' in filetype:
        return web.Response(body=open(filename).read().encode(), headers={
            'Content-Type': filetype,
            "Content-Disposition": "inline"
        })
    else:
        resp = web.StreamResponse(headers={
            'Content-Type': filetype,
            'Content-Length': str(os.path.getsize(filename)),
            'Content-Disposition': 'attachment'
        })
        await resp.prepare(request)
        resp.write(open(filename, "rb").read())
        return resp


def human_readable_size(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def get_directory_listing(dirname):
    body = """\
<!DOCTYPE html>
<html>
<title>
   Shared
</title>
<h1>
   Directory listing {}
</h1>
<hr>
<table>
    <th align=left>
        Name
    </th>
    <th style="padding-left: 20pt;">
        Type
    </th>
    <th style="padding-left: 20pt;">
        Size
    </th>""".format(dirname.replace('.', ''))
    for filename in os.listdir(dirname):
        fullpath = dirname  + '/' + filename
        if os.path.isdir(fullpath):
            file_type = 'Dir'
        else:
            file_type = 'File'
        if dirname != './':
            filename = '/' + filename
        dir = dirname.replace('./', '')
        body += """
    <tr>
        <td>
            <a href={}>{}</a>
        </td>
        <td style="padding-left: 20pt;">
            {}
        </td>
        <td style="padding-left: 20pt;">
            {}
        </td>
    </tr>""".format(dir + filename, dir + filename, file_type, human_readable_size(os.path.getsize(fullpath)))
    body += """
<table>
<hr>
</html>"""
    return body


def main(argv):
    port = None
    help = 'server.py -p|--port <port>'
    try:
        opts, args = getopt.getopt(argv, "hp:", ["help", "port="])
    except getopt.GetoptError:
        print(help)
        sys.exit(1)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(help)
            sys.exit()
        elif opt in ('-p', '--port'):
            port = int(arg)
    app = web.Application()
    app.router.add_get('/{tail:.*}', handle)
    web.run_app(app, port=port)


if __name__ == '__main__':
    main(sys.argv[1:])
