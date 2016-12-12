import webbrowser, time
with open('url_list.txt', 'r') as url_file:
    urls = [line.strip() for line in url_file]
webbrowser.open(urls[0])
time.sleep(4)
for url in urls[1:]:
    webbrowser.open_new_tab(url)